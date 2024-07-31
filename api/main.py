from app import create_app

"""
instatiates an app and starts it running on the appropriate port
"""

app = create_app()

if __name__ == "__main__":
    app.run(port=3000, debug=True)
