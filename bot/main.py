from threading import Thread
from bot import start_bot
from api import start_api

if __name__ == '__main__':
    bot_thread = Thread(target=start_bot)
    api_thread = Thread(target=start_api)

    bot_thread.start()
    api_thread.start()

    bot_thread.join()
    api_thread.join()

