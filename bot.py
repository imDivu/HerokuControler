from config import Config
import logging

from telegram.ext import Updater, CommandHandler
from callbacks import startHandler, logHandler, restartHandler, adminsHandler, helpHandler, dynosHandler, aboutHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

LOGGER = logging.getLogger(__name__)



def main():
    LOGGER.info("Starting Bot")
    updater = Updater(Config.BOT_TOKEN,use_context=True)
    dispatcher = updater.dispatcher
    start_handler = CommandHandler("start",startHandler)
    help_handler = CommandHandler("help",helpHandler)
    admins_handler = CommandHandler("admins",adminsHandler)
    log_handler = CommandHandler("log",logHandler)
    dynos_handler = CommandHandler("dynos",dynosHandler)
    restart_handler = CommandHandler("restart",restartHandler)
    about_handler = CommandHandler("about",aboutHandler)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(admins_handler)
    dispatcher.add_handler(log_handler)
    dispatcher.add_handler(dynos_handler)
    dispatcher.add_handler(restart_handler)
    dispatcher.add_handler(about_handler)
    LOGGER.info("Starting Updater Thread.")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
