from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.remote_connection import LOGGER

import logging

from threading import Thread

import pandas as pd
import time
import sys
import os

import selenium_init as si

from settings import Settings, load_settings

SETTINGS_FILE = './settings.json'
SETTINGS = load_settings(SETTINGS_FILE)

STARTING_URL = SETTINGS.starting_url
INPUT_FILE = SETTINGS.input_file_path
OUTPUT_FILE = SETTINGS.output_file_path
NUMBER_OF_THREADS = SETTINGS.thread_count
OPTIONS = SETTINGS.options
POPULATION = SETTINGS.population

import datetime


def main():
    print('Starting the program...')
    
    start_time = datetime.datetime.now()

    # Prepare the dataframe
    df = prepare_dataframe(INPUT_FILE)

    # Validate the output file name and make sure it doesn't exist
    #OUTPUT_FILE = validate_file_name(OUTPUT_FILE)

    df = loop_through_dataframe_with_threads(df)

    # Retry all -1 values if prompted
    if Settings.do_end_checkup == 'true':
        print('Doing end checkup ....')
        df = loop_through_dataframe_with_threads(df)
        print('End checkup complete.')

    print("Exporting to Excel once again...")
    df.to_excel(OUTPUT_FILE)

    print("Exported.")

    end_time = datetime.datetime.now()

    print('Start time: ', start_time, ' | End time: ', end_time, ' | Lasted: ', end_time - start_time )

    print("Closing application...")
    sys.exit(0)

def validate_file_name(file_name: str) -> str:
    # Check if the file name ends with .xlsx
    file_name = attach_extension(file_name, '.xlsx')
    
    # Check if file exists
    counter = 1
    while os.path.exists(file_name):
        file_name = file_name.replace('.xlsx', '') + '_' + str(counter) + '.xlsx'
        counter += 1

    return file_name

def attach_extension(file_name: str, extension: str) -> str:
    if not file_name.endswith(extension):
        file_name += extension
    return file_name


def load_data(file_path: str) -> pd.DataFrame:
    df = pd.read_excel(file_path)
    return df

def prepare_dataframe(input_file: str) -> pd.DataFrame:
    print('Preparing the dataframe...')

    input_file = attach_extension(input_file, '.xlsx')
    
    # Load the data
    df = load_data(input_file)

    # Drop the first column
    df = df.set_index('rsid')

    # Set the index of the dataframe to the rsid column
    for index in df.index:
        df[index] = index

    # Set values of all columns to -1.0
    df[:] = -1.0

    print('Dataframe prepared.')
    return df

def load_first_section(rsid_1: str, rsid_2: str, driver):
     # Find the textbox with id = 'se_q'
    textbox = None
    counter = 0
    while textbox is None and counter < SETTINGS.page_load_seconds + 20:
        try:
            textbox = driver.find_element(By.ID,'se_q')
        except:
            counter += 1
            time.sleep(1)
        

    if textbox is None:
        print('Could not find the textbox for the rsid: ' + rsid_1)
        return -1

    try:
        textbox.send_keys(rsid_1)
        textbox.send_keys(Keys.RETURN)
    except:
        print('Could not send the keys for the rsid: ' + rsid_1)
        return -1
    


    # Find the link that contains the (Human Variant) text (Possible long wait)
    link = None
    counter = 0
    while link is None and counter < SETTINGS.page_load_seconds + 20:
        try:
            link = driver.find_element(By.XPATH, "//a[contains(text(), '(Human Variant)')]")
        except:
            counter += 1
            time.sleep(1)

    if link is None:
        print('Could not find the link for the rsid: ' + rsid_1)
        return -1


    try:
        link.click()
    except:
        print('Could not click the link for the rsid: ' + rsid_1)
        return -1



    # Find the link that contains the (HighLD) href
    link = None
    counter = 0
    while link is None and counter < SETTINGS.page_load_seconds + 20:
        try:
            link = driver.find_element(By.XPATH, "//a[contains(@href, 'HighLD')]")
        except:
            counter += 1
            time.sleep(1)

    if link is None:
        print('Could not find the link for the rsid: ' + rsid_1)
        return -1

    try:
        link.click()
    except:
        print('Could not click the link for the rsid: ' + rsid_1)
        return -1


def get_value(rsid_1: str, rsid_2: str, driver, skip: bool) -> float:

    if not skip:
        load_first_section(rsid_1, rsid_2, driver)
    
    # Find the textbox with id = 'variant'
    textbox = None 
    counter = 0
    while textbox is None and counter < SETTINGS.page_load_seconds + 20:
        try:
            textbox = driver.find_element(By.ID, 'variant')
        except:
            counter += 1
            time.sleep(1)

    if textbox is None:
        print('Could not find the textbox for the rsid: ' + rsid_1)
        return -1

    try:
        textbox.clear()
        textbox.send_keys(rsid_2)
        textbox.send_keys(Keys.RETURN)
    except:
        print('Could not send the keys for the rsid: ' + rsid_1)
        return -1
    

    # Find the r^2 value in the row with Description that contains 'Utah residents with Northern and... ' text
    r2_value = None
    counter = 0
    while r2_value is None and counter < SETTINGS.page_load_seconds + 25:
        try:
            # Table also has a column with the text 'Focus Variant' and 'Utah residents with Northern and... '
            # We need to find the row that has the text 'Utah residents with Northern and... '
            # and then find the r^2 value in the same row

            Focus_Variant = driver.find_element(By.XPATH, "//th[contains(text(), 'Focus Variant')]")

            table = Focus_Variant.find_element(By.XPATH, "./ancestor::table")

            # Find the row that has the text 'Utah residents with Northern and... '
            row = table.find_element(By.XPATH, f"//td[contains(text(), '{POPULATION}')]/ancestor::tr")

            # Find the r^2 value in the same row
            r2_value = row.find_element(By.XPATH, "./td[6]").text
        except:
            counter += 1
            time.sleep(1)
    
    if r2_value is None:
        print('Could not find the r^2 value for the rsid: ' + rsid_1)
        return -1

    print('The r^2 value for ' + rsid_1 + ' and ' + rsid_2 + ' is: ' + r2_value)

    return r2_value


def loop_through_dataframe_with_threads(df: pd.DataFrame) -> pd.DataFrame:
    print('Looping through the dataframe with ' + str(NUMBER_OF_THREADS) + ' threads...')

    # Create a list of threads
    threads = []
    drivers = []
    try:
        for i in range(NUMBER_OF_THREADS):
            LOGGER.setLevel(logging.WARNING)
            driver = si.start(STARTING_URL, OPTIONS, 5)
            drivers.append(driver)
            threads.append(Thread(target=loop_through_dataframe, args=(df, drivers[i], i)))
            threads[i].start()
    except:
        print('Thread creation failed.')
        sys.exit(1)
    

    # Wait for the threads to finish
    for i, thread in enumerate(threads):
        print('Waiting for thread number: ' + str(i) + ' to finish...')
        thread.join()
        print('Thread number: ' + str(i) + ' finished.')

    # Close the drivers
    for driver in drivers:
        driver.close()


    print('Looping through the dataframe with ' + str(NUMBER_OF_THREADS) + ' threads finished.')

    return df

def loop_through_dataframe(df: pd.DataFrame, driver, thread_number) -> pd.DataFrame:
    print('Looping through the dataframe with thread number: ' + str(thread_number) + '...')

    number_of_rows = len(df.index)
    print('Number of rows: ' + str(number_of_rows))

    # Calculate the start and end index for the thread
    start_index = int(thread_number * number_of_rows / NUMBER_OF_THREADS)
    end_index = int((thread_number + 1) * number_of_rows / NUMBER_OF_THREADS)

    # If the thread is the last thread, then set the end index to the last row
    if thread_number == NUMBER_OF_THREADS - 1:
        end_index = number_of_rows

    print('Thread number: ' + str(thread_number) + ' will loop from row: ' + str(start_index) + ' to row: ' + str(end_index))

    current_index = None
    last_index = None
    skip = False

    for index in df.index[start_index:end_index]:

        last_index = index

        for column in df.columns: 
            print(f"THREAD #{thread_number} -> Progress (may fluctuate): " + str(round((df.index.get_loc(index) + 1) / number_of_rows * 100, 2)) + " %")

            if df[index][column] != -1:
                print(f'THREAD #{thread_number} -> Skipping the column: ' + column + ' - VALUE ALREADY SET')
                continue

            if current_index == last_index and index != column:
                print(f'THREAD #{thread_number} -> Skipping the column: ' + column)
                skip = True
            else:
                if index != column:
                    skip = False
                    current_index = index

            if index == column:
                print(f'THREAD #{thread_number} -> The index and column are the same. Setting the value to 1.0')
                df[index][column] = 1.0
            else:
                print(f'THREAD #{thread_number} -> Getting the value for ' + index + ' and ' + column)
                df[index][column] = get_value(index, column, driver, skip)
            
            # Fail safe
            df.to_excel(OUTPUT_FILE)   
        
        print(f"THREAD #{thread_number} -> Progress: " + str(round((df.index.get_loc(index) + 1) / number_of_rows * 100, 2)) + " %" + " -> Finished row: " + index)
        


    print('Looping through the dataframe with thread number: ' + str(thread_number) + ' finished.')

    return df


# Initial page : https://www.ensembl.org/index.html
# TextBox : id = 'se_q' -> type = 'text' -> input = 'rsid'
# Next page: https://www.ensembl.org/Multi/Search/Results?q=<rsid_value>;site=ensembl_all
# Looking for <a> class = 'table_toplink' where the text has (Human Variant) in it
# After click, wait around 10 seconds for the next page to load
# Next page: https://www.ensembl.org/Homo_sapiens/Variation/Explore?r=2:174751073-174752073;v=rs74803262;vdb=variation;vf=195784804
# https://www.ensembl.org/Homo_sapiens/Variation/HighLD?db=core;r=2:174751073-174752073;v=rs74803262;vdb=variation;vf=195784804

if __name__ == '__main__':
    main()





