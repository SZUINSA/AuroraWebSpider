from flask import Flask, request,render_template,redirect,url_for,send_from_directory
from db import *
from datetime import datetime
from bs4 import BeautifulSoup
from flask_compress import Compress
from flask_httpauth import HTTPBasicAuth
import socket


socket.setdefaulttimeout(120)
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 3600
app.config['STATIC_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
auth = HTTPBasicAuth()
compress = Compress(app)

@auth.verify_password
def verify_password(username, password):
    if password == 'MakeAuroraGreatAgain':
        return True
    return False


@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(app.config['STATIC_FOLDER'], filename)
def isnas(variable):
    return variable.isalnum() and variable.islower()
class BreakLoop(Exception):
    pass
startwith = ["https://","http://",""]

@app.route('/show', methods=['GET'])
def show():
    url=request.args.get("url")
    if url == "None" or isnas == False:
        return redirect(url_for('list'))
    file_path = os.path.join("html",url+".html")
    with open(file_path,"r") as f:
        data=f.read()
        try:
            cachetime = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y/%m/%d %H:%M')
            db = sqliteDB()
            items = db.list_raw()
            banner="Aurora 离线缓存"
            for item in items:
                if item[0] is None or item[1] is None or item[0] == "" or item[1] == "":
                    items.remove(item)
                elif item[1]==url:
                    banner=f"网站/SITE：{item[2]} 网址/URL：{item[0]} 缓存时间/CACHETIME：{cachetime}"
            print(banner)
            soup = BeautifulSoup(data, 'html.parser')
            tags = soup.find_all()
            for tag in tags:
                try:
                    href = tag['href']
                    try:
                        for rep in items:
                            for start in startwith:
                                if href == start+rep[0]:
                                    href = f"/show?url={rep[1]}"
                                    raise BreakLoop
                    except BreakLoop:
                            tag['href'] = href
                            
                except:
                    pass
            
            banner_div = soup.new_tag('div', attrs={'class': 'aurora_banner'})
            banner_div['style'] = 'width: 100%; height: 30px; background-color: #007aff; color: white; text-align: center; position: fixed;  top: 0; left: 0; z-index: 9999;'
            banner_div.string = banner
            body_tag = soup.body
            body_tag.insert(0, banner_div)
            
            data = soup.prettify()
        except:
            pass
    return data

'''
@app.route('/rebuild', methods=['GET'])
def rebuild():
    return redirect(url_for('list'))
'''

@app.route('/site', methods=['GET'])
def site():
    db = sqliteDB()
    items=db.list_site("")
    return render_template('site.html',items=items)

@app.route('/edit', methods=['GET'])
@auth.login_required
def edit():
    db = sqliteDB()
    url=request.args.get("url")
    if url is None:
        items=[("","","","")]
    else:
        items=db.list_site(url)
    return render_template('edit.html',items=items[0])

@app.route('/update', methods=['GET'])
@auth.login_required
def update():
    db = sqliteDB()
    url=request.args.get("url")
    if url is None:
        return redirect(url_for('site'))
    items=db.list_site(url)
    item=items[0]
    db.insert_site(item[0],item[1],-item[2])
    return redirect(url_for('site'))

@app.route('/del', methods=['GET'])
@auth.login_required
def delsite():
    db = sqliteDB()
    url=request.args.get("url")
    if url is None:
        return redirect(url_for('site'))
    db.del_site(url)
    return redirect(url_for('site'))

@app.route('/add', methods=['GET'])
@auth.login_required
def add():
    db = sqliteDB()
    site=request.args.get("site")
    url=request.args.get("url")
    interval=request.args.get("interval")
    if interval is None:
        interval=30
    try:
        interval = int(interval)
    except ValueError:
        interval = 30
    if url!="" and site!="":
        db.insert_site(url, site, interval)
    return redirect(url_for('site'))

@app.route('/list', methods=['GET'])
@app.route('/', methods=['GET'])
def list():
    db = sqliteDB()
    summary=request.args.get("search")
    type=request.args.get("type")
    if summary is None:
        summary=""
    if type is None:
        type="0"
        
    items=db.list_html(summary,type)
    pages=db.list_page()
    return render_template('list.html',pages=pages, items=items)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=False)
    
