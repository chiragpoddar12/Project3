To Run the application
*Expecting that python and Flask are already installed in the system
if not kindly follow the link: http://flask.pocoo.org/docs/0.12/installation/

1) Install required sqlAlchemy
    pip install sqlalchemy
2) To get the google login to be working:
    a) login to console.developer.google.com account
    b) create a project and give a suitable name
    c) create a client ID for the project
    d) provide this client ID in the file app.py at line 26 as a value for 'data-clientid'
    e) Add 127.0.0.1:27016 to 'Authorized JavaScript origins'
    f) Add '127.0.0.1:27016/gconnect' and '127.0.0.1:27016/login' to 'Authorized redirect URIs'
    g) download the json for the project and save in the same directory as of app.py
3) You can run Catalog_items.py to upload random data for your DB
4) Run the app.py file
5) The application should be running at 127.0.0.1:27016

