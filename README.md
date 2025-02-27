# Abstract
This project aims to be an easily extensible RESTful API for creating and managing
competitions which use [ELO](https://en.wikipedia.org/wiki/Elo_rating_system) leaderboards. Examples of use cases include a leaderboard for an office environment,
classroom or hobby leagues, particularly those in which matches schedules are irregular or an elo rating system is desired.

Current implementations of such a software come with limitations such as:
- State not saved between browser instances
- Premium pricing models

The source code can be found at https://github.com/NasserMalibari/nas_leaderboard 

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
![](/assests/swagger_docs_preview.png)


## Database
Django uses an ORM (Object Relation Mapper) however the following ER diagram captures the essential relationships in the database.
![](/assests/ER_diagram.png)

## Testing
All views/endpoints have a series of unit tests which can be found inside the repository at
/backend/api/tests.py
<!-- A series of unit tests can be found in  -->


# Installation and Setup


### 1. Clone the Repository Clone the repo: 
```sh
git clone git@github.com:NasserMalibari/nas_leaderboard.git
```

### 2. Create a .env file

Create a `.env` file in the `backend/` directory and populate it with
```
DJANGO_SECRET_KEY='YOUR_KEY'
```
replace 'YOUR_KEY' with a secret key of your choice.


### 3. Install the requirements

### 3. a)  (Optional)
\# Optionally use virtual environment
```sh
python -m venv env
source env/bin/activate
```

### 3. b  
```sh
pip install -r requirements.txt
```

### 4. Run the backend
```sh
cd backend
python manage.py runserver
```



## Example workflow via the docs

The swagger docs provide a convenient frontend for making requests. The docs
can be visited at `http://127.0.0.1:8000/api/docs/` .


The first step is to register a user under `/api/user/register/`, then generating a token for that user under `/api/token` .

Once you generate the **access** token, copy it and past it in the top right 'Authorize' button. You will now have access for all the endpoints
for the user you logged in with. You may of course repeat this process with as many users as desired.

Alternatively you can use tools like [Postman](https://www.postman.com/) or [curl](https://curl.se/).


# Future Extensions

## Updates To the Participant Model
Currently to add a participant to a competition, they must be a user. Changing this such
that participants are not required to be users, (but can connect their account later) is
the current priority.

## Competition Settings
- Let competition owners decide the 'K-factor' for elo settings,
- Change the type of leaderboard from an 'elo' to a classic competition
where wins give you competition points. 


## Modern Frontend
- Develop into a full-stack app with a modern frontend.


