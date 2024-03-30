from GLOBALS import *; DEBUG = (__name__ == "__main__")

def read_headlines():
  log("Welt.read_headlines()")
  with urllib.request.urlopen("https://www.welt.de/?service=rss") as f:
    feed = f.read().decode("utf-8").replace("<?xml ", "<html ").replace("link>", "url>")
  soup = bs4.BeautifulSoup(feed, "html.parser")
  articles = []
  for i in soup.find_all("item"):
    a = Article(publisher="Welt")
    a.title = i.title.text
    a.description = i.description.text
    a.url = i.url.text
    a.pubdate = int(time.mktime(time.strptime(i.pubdate.text, "%a, %d %b %Y %H:%M:%S GMT")))
    if "/video" in a.url or "/mediathek/" in a.url: a.title += " (Video)"
    if "/plus" in a.url: a.url = "https://archive.li/newest/" + a.url
    articles.append(a)
  return articles

if DEBUG: # read_headlines()
  for a in read_headlines():
    logi(a)
    log(f"age = {(time.time() - a.pubdate) / 3600 :.0f} hrs")
    logo()
  exit()

publishers["Welt"] = Publisher(read_headlines=read_headlines)
