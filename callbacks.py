from datetime import datetime
from telegram.ext import run_async
from heroku_helper import HerokuHelper
from io import BytesIO
from config import Config
from telegram import ParseMode
from telegram.error import BadRequest
from telegram.utils.helpers import escape_markdown
import requests
import math
import heroku3
from telegram.utils.helpers import mention_html

help_string = """<b>Available commands:</b>
- /start: for start message.
- /help: for get this message.
- /admins: get user ID's list of who have power over me.
- /restart: to restart @MissStella_bot.
- /dynos: to check Stella's dyno usage.
- /log: to get latest console log in .txt
- /about: to get info about me.

Join channel: @spookyanii
"""

non_admin = "<code>You are not allowed to use this command.\nDo</code> /help <code>for get more commands.\nJoin channel:</code> @spookyanii"
meanii_start = "@MissStella_bot's <code>Control center devloped & hosted by</code> @meanii"

@run_async
def startHandler(update,context):
    bot = context.bot
    message = update.effective_message
    user_id = message.from_user.id
    first_name = update.message.from_user.first_name
    message.reply_text(f"Hey *{first_name}*, I'm *Stella's Control Center bot* :)\n"
                       "I manage Stella's heroku app.\n\n"
                       "/admins: Get USER IDs list of who have power over me.\n\n"
                       "Admins are devided into two parts:\n"
                       "1: *Sudo Users* and\n"
                       "2: *Support Users.*\n\n"
                       "Sudo users have full power over me and Support users can do almost everything except using some sudo and owner only commands like /restart.\n",
                       parse_mode=ParseMode.MARKDOWN)
    if int(user_id) in Config.SUDO_USERS:
        user_status = "Sudo user"
    elif int(user_id) in Config.SUPPORT_USERS:
        user_status = "Support user"
    else:
        user_status = "Normal user"
    bot.send_message(user_id,
                     f"Your are my *{user_status}*.\n"
                     "- /help: for more commands.\n"
                     "- /about: to know more about *Stella's Control Center bot*.",
                     parse_mode=ParseMode.MARKDOWN)
        
    
@run_async
def logHandler(update,context):
    sudo = list(Config.SUDO_USERS) + list(Config.SUPPORT_USERS) 
    message = update.effective_message
    user_id = message.from_user.id
    if int(user_id) in sudo:
        herokuHelper = HerokuHelper(Config.HEROKU_APP_NAME,Config.HEROKU_API_KEY)
        log = herokuHelper.getLog()
        if len(log) > Config.TG_CHARACTER_LIMIT:
            file = BytesIO(bytes(log,"utf-8"))
            file.name = "log.txt"
            update.message.reply_document(file)
        else:
            update.message.reply_text(log)
    else:
        message.reply_text(non_admin,parse_mode=ParseMode.HTML)

@run_async
def adminsHandler(update,context):
    bot = context.bot
    message = update.effective_message
    text1 = "My sudo users are:"
    text2 = "My support users are:"
    for user_id in Config.SUDO_USERS:
        try:
            user = bot.get_chat(user_id)
            name = "[{}](tg://user?id={})".format(
                user.first_name + (user.last_name or ""), user.id)
            if user.username:
                name = escape_markdown("@" + user.username)
            text1 += "\n - `{}`".format(name)
        except BadRequest as excp:
            if excp.message == 'Chat not found':
                text1 += "\n - ({}) - not found".format(user_id)
    for user_id in Config.SUPPORT_USERS:
        try:
            user = bot.get_chat(user_id)
            name = "[{}](tg://user?id={})".format(
                user.first_name + (user.last_name or ""), user.id)
            if user.username:   
                name = escape_markdown("@" + user.username)
            text2 += "\n - `{}`".format(name)
        except BadRequest as excp:
            if excp.message == 'Chat not found':
                text2 += "\n - ({}) - not found".format(user_id)
    message.reply_text(text1 + "\n" + text2 + "\n",
                       parse_mode=ParseMode.MARKDOWN)

@run_async
def restartHandler(update,context):
    bot = context.bot
    sudo = Config.SUDO_USERS 
    message = update.effective_message
    user = update.effective_user
    user_id = message.from_user.id
    datetime_fmt = "%Y-%m-%d // %H:%M"
    current_time = datetime.utcnow().strftime(datetime_fmt)
    if int(user_id) in sudo:
        herokuHelper = HerokuHelper(Config.HEROKU_APP_NAME,Config.HEROKU_API_KEY)
        herokuHelper.restart()
        update.message.reply_text("Restarted.")
        if Config.LOGS:
            bot.send_message(Config.LOGS,
                "<b>[Restarted]</b>\n\n"
                f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
                f"<b>Event Stamp:</b> <code>{current_time}</code>",
                 parse_mode=ParseMode.HTML
            )
    else:
        message.reply_text(non_admin,parse_mode=ParseMode.HTML)

    
@run_async
def dynosHandler(update, context):
    sudo = list(Config.SUDO_USERS) + list(Config.SUPPORT_USERS) 
    message = update.effective_message
    user_id = message.from_user.id
    if int(user_id) in sudo:
        Heroku = heroku3.from_key(Config.HEROKU_API_KEY)
        heroku_api = "https://api.heroku.com"
        HEROKU_APP_NAME = Config.HEROKU_APP_NAME
        HEROKU_API_KEY = Config.HEROKU_API_KEY
        useragent = ('Mozilla/5.0 (Linux; Android 10; SM-G975F) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/80.0.3987.149 Mobile Safari/537.36'
                    )
        u_id = Heroku.account().id
        headers = {
        'User-Agent': useragent,
        'Authorization': f'Bearer {HEROKU_API_KEY}',
        'Accept': 'application/vnd.heroku+json; version=3.account-quotas',
        }
        path = "/accounts/" + u_id + "/actions/get-quota"
        r = requests.get(heroku_api + path, headers=headers)
        if r.status_code != 200:
            return message.reply_text("`Error: something bad happened`\n\n"
                                f">.`{r.reason}`\n")
        result = r.json()
        quota = result['account_quota']
        quota_used = result['quota_used']
        
        remaining_quota = quota - quota_used
        total_quote_min = quota / 60
        total_hours = math.floor(total_quote_min / 60)
        percentage = math.floor(remaining_quota / quota * 100)
        minutes_remaining = remaining_quota / 60
        hours = math.floor(minutes_remaining / 60)
        minutes = math.floor(minutes_remaining % 60)
        
        App = result['apps']
        try:
            App[0]['quota_used']
        except IndexError:
            AppQuotaUsed = 0
            AppPercentage = 0
        else:
            AppQuotaUsed = App[0]['quota_used'] / 60
            AppPercentage = math.floor(App[0]['quota_used'] * 100 / quota)
        AppHours = math.floor(AppQuotaUsed / 60)
        AppMinutes = math.floor(AppQuotaUsed % 60)
        
        return message.reply_text("*Stella's Dyno Usage*:\n"
                            f"*Dyno usage for {HEROKU_APP_NAME}*:\n"
                            f"- _{AppHours}h {AppMinutes}m | {AppPercentage}% _\n"
                            "*Dyno hours quota remaining this month*:\n"
                            f"- _{hours}h {minutes}m |  {percentage}%_\n"
                            f"*Total account's dynos(hr)* is `{total_hours}`*h*",
                            parse_mode=ParseMode.MARKDOWN)
    else:
        message.reply_text(non_admin,parse_mode=ParseMode.HTML)

@run_async
def helpHandler(update,context):
    message = update.effective_message
    message.reply_text(help_string,parse_mode=ParseMode.HTML)

@run_async
def aboutHandler(update,context):
    message = update.effective_message
    message.reply_text("This bot is developed & hosted by @meanii.\n"
                       "and this bot is licensed under the [GNU General Public License v3.0.](https://github.com/anilchauhanxda/StellaControlCenter/blob/master/LICENSE)\n"
                       "You can fork from [here](https://github.com/anilchauhanxda/StellaControlCenter)\n"
                       "Join his broadcast channel @spookyanii for get more updates.",
                       parse_mode=ParseMode.MARKDOWN,
                       disable_web_page_preview=True)
