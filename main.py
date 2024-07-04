from threading import Thread
from bot.bot import start_bot
from bot.api import start_api
from traker.traker_api import start_traker_api

if __name__ == '__main__':
    bot_thread = Thread(target=start_bot)
    api_thread = Thread(target=start_api)
    traker_api_thread = Thread(target=start_traker_api)

    bot_thread.start()
    api_thread.start()
    traker_api_thread.start()

    bot_thread.join()
    api_thread.join()
    traker_api_thread.join()