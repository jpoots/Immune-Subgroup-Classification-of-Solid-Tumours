from app import create_app
from app import PORT
import os

"""
instatiates an app and starts it running on the appropriate port
"""
app = create_app()


debug = True if os.getenv("DEBUG") == "True" else False
if __name__ == "__main__":
    app.run(port=PORT, debug=debug)
