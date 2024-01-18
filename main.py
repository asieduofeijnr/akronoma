from functions import *
import os


if __name__ == '__main__':

    table_id = "akronoma.NewsScraping.All_news"
    website = "https://www.ghanaweb.live/"
    mother_extracts = []
    print('Driver Initializing... please wait')

    start_time = time.time()
    driver = initialize_website(website)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time} seconds")
    print('Done with initialization')

    nav_element = driver.find_elements(By.XPATH, '//ul[@id="mainnavinner"]//a')
    for items in nav_element:
        data = {"Data Source": website,
                "Category": (items.text, items.get_attribute("href")),
                "News": []
                }

        mother_extracts.append(data)

    mother_extracts = mother_extracts[:5]
    print('Done with mother extracts')

    for news in mother_extracts:
        site = news['Category'][1]
        news["News"] = (penetrate_site(site, driver))
        time.sleep(5)

    print('Done with mother extracts links')

    all_data = []
    sites_num = 0
    stripped_website = website.strip('https://')

    for data in mother_extracts:
        print(f'Working on {data["Category"][0]}')

        for count, site in enumerate(data['News'][:5], start=1):
            if site.split('/')[2] == stripped_website:
                timestamp = time.time()
                main = {
                    'source': data['Data Source'],
                    'category_title': data['Category'][0],
                    'category_link': data['Category'][1],
                    'date_time': time.ctime(timestamp),
                    'link': site,
                    'story_title': scrape_head_body(site, driver)[0],
                    'story_body': scrape_head_body(site, driver)[1],
                }
                time.sleep(5)

                print(f'Done with {count} out of {len(data["News"])}')
                all_data.append(main)

    sites_num = sum(len(data['News']) for data in mother_extracts)

    print('Done with extracting all news')

    driver.quit()

    client = google_client()

    job = upload_to_bigquery(client=client, table_id=table_id, data=all_data)

    subject = "AKRONOMA PROJECT"
    body = f'''Done with scraping {sites_num} news links on {time.ctime(timestamp)}
            BIGQUERY UPLOAD ERRORS -----> <<<{job}>>>'''
    email_sender(subject, body, app_email)

    print('Completed ----> Check your email for details')
