from functions import *
import os

website = "https://www.ghanaweb.com/"
mother_extracts = []

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
if not os.path.exists("allnews_links.csv") or os.stat("allnews_links.csv").st_size == 0:
    data.to_csv("allnews_links.csv", mode='a', index=False, header=True)
else:
    data.to_csv("allnews_links.csv", mode='a', index=False, header=False)
print('Done with mother extracts links')

all_data = []
count = 0
for data in mother_extracts:
    for sites in data['News'][:6]:
        if sites.split('/')[2] == "www.ghanaweb.com":
            main = {}
            main['Data Source'] = data['Data Source']
            main['Category'] = data['Category']
            timestamp = time.time()
            main['Time'] = time.ctime(timestamp)
            main['Story'] = scrape_head_body(sites, driver)
            time.sleep(5)
            count += 1
            print(f'Done with {count} out of {len(mother_extracts) * 6}')
            all_data.append(main)

all_news = pd.DataFrame(all_data)
if not os.path.exists("allnews_links.csv") or os.stat("allnews_links.csv").st_size == 0:
    all_news.to_csv("allnews.csv", mode='a', index=False, header=True)
else:
    all_news.to_csv("allnews.csv", mode='a', index=False, header=False)
print('Done with mother extracts links')
