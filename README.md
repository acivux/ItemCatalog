# WineCave
WineCave helps you track your wine tasting journey. Add and rate your own wine selection, or, that of the other users of the site.

## Download
- Download the files from https://github.com/acivux/ItemCatalog
- Copy all the project files into the same folder.


## Application set up
### Setting up your user
To access all the features of the site, you will need to set up user account. For convenience, a file called `testing_user_sample.py` has been provided. Fill the required fields and rename the file to `testing_user_sample.py`
This file will be called in by `populate_db.py`, explained below.

### Database setup
`populate_db.py` will create the database and set it up with test data.
Run it by executing `python populate_db.py`. If successful, a database file called catalog.db will be created in the root folder.





