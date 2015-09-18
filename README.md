# WineCave
WineCave helps you track your wine tasting journey. Add and rate your own wine selection or that of the other users of the site.

## Requirements
- Python 2.7.6 or later
- This has not been tested on any Apple devices

## Download
- Download the files from https://github.com/acivux/ItemCatalog
- Copy all the project files into the same folder.

## Installation
The easiest way to get all the required Python packages installed is by using `pip`. On a Linux machine, please make sure to use a user with the appropriate rights.
### Flask
`pip install Flask`
### Flask-Restless
`pip install Flask-Restless`
### Flask-Uploads
`pip Flask-Uploads`

## Setup
### Your user
To access all the features of the site, you will need to set up user account. For convenience, a file called `testing_user_sample.py` has been provided. Fill the required fields and rename the file to `testing_user_sample.py`
This file will be called in by `populate_db.py`, explained below.

### Database
`populate_db.py` will create the database and set it up with test data.
Run it by executing `python populate_db.py`. If successful, a database file called catalog.db will be created in the root folder.

### Application
#### Vagrant
To run the application from inside Vagrant, change the host IP address to `0.0.0.0` inside `application.py`:
`app.run(host='0.0.0.0', port=5000)`

#### Non-Vagrant
To run the application from outside Vagrant, change the host IP address to `127.0.0.1` inside `application.py`:
`app.run(host='127.0.0.1', port=5000)`

The application is accessed from `http://localhost:5000` in the browser. Anything else will prevent the 3rd party authentication from succeeding.

### 3rd Party Authentication
WinCave uses Google and Facebook for user authentication. The app registration data can be found in auth_api as JSON files.  

### Administration
An admin user can manage the following wine type attributes:

 * Colors
 * Calories
 * Alcohol by Volume
 * Temperature
 * Glass types

To mark a user as an administrator, set the `admin` field in the user's database record to `True`. No UI has been implemented for this.
Normally the test user will be set as administrator when `populate_db.py` is executed. 

## API
A JSON API is implemented through Flask-Restless on the database level. Only GET requests are valid. Some additional features, like paging, is implemented.

Please read the Flask-Restless [documentation](https://flask-restless.readthedocs.org/en/latest/index.html) for further information. 

Endpoints available:

 * `winebrand`
 * `winetype`
 * `review`
 * `color`
 * `calories`
 * `abv`
 * `temperature`
 * `glass`
 
 For a complete paged listing, use the url `http://localhost:5000/api/<endpoint>`. To reach a specific item, use `http://localhost:5000/api/<endpoint>/<item_id>`
 
### Example
We will use the `color` endpoint as an example.

#### List all the colors 
Use the url `http://localhost:5000/api/color`. This will list the first page of results. To retrieve the second page, use the url `http://localhost:5000/api/color?page=2`

#### List all a specific color
To find the color with id=2: `http://localhost:5000/api/color/2`