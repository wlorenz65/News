from GLOBALS import *; DEBUG = (__name__ == "__main__")

def read_headlines():
  log("Focus.read_headlines()")
  with urllib.request.urlopen("https://rss.focus.de/fol/XML/rss_folnews.xml") as f:
    feed = f.read().decode("utf-8").replace("<?xml ", "<html ").replace("link>", "url>")
  soup = bs4.BeautifulSoup(feed, "html.parser")
  articles = []
  for i in soup.find_all("item"):
    a = Article(publisher="Focus")
    a.title = i.title.text
    a.description = re.sub(r"\bVon FOCUS\b.*", "", i.description.text.strip()) if i.description else ""
    a.url = i.url.text
    a.pubdate = int(time.mktime(time.strptime(i.pubdate.text.strip(), "%a, %d %b %Y %H:%M:%S %z")))
    if "/deals/" in a.url: a.title += " (Werbung)"
    articles.append(a)
  return articles

if DEBUG: # read_headlines()
  for a in read_headlines():
    logi(a)
    log(f"age = {(time.time() - a.pubdate) / 3600 :.0f} hrs")
    logo()
  exit()

publishers["Focus"] = Publisher(read_headlines=read_headlines)
