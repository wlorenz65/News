from GLOBALS import *; DEBUG = (__name__ == "__main__")

def read_headlines():
  log("Tagesschau.read_headlines()")
  with urllib.request.urlopen("https://www.tagesschau.de/infoservices/alle-meldungen-100~rdf.xml") as f:
    feed = f.read().decode("utf-8").replace("<?xml ", "<html ").replace("link>", "url>")
  soup = bs4.BeautifulSoup(feed, "html.parser")
  articles = []
  for i in soup.find_all("item"):
    a = Article(publisher="Tagesschau")
    a.title = i.title.text
    a.description = re.sub(r" Von [\w .-]{3,40}\.$", "", i.description.text)
    a.url = i.url.text
    a.pubdate = int(time.mktime(time.strptime(i.pubdate.text, "%a, %d %b %Y %H:%M:%S %z")))
    if a.title.startswith("Liveblog"): a.title += " (Ticker)"
    articles.append(a)
  return articles

if DEBUG: # read_headlines()
  for a in read_headlines():
    logi(a)
    log(f"age = {(time.time() - a.pubdate) / 3600 :.0f} hrs")
    logo()
  exit()

publishers["Tagesschau"] = Publisher(read_headlines=read_headlines)
