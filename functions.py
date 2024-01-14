from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from utilities import app_password
from utilities import app_email
from google.cloud import bigquery

import pandas as pd
import smtplib
import time
import os


def initialize_website(website_url):

    # Initialize the Chrome driver with options
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(
        ChromeDriverManager().install()), options=chrome_options)

    try:
        driver.get(website_url)
    except Exception as e:
        print(f"An error occurred: {str(e)}")

    return driver


def penetrate_site(website, driver):
    driver.get(website)
    driver_links = driver.find_elements(
        By.XPATH, '//div[@id="inner-left-col"]//a')
    raw_links = [items.get_attribute('href') for items in driver_links]
    return raw_links


def scrape_head_body(website, driver):
    tags = ['h1', 'p']
    driver.get(website)
    main_story = driver.find_element(
        By.XPATH, '//div[@class="article-left-col"]')
    header = main_story.find_element(By.XPATH, f'//{tags[0]}')
    body = main_story.find_element(By.XPATH, '//p[@id="article-123"]')
    return (header.text, body.text)


def email_sender(subject, body, recipient_email):
    sender_email = "adwintechnology@gmail.com"  # replace with your email
    sender_password = app_password  # replace with your password

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


def upload_to_bigquery(client, dataframe):
    job_config = bigquery.LoadJobConfig(
        schema=[
            bigquery.SchemaField("source", bigquery.enums.SqlTypeNames.STRING),
            bigquery.SchemaField(
                "category", bigquery.enums.SqlTypeNames.STRING),
            bigquery.SchemaField(
                "date_time", bigquery.enums.SqlTypeNames.STRING),
            bigquery.SchemaField("link", bigquery.enums.SqlTypeNames.STRING),
            bigquery.SchemaField("story", bigquery.enums.SqlTypeNames.STRING),
        ],
        skip_leading_rows=0,
        source_format=bigquery.SourceFormat.CSV,
    )

    job = client.load_table_from_dataframe(
        dataframe=dataframe,
        destination='akronoma.NewsScraping.All_news',
        location='US',
        job_config=job_config,
        job_id_prefix='job_load_df',
    )

    return job.result()
