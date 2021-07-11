import time
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
import json
import datetime
from application import app
from .models import Userimage

""" Schedule any random thing that doesn't require imports from app """


def print_date_time():

    print(time.strftime("Running cleanup at: %A, %d. %B %Y %I:%M:%S %p"))


def start_scheduler():
    scheduler = BackgroundScheduler()
    # scheduler.add_job(func=print_date_time, trigger="interval", seconds=120)

    scheduler.start()

    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())
