import time
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
import json


def print_date_time():
    print(time.strftime("Running cleanup at: %A, %d. %B %Y %I:%M:%S %p"))


def start_scheduler(config):
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=print_date_time, trigger="interval", seconds=60)
    scheduler.start()

    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())
