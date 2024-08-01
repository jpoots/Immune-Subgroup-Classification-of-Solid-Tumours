from app import create_app
from app import PORT

"""
instatiates an app and starts it running on the appropriate port
"""
app = create_app()

if __name__ == "__main__":
    app.run(port=PORT, debug=True)
