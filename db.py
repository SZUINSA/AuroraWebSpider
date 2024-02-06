import os
import sqlite3
class sqliteDB:
    def __init__(self) -> None:
        if(os.path.exists('sqlite.db')==False):
            self.db = sqlite3.connect('sqlite.db')
            print("Building DataBase...")
            self.make()
            print("Building Database Succeed.")
        else:
            self.db = sqlite3.connect('sqlite.db')
            self.make()
            print("Connect Database Succeed.")
        self.db.enable_load_extension(True)
        self.db.execute('PRAGMA temp_store=MEMORY;')
        self.db.execute('PRAGMA journal_mode=MEMORY;')
        self.db.execute('PRAGMA auto_vacuum=INCREMENTAL;')
        
    def make(self) -> None:
        self.db.execute('''CREATE TABLE IF NOT EXISTS html(
                url VARCHAR(256) PRIMARY KEY,
                site VARCHAR(256),
                title TEXT,
                summary TEXT,
                content TEXT,
                updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP);''')
        self.db.execute('''CREATE TABLE IF NOT EXISTS site(
                url VARCHAR(256) PRIMARY KEY,
                site VARCHAR(256),
                interval INT,
                updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP);''')
        
        self.db.commit()
        
    def insert_html(self, url, site, title=None, summary=None, content=None):
        
        self.db.execute("REPLACE INTO html (url, site, title, summary, content) VALUES (?, ?, ?, ?, ?)",(url, site, title, summary, content))
        self.db.commit()
        
    def insert_site(self, url, site, interval):
        cursor = self.db.execute("SELECT site FROM site WHERE url = ?",(url,))
        for i in cursor:
            self.db.execute("UPDATE html SET site=? WHERE site=?",(site, i[0]))
        self.db.execute("REPLACE INTO site (url, site, interval) VALUES (?, ?, ?)",(url, site, interval))
        self.db.commit()

    def del_site(self,url):
        self.db.execute("DELETE FROM site WHERE url=?",(url,))
        self.db.commit()
    def random_html(self):
        cursor = self.db.execute("SELECT url,site,title FROM html WHERE summary IS NULL ORDER BY RANDOM() LIMIT 1")
        for i in cursor:
            return i[0],i[1],i[2]
        
    def show_html(self,url):
        cursor = self.db.execute("SELECT url,site,title,content FROM html WHERE url=? LIMIT 1",(url,))
        for i in cursor:
            return i[0],i[1],i[2],i[3]
        
    def list_html(self,summary,type):
        if summary=="":
            return []
        else:
            summary=f"%{summary}%"
            if type=="0":
                cursor = self.db.execute("SELECT url,site,title,content FROM html WHERE summary like ? OR title like ? OR url like ?",(summary,summary,summary))
            elif type=="1":
                cursor = self.db.execute("SELECT url,site,title,content FROM html WHERE title like ?",(summary,))
            elif type=="2":
                cursor = self.db.execute("SELECT url,site,title,content FROM html WHERE site like ?",(summary,))
            elif type=="3":
                cursor = self.db.execute("SELECT url,site,title,content FROM html WHERE url like ?",(summary,))
            elif type=="4":
                cursor = self.db.execute("SELECT url,site,title,content FROM html WHERE summary like ?",(summary,))
            return [(i[0],i[1],i[2],i[3]) for i in cursor]
    
    def list_site(self,url=""):
        if url=="":
            cursor = self.db.execute("SELECT url,site,interval,updated FROM site WHERE 1")
        else:
            cursor = self.db.execute("SELECT url,site,interval,updated FROM site WHERE url=?",(url,))
        return [(i[0],i[1],i[2],i[3]) for i in cursor]
    
    def list_page(self):
        cursor = self.db.execute("SELECT count(*) FROM html WHERE summary IS NOT NULL")
        for i in cursor:
            return i[0]
    
    def list_raw(self):
        cursor = self.db.execute("SELECT url,content,site,title FROM html WHERE 1")
        return [(i[0],i[1],i[2],i[3]) for i in cursor]
    
