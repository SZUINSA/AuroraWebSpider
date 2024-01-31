import sys
import subprocess
from bs4 import BeautifulSoup

import hashlib
import time
from db import *

def extract_text(html):
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(separator='')
    return text.replace("\r\n","").replace("\n","")

def calc_md5(string):
    md5_hash = hashlib.md5()
    md5_hash.update(string.encode('utf-8'))
    return md5_hash.hexdigest()

def singlefile(url):
    chrome_path = '""'
    if sys.platform.startswith('darwin'):
        chrome_path = '"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"'
    elif sys.platform.startswith('win'):
        chrome_path = '"C:\Program Files\Google\Chrome\Application\chrome.exe"'
    else:
        chrome_path = '"/usr/bin/google-chrome"'
    command = [
        'single-file',
        '--block-scripts=false',
        '--browser-executable-path=' + chrome_path,
        '--browser-width=1600',
        '--browser-height=900',
        '--compress-CSS=true',
        '--browser-ignore-insecure-certs=true',
        '--http-proxy-server="http://local-lab.hz2016.cn:7890"',
        #'--http-proxy-username="hz2016"',
        #'--http-proxy-password="hz20162333"',
        '--save-original-urls=true',
        #'--max-resource-size=50',
        #'--browser-wait-delay=1000',
        #'--browser-load-max-time=60000',
        #'--load-deferred-images-max-idle-time=10000',
        '--dump-content=true',
        url
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True)
        return extract_text(result.stdout),result.stdout
    except:
        return "",""

db=sqliteDB()
while True:
    try:
        try:
            url,site,title=db.random_html()
        except:
            time.sleep(300)
            continue
        print(site,url,title,end="")
        summary,content=singlefile("https://"+url)
        folder_name = "html"
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        content_md5=calc_md5(url)
        file_path=os.path.join(folder_name,content_md5+".html")
        with open(file_path,"w") as f:
            f.write(content)
        db.insert_html(url, site, title, summary,content_md5)
        print(" SUCCESS")
    except:
        pass
    
