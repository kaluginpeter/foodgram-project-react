# praktikum_new_diplom
![GitHub Action Workflow](https://github.com/kaluginpeter/foodgram-project-react/actions/workflows/main.yml/badge.svg)
## Что нужно сделать
### About
Foodgram - Social service for people who loves foods and recipes(who not loves eat and look at beautiful food?).
You can register in app, create recipes, pin a photo, add ingredients and more.
Also you can see recipes of another people, add her to favorite, subcribe on users and make shopping list. Have a fun!
### Stack Technologies
Python/Django/Django Rest/NodeJs/Docker/Djoser/PostgresSql/GitHub Actions
# for admin
username: admin
password: admin
### Getting Started
1) Pull repo from github
```
git pull git@github.com:kaluginpeter/foodgram-project-react.git
```
2) Add variables in .env file
3) Launch Dokcer Compose file
```
cd infra
docker compose up
```
4) Done!
### How to add .env file

POSTGRES_USER=name_user_for_postgres (only for production)

POSTGRES_PASSWORD=password_for_postgres (only for production)

POSTGRES_DB=name_of_db (only for production)

DB_HOST=name_of_postgres_db (for docker network connection) (only for production)

DB_PORT=5432 for connecting Backend Container

SECRET_KEY=project_secret_key

DEBUG=False boolean (Set to False for production otherwise True)

POSTGRES_DATABASE=True boolean (Set to False for using SQLite)

HOSTS_ALLOWED='localhost' (write a allowed hosts SEPARATED BY SINGE WHITESPACE)

CSRF_TRUSTED_ORIGINS=https://example.org (adding to protect csrf attacks) NEEDED

### Basical endpoints

```
https://foodgram-peka.zapto.org/recipes/
```

Get list of all recipes on service

```
https://foodgram-peka.zapto.org/subscriptions/
```

Get list of all users that you subscribed

```
https://foodgram-peka.zapto.org/recipes/create
```

Create recipe

```
https://foodgram-peka.zapto.org/favorites
```

Get list of all favorite recipes that you pin

```
https://foodgram-peka.zapto.org/cart
```

Get list of all recipes that you added in shopping cart

```
https://foodgram-peka.zapto.org/api/recipes/download_shopping_cart/
```

Download shopping list of all ingredients that included in recipes in shopping cart


### Author
@kaluginpeter

```yaml
repo_owner: @kaluginpeter
foodgram_domain: https://foodgram-peka.zapto.org/
dockerhub_username: @kaluginpeter
```