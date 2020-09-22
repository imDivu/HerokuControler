import os

class Config:
    BOT_TOKEN = os.environ.get("BOT_TOKEN","")
    HEROKU_API_KEY = os.environ.get("HEROKU_API_KEY","")
    LOGS = os.environ.get("LOGS","")
    SUDO_USERS = [int(user) for user in os.environ.get("SUDO_USERS").split(",")]
    SUPPORT_USERS = [int(user) for user in os.environ.get("SUPPORT_USERS").split(",")]
    TG_CHARACTER_LIMIT = 4000 
    HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME","")
