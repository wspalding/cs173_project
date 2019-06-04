#need to replace with mechanicalsoup
import mechanicalsoup as MechSoup
from bs4 import BeautifulSoup as BSoup
from news_collector.utils.text_reader import get_labels
import json
import requests
import datetime

class news_collector():
    def __init__(self):
        self.browser = MechSoup.StatefulBrowser()

    def get_msnbc_links(self, **kwargs):
        start = kwargs.get('url', "https://www.msnbc.com/")
        self.browser.open(start)
        page = self.browser.get_current_page()
        urls = []
        #print(len(articles))
        #all -> div.id = content
        #top story = section2 -> a.href
        #seconday story = section3 -> article -> a.href
        #third set story = section4 -> article -> a.href
        #fourth & fifth = section5 -> a.href
        #sixth = section 6 -> ul -> li -> h2 -> a.href
        #vids = section7 -> video
        content = page.find_all('div', {'id': 'content'})
        #urls.append(len(content))
        for cont in content:
            #secs = cont.find_all('section')
            #url.append(secs)
            for sec in cont.find_all('section'):
                for a in sec.find_all('a'):
                    urls.append(a.attrs.get('href', None))
                for ul in sec.find_all('ul'):
                    for li in ul.find_all('li'):
                        for h2 in li.find_all('h2'):
                            for a in h2.find_all('a'):
                                urls.append(a.attrs.get('href', None))
                for h3 in sec.find_all('h3'):
                    for a in h3.find_all('a'):
                        urls.append(a.attrs.get('href', None))
                for article in sec.find_all('article'):
                    for a in article.find_all('a'):
                        urls.append(a.attrs.get('href', None))
            
            #print(url)
        urls = set(i for i in urls if not any(i in s for s in urls if i != s))
        urls = set(i for i in urls if (i.startswith("https://www.msnbc.com") or i.startswith("https://www.nbcnews.com")))
        
        urls = [i for i in urls if i.count("/") >=5]
        return urls
    
    def extract_msnbc_info(self, **kwargs):
         # things to set:
            # date, source, status_code, 
            # title, labels, text, 
            # author, media,
        urls = kwargs.get("urls", self.get_msnbc_links())
        info = {}
        for url in urls:
            try:
                response = self.browser.open(url)
            except:
                cur_dict["status_code"] = "Error could not open url"
                continue
            page = self.browser.get_current_page()
            info[url] = {}
            cur_dict = info[url]
            response = self.browser.open(url)
            cur_dict["date"] = datetime.date.today()
            cur_dict["source"] = "MSNBC"
            cur_dict["source_url"] = "https://www.msnbc.com/"
            cur_dict["status_code"] = response.status_code
            page = self.browser.get_current_page()
            if response.status_code != 200:
                continue;
            cur_dict["title"] = page.find('h1').text
            cur_dict["text"] = ""
            cur_dict["labels"] = get_labels(cur_dict["text"], cur_dict["title"])
#            cur_dict["author"] = "unknown"
#            author = page.find('section', {'class':'mb7'})
#            if author is None:
#                index = url.find("www.msnbc.com/")
#                end_index = url.find("/watch/")
#                if index >= 0 and end_index > index:
#                    cur_dict["author"] = url[index+len("www.msnbc.com/"):end_index]
#            if author is not None:
#                index = author.text.find("By ")
#                if index > 0:
#                    cur_dict["author"] = author.text[index+len("By "):]
#                else:
#                    cur_dict["author"] = "unknown"
#                #cur_dict["author"] = author.text
            cur_dict["media"] = None
            text = page.find_all('p')
            full_text = ""
            copy_right = "This material may not be"
            #if type(text) != list:
            #    text = [text]
            for t in text:
                if copy_right not in t:
                    full_text += "\n" + t.text
            real_text = full_text.encode('ascii', 'ignore')
            #print(full_text)
            real_text = real_text.decode("utf-8")
            #real_text = real_text.replace(copy_right, "")
            #real_text = real_text.replace(copy_right2, "")
            cur_dict["text"] = real_text
            cur_dict["labels"] = get_labels(real_text,
                                            cur_dict["title"])
        return info
    
    
    
    
    
    
    
    
    
    
    
    
    
    def get_fox_links(self):
        start_urls = [
        # lot of catagories might want to start at home 
        # and traverse to all these
        # assumign these all have the same html layout
        "https://www.foxnews.com/us",
        "https://www.foxnews.com/world", 
        "https://www.foxnews.com/science", 
        "https://www.foxnews.com/tech", 
        "https://www.foxnews.com/health",
        "https://www.foxnews.com/opinion",
        "https://www.foxnews.com/politics", 
        #"https://www.foxnews.com/shows", # 0 results
        #"https://www.foxnews.com/entertainment", 
        "https://www.foxbusiness.com/",
        ]
        urls = set()
        for url in start_urls:
            self.browser.open(url)
            page = self.browser.get_current_page()
            articles = page.find_all('article')
            #print(len(articles))
            for art in articles:
                div_m = art.find_all('div', {"class": "m"})
                for m in div_m:
                    all_a = m.find_all('a')
                    for a in all_a:
                        link = a.attrs['href']
                        if "http" not in link:
                            end = url.find(".com") + len(".com")
                            link = url[:end] + link
                        urls.add(link)
                        #print(url)
            #browser.close()
        return urls
    
    
    def extract_fox_info(self, **kwargs):
        urls = kwargs.get("urls", self.get_fox_links())
        info = {}
        for url in urls:
            info[url] = {}
            cur_dict = info[url]
            try:
                response = self.browser.open(url)
            except:
                cur_dict["status_code"] = "Error could not open url"
                continue
            cur_dict["date"] = datetime.date.today()
            cur_dict["source"] = "Fox"
            cur_dict["source_url"] = "https://www.foxnews.com/"
            cur_dict["status_code"] = response.status_code
            page = self.browser.get_current_page()
            if response.status_code != 200:
                continue;
            cur_dict["title"] = page.find("h1").text
            text = page.find_all('p')
            full_text = ""
            copy_right = "This material may not be published, broadcast, rewritten, or redistributed. 2019 FOX News Network, LLC. All rights reserved. All market data delayed 20 minutes."
            #if type(text) != list:
            #    text = [text]
            for t in text[1:-1]:
                #if copy_right not in t:
                if t.find(copy_right) is None:
                    full_text += " \n" + t.text
                    #full_text += "\n" + t.text[copy_index+len(copy_right):]
            real_text = full_text.encode('ascii', 'ignore')
            #print(full_text)
            #copy_right1 = " \n      This material may not be published, broadcast, rewritten,\n or redistributed. 2019 FOX News Network, LLC. All rights reserved.\n All market data delayed 20 minutes.\n     \n(2011 Getty Images)"
            
            real_text = real_text.decode("utf-8")
            #real_text = real_text.replace(copy_right, "")
            #real_text = real_text.replace(copy_right2, "")
            cur_dict["text"] = real_text
            cur_dict["labels"] = get_labels(real_text,
                                            cur_dict["title"])
            #cur_dict["text"] = full_text
#            author = page.find("div", {"class": "author-byline"})
#            if author:
#                author = author.find('a')
#            if author is None:
#                    author = page.find("span", {"class": "author"})
#            name = "unknown"
#            if author:
#                name = author.text
#                #bar = name.find("|")
#                #if bar != -1:
#                    #name = name[4 : (bar - 1)]
#                    #name = new_name
#            cur_dict["author"] = name
            cur_dict["media"] = None
            vid = page.find("div", {"class": "video-container"})
            if vid:
                a = vid.find('a')
                if a:
                    v = a.attrs["href"]
                    if "http" not in v:
                        cur_dict["media"] = url
                    else:
                        cur_dict["media"] = v
        return info
            
            
        
        
        
        
        
        
        
    # dont actually need this function because extract_kqed_info handles it
    def get_kqed_links(self):
        request = requests.get("https://projects-api.kqed.org/posts/news?&page[size]=100&page[from]=0")

        content = json.loads(request.text)
        links = set()
        for dic in content["data"]:
            links.add(dic["attributes"]["disqusUrl"])
        return links
    
    
    def extract_kqed_info(self, **kwargs):
        request = requests.get("https://projects-api.kqed.org/posts/news?&page[size]=100&page[from]=0")

        content = json.loads(request.text)
        info = {}
        for post in content["data"]:
            
            info[post["attributes"]["disqusUrl"]] = {}
            cur_dict = info[post["attributes"]["disqusUrl"]]
            cur_dict["date"] = datetime.date.today() #need to convert from epoch
            cur_dict["source"] = "KQED"
            cur_dict["source_url"] = "https://www.kqed.org/"
            cur_dict["status_code"] = request.status_code
            cur_dict["title"] = post["attributes"]["title"]
#            cur_dict["author"] = "unknown"
            result = self.browser.open(post["attributes"]["disqusUrl"])
            page = self.browser.get_current_page()
            # author = page.find("span", {"class":"src-routes-Site-routes-Post-components-Post-___Post__post_Author___3vn-d"})
            # if author is not None:
            #     cur_dict["author"] = author.text
            cur_dict["media"] = post["attributes"].get("nprAudio", None)
            text = post["attributes"].get("content", None)
            soup = BSoup(text, "lxml")
            text = soup.get_text()
            cur_dict["text"] = text.encode('ascii', 'ignore').decode("utf-8")
            cur_dict["labels"] = get_labels(cur_dict["text"], cur_dict["title"])
        return info
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    def get_NYT_links(self):
        start_url = "https://www.nytimes.com"
        self.browser.open(start_url)
        page = self.browser.get_current_page()

        articles = page.find_all('article')
        urls = set()
        #print(len(articles))
        for art in articles:
            all_a = art.find_all('a')
            for a in all_a:
                url = start_url + a.attrs['href']
                urls.add(url)
                #print(url)
        return list(urls)
    
    def extract_NYT_info(self, **kwargs):
        urls = kwargs.get("urls", self.get_NYT_links())
        info = {}
        for url in urls:
            # things to set:
            # date, source, status_code, 
            # title, labels, text, 
            # author, media,
            info[url] = {}
            cur_dict = info[url]
            try:
                response = self.browser.open(url)
            except:
                cur_dict["status_code"] = "Error could not open url"
                continue
            cur_dict["date"] = datetime.date.today()
            cur_dict["source"] = "NYT"
            cur_dict["source_url"] = "https://www.nytimes.com"
            cur_dict["status_code"] = response.status_code
            page = self.browser.get_current_page()
            if response.status_code != 200:
                continue;
            #div = page.find_all("div", {"class": "rad-article"})
            title = ""
            pos_title = page.find_all("h1")
            for pos in pos_title:
                title += pos.text
            #return str(page)
            #if div is not None:
                #header = div.find("header")
                #p = header.find("p")
                #if p is not None:
                    #title = title + p.text
            cur_dict["title"] = title
            
            text = ""
            for p in page.find_all("p"):
                text += p.text + " "
            cur_dict["text"] = text 
            cur_dict["labels"] = get_labels(cur_dict["text"], cur_dict["title"])
#            author = page.find("p", {"itemprop":"author creator"})
#            cur_dict["author"] = "unknown"
#            if author is not None:
#                #a = author.find("a")
#                #if a is not None:
#                cur_dict["author"] = author.text
            cur_dict["media"] = None
        return info
    
    
    
    
    
    
    
    def get_LAT_links(self):
        start_url = "https://www.latimes.com"
        self.browser.open(start_url)
        page = self.browser.get_current_page()
        articles = page.find_all('div', {"class": "card"})
        urls = set()
        #print(len(articles))
        for art in articles:
            all_a = art.find_all('a')
            for a in all_a:
                link = a.attrs['href']
                if "https://" not in link:
                    end = start_url.find(".com") + len(".com")
                    link = start_url[:end] + link
                #print(link)
                if link.find("#nt") == -1:
                    urls.add(link)
                #print(url)
        return list(urls)
    
    
    
    
    
    
    def get_NPR_links(self):
        start_url = "https://www.npr.org/"
        self.browser.open(start_url)
        page = self.browser.get_current_page()
        articles = page.find_all('article')
        urls = set()
        #print(len(articles))
        for art in articles:
            all_a = art.find_all('a')
            for a in all_a:
                link = a.attrs['href']
                #if "https://" not in link:
                #    end = start_url.find(".com") + len(".com")
                #    link = start_url[:end] + link
                #print(link)
                #if link.find("#nt") == -1:
                urls.add(link)
                #print(url)
        return list(urls)
        
        
        
