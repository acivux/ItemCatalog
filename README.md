# WineCave
WineCave helps you track your wine tasting journey. Add and rate your own wine selection or that of the other users of the site.

## Requirements
- Python 2.7.6 or later
- This has not been tested on any Apple devices

## Download
- Download the files from https://github.com/acivux/ItemCatalog
- Copy all the project files into the same folder.

## Setup
### Your user
To access all the features of the site, you will need to set up user account. For convenience, a file called `testing_user_sample.py` has been provided. Fill the required fields and rename the file to `testing_user_sample.py`
This file will be called in by `populate_db.py`, explained below.

### Database
`populate_db.py` will create the database and set it up with test data.
Run it by executing `python populate_db.py`. If successful, a database file called catalog.db will be created in the root folder.

### Application
The application is accessed from
`http://localhost:5000`

Anything else will prevent the 3rd party authentication from succeeding.

### 3rd Party Authentication
WinCave uses Google and Facebook for user authentication. The app registration data can be found in auth_api as JSON files.  