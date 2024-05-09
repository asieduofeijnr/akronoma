from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from webdriver_manager.chrome import ChromeDriverManager
from email.mime.text import MIMEText

from google.cloud import bigquery


import smtplib
import time
import os


def initialize_website(website_url, max_retries=5, retry_delay=5):
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")

    attempt = 0
    while attempt < max_retries:
        print('Driver Initializing... please wait')
        try:
            driver = webdriver.Chrome(options=chrome_options, service=Service(
                ChromeDriverManager().install()))
            driver.get(website_url)
            return driver
        except Exception as e:
            attempt += 1
            print(f"Attempt {attempt}: An error occurred - {str(e)}")
            time.sleep(retry_delay)

    print("Failed to initialize the WebDriver after multiple attempts.")
    return None


def penetrate_site2(website, driver):
    driver.get(website)
    driver_links = driver.find_elements(
        By.XPATH, '//div[@id="inner-left-col"]//a')
    raw_links = [items.get_attribute('href') for items in driver_links]
    return raw_links


def penetrate_site(website, driver, retries=3):
    try:
        driver.set_page_load_timeout(30)  # Timeout in seconds
        driver.get(website)

        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, '//div[@id="inner-left-col"]//a'))
        )

        driver_links = driver.find_elements(
            By.XPATH, '//div[@id="inner-left-col"]//a')
        raw_links = [item.get_attribute('href') for item in driver_links]
        return raw_links

    except TimeoutException:
        if retries > 0:
            print(
                f"Timeout occurred for {website}. Retrying... ({retries} retries left)")
            return penetrate_site(website, driver, retries - 1)
        else:
            print(f"Failed to load {website} after several retries.")
            return []


def scrape_head_body(website, driver):
    tags = ['h1', 'p']
    try:
        driver.get(website)
        main_story = driver.find_element(
            By.XPATH, '//div[@class="article-left-col"]')
        header = main_story.find_element(By.XPATH, f'//{tags[0]}')
        body = main_story.find_element(By.XPATH, '//p[@id="article-123"]')
        return header.text, body.text
    except NoSuchElementException as e:
        print(f"Element not found: {e}")
        return None, None


def email_sender(subject, body, recipient_email):
    sender_email = "adwintechnology@gmail.com"  # replace with your email
    # replace with your password
    sender_password = os.getenv('GMAIL_ADWIN_PASSWORD')

    try:
        # Set up server
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server_ssl:
            # Log in to the server
            server_ssl.login(sender_email, sender_password)

            # Prepare email
            message = MIMEText(body, 'plain')
            message['From'] = sender_email
            message['To'] = recipient_email
            message['Subject'] = subject

            # Send email
            server_ssl.send_message(message)
            print("Email sent successfully!")

    except Exception as e:
        print(f'Something went wrong... {e}')


def google_client():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "akronomacloudserviceaccount.json"
    client = bigquery.Client()
    return client


def upload_to_bigquery(client, table_id, data):

    errors = client.insert_rows_json(table_id, data)  # Make an API request.
    if errors == []:
        print("New rows have been added.")
    else:
        print("Encountered errors while inserting rows: {}".format(errors))
