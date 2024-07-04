from threading import Thread
from traker_api import start_traker_api

if __name__ == '__main__':
    traker_api_thread = Thread(target=start_traker_api)

    traker_api_thread.start()

    traker_api_thread.join()

