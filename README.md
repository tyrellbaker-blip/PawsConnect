# PawsConnect Project Setup Instructions

Welcome to the PawsConnect project! This document provides a comprehensive guide
to setting up your local development
environment.

## Prerequisites

Before you begin, ensure you have the following installed:

- ### Requirements File
- Install the requirements.txt file by running the following command:

```bash
pip install -r requirements.txt
```

- ## Python, pip, postgresql, and postgis

- Python 3.8 or higher
- pip (Python package manager)
- [PostgreSQL and PostGIS](https://postgresapp.com/downloads.html)

# Setting Up PostgreSQL for Django Projects

This guide provides step-by-step instructions for setting up PostgreSQL for your
Django projects on macOS and Windows.

## For macOS Users: Using Postgres.app

### Downloading and Installing Postgres.app

1. **Visit the Official Site**:
   Open [Postgres.app official website](http://postgresapp.com/).

2. **Download**: Click on "Download". If multiple versions are presented, choose
   the one that fits your requirements.

3. **Install**: Open the downloaded `.dmg` file and drag Postgres.app into your "
   Applications" folder.

### Configuring Postgres.app

1. **Launch**: Double-click Postgres.app from the "Applications" folder. If a
   security warning appears, right-click,
   select "Open", and confirm.

2. **Initialize**: On first launch, Postgres.app will automatically create a new
   server instance.

3. **Set PATH (Optional)**: For command-line tool access, add Postgres.app to your
   PATH via its preferences.

## For Windows Users: Using the Official PostgreSQL Installer

### Downloading and Installing PostgreSQL

1. **Download**: Go to
   the [PostgreSQL download page](https://www.postgresql.org/download/windows/)
   and click "Download
   the installer". Select the desired version and proceed with the download.

2. **Install**: Run the downloaded installer and follow the prompts to set your
   installation preferences, including the
   PostgreSQL superuser password and port number (default is 5432).

### Post-installation Steps

1. **Launch pgAdmin**: If installed, use pgAdmin from the Start Menu for graphical
   database management.

2. **Use SQL Shell**: Access the psql command-line tool via "SQL Shell (psql)" in
   the Start Menu or navigate to the bin
   directory of your PostgreSQL installation in the Command Prompt.

# Universals for database setup

### DO NOT LOSE USERNAME AND PASSWORD YOU SET DURING INSTALLATION

### Creating a Database

Use the PostgreSQL command-line interface (CLI) accessible from the terminal by
double-clicking the server in pgAdmin.

Once you've accessed the CLI, create a new database using the following command:

```bash
createdb pawsconnect
```

Once the database has been created, you're ready to work with it in django. To
make this functional, you need to go into your `settings.py` file and change
the DATABASES variable to the following:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'pawsconnect',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```


![PG.png](misc%2FPG.png)In the photo, I've labeled a couple things you'll want to be mindful of.

Then, once you've done that, you can run the following command to make sure
that your database has the things from the sqlite database:

```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

Once your database is set up, you should be able to run the server as you
normally would. If you have any questions, reach out to me.

# IMPORTANT NOTE: DO NOT add dependencies to the application without notifying and commiserating with both front and backend to ensure that your dependency aligns with project goals. 