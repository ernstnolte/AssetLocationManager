# Location Storage

## Prerequisites
- python 3.11.x
- pip

## Initial Setup
After cloning this repository to your machine, you will have to configure the following

### 1. Python Virtual Environment
On Windows:

    > py -m venv venv
    > venv\Scripts\activate

Ensure that the (venv) tag appears in your terminal, then proceed to continue to dependency installation.

### 2. Dependencies
Inside the virtual environment:

    > pip install --upgrade pip
    > pip install -r requirements.txt

This will install the required version of Django, and any other dependencies in the *requirements.txt* file.

### 3. SQLite Database and Models

To create the database and database objects, run the following:
    
    > python manage.py makemigrations
    > python manage.py migrate

### 4. Administrative Access to Django Server

You will need an administrative user for development and testing (handy for test data management)

    > python manage.py createsuperuser

Follow the promts in your terminal to configure your admin credentials

## Running the Application
1. Start the development server:

        > python manage.py runserver

2. Your application will now be running at http://localhost:8000/

        ## Home Page
        http://localhost:8000/

        ## Django Admin Panel
        http://localhost:8000/admin/
