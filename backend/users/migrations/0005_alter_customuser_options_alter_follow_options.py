# Generated by Django 5.0.4 on 2024-04-20 11:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_follow_author_alter_follow_user'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customuser',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='follow',
            options={'ordering': ['-id']},
        ),
    ]
