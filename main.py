from functions import *
import os


if __name__ == '__main__':

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
        data = {}
        data["Data Source"] = website
        data["Category"] = (items.text, items.get_attribute("href"))
        data["News"] = []

        mother_extracts.append(data)

    mother_extracts = mother_extracts[:5]
    print('Done with mother extracts')

    for news in mother_extracts:
        site = news['Category'][1]
        news["News"] = (penetrate_site(site, driver))
        time.sleep(5)
    data = pd.DataFrame(mother_extracts)

    print('Done with mother extracts links')

    all_data = []
    sites_num = 0

    for data in mother_extracts:
        print(f'Working on {data["Category"][0]}')
        count = 0
        for sites in data['News']:
            if sites.split('/')[2] == website.strip('https://'):
                main = {}
                main['source'] = data['Data Source']
                main['category'] = data['Category']
                timestamp = time.time()
                main['date_time'] = time.ctime(timestamp)
                main['link'] = sites
                main['story'] = scrape_head_body(sites, driver)
                time.sleep(5)
                count += 1
                print(f'Done with {count} out of {len(data["News"])}')
                all_data.append(main)
                sites_num += len(data['News'])

    all_news = pd.DataFrame(all_data)
    columns = ['source', 'category', 'date_time', 'link', 'story']
    all_news.columns = columns

    print('Done with extracting all news')

    driver.quit()

    client = google_client()

    job = upload_to_bigquery(client, all_news)

    subject = "AKRONOMA PROJECT"
    body = f'''Done with scraping {sites_num} news links on {time.ctime(timestamp)}
            Uploaded to <<<{job}>>>'''
    email_sender(subject, body, app_email)
