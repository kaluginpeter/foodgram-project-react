from http import HTTPStatus
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from djoser import views as djoser_views

from apis.pagination import CustomPagination
from apis.serializers import (
    UserRetrieveListSerializer,
    CustomUserCreateSerializer,
    FollowingSerializer
)
from users.models import Follow

User = get_user_model()


class CustomRetrieveListUserViewSet(djoser_views.UserViewSet):
    lookup_field = 'id'
    pagination_class = CustomPagination

    def get_queryset(self):
        if (self.request.path.endswith('subscriptions/')
                or self.request.path.endswith('subscribe/')):
            return Follow.objects.all()
        return User.objects.all()

    def get_permissions(self):
        if self.action in {'list', 'retrieve'}:
            return (AllowAny(),)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in {'list', 'retrieve', 'me'}:
            return UserRetrieveListSerializer
        elif self.request.path.endswith('set_password/'):
            return super().get_serializer_class()
        return CustomUserCreateSerializer

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        serializer_class=FollowingSerializer,
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(subscribing__user=self.request.user)
        queryset = self.paginate_queryset(queryset)
        serializer = FollowingSerializer(
            queryset, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        lookup_field='id',
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
        serializer_class=FollowingSerializer
    )
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=self.kwargs.get('id'))
        if request.method == 'POST':
            serializer = FollowingSerializer(
                author, data=request.data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=user, author=author)
            return Response(serializer.data, status=HTTPStatus.CREATED)

        elif request.method == 'DELETE':
            follow_instance = Follow.objects.filter(user=user, author=author)
            if not follow_instance.exists():
                return Response(
                    data={'errors': 'Not existing subscription'},
                    status=HTTPStatus.BAD_REQUEST
                )
            follow_instance = get_object_or_404(
                Follow, user=user, author=author
            )
            follow_instance.delete()
            return Response(status=HTTPStatus.NO_CONTENT)
