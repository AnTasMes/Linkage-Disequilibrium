import sys
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.remote_connection import LOGGER

import logging

OPTIONS = webdriver.EdgeOptions()

# OPTIONS.add_argument("--headless")
# OPTIONS.add_argument("--disable-crash-reporter")
# OPTIONS.add_argument("--disable-in-process-stack-traces")
# OPTIONS.add_argument("--disable-logging")
# OPTIONS.add_argument("--disable-dev-shm-usage")
# OPTIONS.add_argument("--log-level=3")
# OPTIONS.add_argument("--output=/dev/null")

def start(url: str, options: list = None, load_time: int = 1):

    load_options(options)

    try:
        LOGGER.setLevel(logging.WARNING)
        driver = webdriver.Edge(options=OPTIONS)
        driver.get(url)
        time.sleep(load_time)
    except Exception as e:
        print(e)
        sys.exit()
    return driver

def load_options(options: list):
    for option in options:
        OPTIONS.add_argument(option)