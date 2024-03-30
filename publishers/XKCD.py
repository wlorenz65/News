from GLOBALS import *; DEBUG = (__name__ == "__main__")

def read_headlines():
  log("XKCD.read_headlines()")
  with urllib.request.urlopen("https://xkcd.com/rss.xml") as f:
    feed = f.read().decode("utf-8").replace("<?xml ", "<html ").replace("link>", "url>")
  soup = bs4.BeautifulSoup(feed, "html.parser")
  articles = []
  for i in soup.find_all("item"):
    a = Article(publisher="XKCD", category="Computer", read=True)
    a.title = "XKCD: " + i.title.text
    a.description = re.search(r' alt="(.+?)" ', i.description.text).group(1)
    a.url = i.url.text
    a.pubdate = int(time.mktime(time.strptime(i.pubdate.text, "%a, %d %b %Y %H:%M:%S %z")))
    articles.append(a)
  return articles

if DEBUG: # read_headlines()
  for a in read_headlines():
    logi(a)
    log(f"age = {(time.time() - a.pubdate) / 3600 :.0f} hrs")
    logo()
  exit()

publishers["XKCD"] = Publisher(read_headlines=read_headlines)
