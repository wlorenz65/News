from GLOBALS import *; DEBUG = (__name__ == "__main__")

def read_headlines():
  log("ExtremNews.read_headlines()")
  r = urllib.request.Request("https://www.extremnews.com/feed/", headers=user_agent)
  with urllib.request.urlopen(r) as f:
    feed = f.read().decode("utf-8").replace("<?xml ", "<html ")
  soup = bs4.BeautifulSoup(feed, "html.parser")
  articles = []
  for i in soup.find_all("entry"):
    a = Article(publisher="ExtremNews")
    a.title = i.title.text
    a.description = i.summary.text
    a.url = re.sub(r"\?.*", "", i.link["href"])
    a.pubdate = timestamp(i.published.text, "%Y-%m-%dT%H:%M:%SZ")
    articles.append(a)
  return articles

if DEBUG: # read_headlines()
  for a in read_headlines():
    logi(a)
    log(f"age = {(time.time() - a.pubdate) / 3600 :.0f} hrs")
    logo()
  exit()

publishers["ExtremNews"] = Publisher(read_headlines=read_headlines)
