Deploying Locally
================

This page includes instructions on how to deploy ChiGame locally.

Initial Setup
-------------

Assuming you've cloned the repository, perform the following steps from inside
the repository's root. Please note that these steps only have to be performed
once.

1. Create a virtual environment and install dependencies.
   
       python3 -m venv venv
       source venv/bin/activate
       pip3 install pip --upgrade
       pip3 install wheel
       pip3 install -r requirements.txt

2. Setup the pre-commit hooks:

       export PYTHONPATH=$(pwd)/src:$PYTHONPATH

3. Create an empty database:

       python3 scripts/manage.py migrate

   By default, a SQLite database called `db.sqlite3` will be created in the `src/` directory.

4. Create a superuser (make sure to replace CNETID with your CNetID):

       python3 manage.py createsuperuser --email admin@example.com

   You will prompted for a password (you can use any password you want)


Running the test environment
----------------------------

You will need to follow these steps each time you want to run
the test environment.

1. Make sure the virtual environment has been activated. If you
   do not see `(venv)` in your shell prompt, make sure to run
   the following from the root of the repository:

       source venv/bin/activate

2. Run the test server like this:

       python3 manage.py runserver

   Use the URL shown by that command to access the test server
   (typically `http://127.0.0.1:8000/`). 

3. If you'd like to create a regular user account, use the "Sign Up"
   page on the test server. While creating new accounts technically
   requires e-mail verification, the test server does not send out
   a verification e-mail; instead, it will print the e-mail 
   verification message to the terminal. Simply follow the URL in
   that message to verify the user account.

