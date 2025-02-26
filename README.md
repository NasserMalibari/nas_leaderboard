# Abstract
This project aims to be an easily extensible RESTful API for creating and managing
competitions which use [ELO](https://en.wikipedia.org/wiki/Elo_rating_system) leaderboards. Examples of use cases include a leaderboard for an office environment,
classroom or hobby leagues, particularly those in which matches schedules are irregular or an elo rating system is desired.

Current implementations of such a software come with limitations such as:
- State not saved between browser instances
- Premium pricing models

# Design

## Technology
The backend is designed to be easily extensible by using [Django](https://www.djangoproject.com/[) and the 
[Django Rest Framework](https://www.django-rest-framework.org/). It is thus easily extensible in that it features:
- Web browsable API.
- Official support for PostgreSQL, MySQL, SQLite and a number of [others](https://docs.djangoproject.com/en/5.1/ref/databases/).
- Authentication policies including [Oauth2](https://www.django-rest-framework.org/api-guide/authentication/#django-oauth-toolkit).


## Routes
All views (API endpoints) have been fully documented using the popular [Swagger Docs](https://swagger.io/docs/).
Preview:

## Database
Django uses an ORM (Object Relation Mapper) however the following ER diagram captures the essential relationships in the database.
![](/assests/ER_diagram.png)

## Testing
All views/endpoints have a series of unit tests which can be found inside the repository at
/backend/api/tests.py
<!-- A series of unit tests can be found in  -->

# Extensions

## Updates To the Participant Model

## Competition Settings

## Modern Frontend






Hello World


**bold**
