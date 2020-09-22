import os

class Config:
    BOT_TOKEN = os.environ.get("BOT_TOKEN","1275856659:AAEsSfgvNQL4yS7M9p1yu7zqK8nCF_xwkZk")
    HEROKU_API_KEY = os.environ.get("HEROKU_API_KEY","4f39e784-aed1-4ddc-a4a1-01ebe05cae03")
    LOGS = os.environ.get("LOGS","")
    SUDO_USERS = [int(user) for user in os.environ.get("SUDO_USERS").split(",")]
    SUPPORT_USERS = [int(user) for user in os.environ.get("SUPPORT_USERS").split(",")]
    TG_CHARACTER_LIMIT = 4000 
    HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME","hinatatest")
