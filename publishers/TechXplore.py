from GLOBALS import *; DEBUG = (__name__ == "__main__")

def read_headlines():
  log("TechXplore.read_headlines()")
  with urllib.request.urlopen("https://techxplore.com/rss-feed/") as f:
    feed = f.read().decode("utf-8").replace("<?xml ", "<html ").replace("link>", "url>")
  soup = bs4.BeautifulSoup(feed, "html.parser")
  articles = []
  for i in soup.find_all("item"):
    a = Article(publisher="TechXplore", lang="en", category="Other")
    a.title = i.title.text
    a.description = i.description.text
    a.url = i.url.text
    t = i.pubdate.text.replace("EST", "-0500").replace("EDT", "-0400")
    a.pubdate = int(time.mktime(time.strptime(t, "%a, %d %b %Y %H:%M:%S %z")))
    if i.category.text == "Machine learning & AI": a.category = "AI.en"; a.read = True
    articles.append(a)
  return articles

if DEBUG: # read_headlines()
  for a in read_headlines():
    logi(a)
    log(f"age = {(time.time() - a.pubdate) / 3600 :.0f} hrs")
    logo()
  exit()

publishers["TechXplore"] = Publisher(read_headlines=read_headlines)
