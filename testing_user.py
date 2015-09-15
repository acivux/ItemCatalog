from database import User

# This is the testing user.
# The user email needs to match a valid Google or facebook account.
# The id needs to be 1
TESTING_USER = User(id=1,
                    name="Jannie van Niekerk",
                    email="acivux@gmail.com",
                    admin=True)
