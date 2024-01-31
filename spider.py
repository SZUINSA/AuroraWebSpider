from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse,parse_qs,urlencode
from db import *
import json
from time import sleep
from datetime import datetime, timedelta


chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument('window-size=1600x900')
chrome_options.add_argument('--disable-infobars')
chrome_options.add_argument('--sandbox')
chrome_options.add_argument('--start-maximized')
chrome_options.add_argument('--disable-infobars')
chrome_options.add_argument('--hide-scrollbars')
chrome_options.add_argument('--proxy-server=http://local-lab.hz2016.cn:7890')
prefs = {
    "download.prompt_for_download": False,
    "download_restrictions": 3,
    "profile.password_manager_enabled": False,
    "credentials_enable_service": False,
    "profile.default_content_settings.popups": 0,
    "download.default_directory": "/dev/null",
    "directory_upgrade": True
}
chrome_options.add_experimental_option(
    "prefs", prefs
)
chrome_options.add_argument("--disable-gpu")

def getpath(url):
    parsed_url = urlparse(url)
    domain_path = parsed_url.netloc + parsed_url.path
    query_params = parse_qs(parsed_url.query)
    params_list = ['id','ids','page','pages']
    filtered_params = {k: v for k, v in query_params.items() if k in params_list}
    filtered_query = urlencode(filtered_params, doseq=True)
    full_url = f"{domain_path}?{filtered_query}" if filtered_query else domain_path
    return full_url

def is_file_url(url):
    file_extension = url.split('.')[-1].lower()
    file_extensions = ['css', 'js', 'jpg', 'jpeg', 'png','svg', 'gif', 'ico', 'bmp', 'webp', 'mp4', 'avi', 'mov', 'mkv', 'mp3', 'wav', 'flac']
    return file_extension in file_extensions

db = sqliteDB()

visited_url = set()

def addurl(url,site,title):
    visited_url.add(url)
    db.insert_html(url,site,title)

url_list = []
def recursive_crawl(site, domain,source,max_level=10):
    while len(url_list) > 0:
        url,current_level = url_list[0]
        url_list.remove((url,current_level))

        if url.startswith("javascript:"):
            continue
        if current_level < max_level:
            if getpath(url) in visited_url:
                continue
            driver = webdriver.Chrome(options=chrome_options)
            try:
                print(site,url,end="")
                driver.get(url)
                scroll_js = """
                    function scrollDown() {
                        window.scrollTo(0, document.body.scrollHeight);
                    }
                    setInterval(scrollDown, 500);
                """
                driver.execute_script(scroll_js)
                wait = WebDriverWait(driver, 3)
                wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
                print(" SUCCESS")

                addurl(getpath(url),site,driver.title)
                if urlparse(driver.current_url).netloc != domain or not getpath(url).startswith(source):
                    if is_file_url(driver.current_url)==False:
                        addurl(getpath(driver.current_url),site,driver.title)
                    driver.quit()
                    continue

                links = driver.find_elements(By.TAG_NAME,"*")
                for link in links:
                    try:
                        href = link.get_attribute("href")
                        if href:
                            full_url = getpath(href)
                            if not full_url in visited_url and is_file_url(full_url) == False:
                                url_list.append((href,current_level + 1))
                    except:
                        pass

                driver.quit()

            except:
                driver.quit()
                pass
            
while True:
    items=db.list_site()
    for item in items:
        
        if item[2]==0 or (item[2]>0 and datetime.now() - datetime.strptime(item[3], '%Y-%m-%d %H:%M:%S') < timedelta(days=item[2])):
            continue
        
        new_interval=item[2]
        if new_interval<0:
            new_interval = -new_interval
            
        db.insert_site(item[0],item[1],new_interval)
        
        print('上次更新时间:', item[3])
        print('站点:', item[1])
        print('网址:', item[0])
        
        try:
            url_list.append((item[0],0))
            visited_url = set()
            recursive_crawl(item[1], urlparse(item[0]).netloc, getpath(item[0]))
        except:
            pass

    sleep(300)
