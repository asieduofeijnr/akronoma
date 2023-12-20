from selenium import webdriver
import pandas as pd
from selenium.webdriver.common.by import By
import time


def initialize_website(website_url):
    driver = webdriver.Chrome()

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
