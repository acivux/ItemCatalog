from database import User

# This is the testing user.
# email (Required) - The user email needs to match a valid Google or
#    Facebook account.
# name (Required) - The name of the user
# admin - The admin attribute can be set to False if this user should
#    not be an admin.
TESTING_USER = User(name="",
                    email="",
                    admin=True)
