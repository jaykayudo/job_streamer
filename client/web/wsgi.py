from client.web.app import app
from conf.settings import Settings

SETTINGS = Settings()

if __name__ == "__main__":
    app.run(debug=SETTINGS.DEBUG)