from functions import *


def initialize_scraping(website):
    """
    Initializes the browser and navigates to the website.
    """
    start_time = time.time()
    driver = initialize_website_firefox(website)
    if driver:
        elapsed_time = time.time() - start_time
        print(f"Elapsed time: {elapsed_time} seconds")
        print('Done with initialization')
        return driver
    else:
        return None


def extract_mother_links(driver, website):
    """
    Extracts category links from the main navigation.
    """
    mother_extracts = []
    nav_elements = driver.find_elements(
        By.XPATH, '//ul[@id="mainnavinner"]//a')

    for item in nav_elements:
        data = {
            "Data Source": website,
            "Category": (item.text, item.get_attribute("href")),
            "News": []
        }
        mother_extracts.append(data)

    mother_extracts = mother_extracts[:5]  # Take only first 4 headers
    print('Done with mother extracts links')
    return mother_extracts


def extract_news_data(mother_extracts, driver, website):
    """
    Penetrates each category and extracts news links and data.
    """
    all_data = []
    stripped_website = website.strip('https://')

    for data in mother_extracts:
        print(f'Working on {data["Category"][0]}')
        for count, site in enumerate(data['News'], start=1):
            if site.split('/')[2] == stripped_website:
                timestamp = time.time()
                story_title, story_body = scrape_head_body(site, driver)

                main = {
                    'source': data['Data Source'],
                    'category_title': data['Category'][0],
                    'category_link': data['Category'][1],
                    'date_time': time.ctime(timestamp),
                    'link': site,
                    'story_title': story_title,
                    'story_body': story_body,
                }
                all_data.append(main)
                print(f'Done with {count} out of {len(data["News"])}')
                time.sleep(3)

    return all_data


def upload_data_to_bigquery(all_data, table_id):
    """
    Uploads the extracted data to BigQuery.
    """
    client = google_client()
    job = upload_to_bigquery(client=client, table_id=table_id, data=all_data)
    return job


def send_email_report(sites_num, job_status, timestamp):
    """
    Sends a report email with the result of the scraping and upload.
    """
    subject = "AKRONOMA PROJECT"
    body = f'''Done with scraping {sites_num} news links on {time.ctime(timestamp)}
            BIGQUERY UPLOAD ERRORS -----> <<<{job_status}>>>'''
    email_sender(subject, body, app_email)
    print('Completed ----> Check your email for details')


def main():
    table_id = "akronoma.NewsScraping.All_news"
    website = "https://www.ghanaweb.live/"

    driver = initialize_scraping(website)

    if driver:
        mother_extracts = extract_mother_links(driver, website)

        for news in mother_extracts:
            site = news['Category'][1]
            news["News"] = penetrate_site(site, driver)
            time.sleep(3)

        all_data = extract_news_data(mother_extracts, driver, website)
        driver.quit()

        job_status = upload_data_to_bigquery(all_data, table_id)
        sites_num = sum(len(data['News']) for data in mother_extracts)
        send_email_report(sites_num, job_status, time.time())

    else:
        subject = "AKRONOMA PROJECT"
        body = f"Driver Failed to initialize"
        email_sender(subject, body, app_email)
        print('Driver not initialized')


if __name__ == '__main__':
    main()
