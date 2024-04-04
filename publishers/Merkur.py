from GLOBALS import *; DEBUG = (__name__ == "__main__")

def read_headlines():
  logi("Merkur.read_headlines()")
  articles = []
  for ressort in ("lokales",):
    log(ressort)
    with urllib.request.urlopen(f"https://www.merkur.de/{ressort}/rssfeed.rdf") as f:
      feed = f.read().decode("utf-8").replace("<?xml ", "<html ").replace("link>", "url>")
    soup = bs4.BeautifulSoup(feed, "html.parser")
    for i in soup.find_all("item"):
      a = Article(publisher="Merkur")
      a.title = i.title.text
      a.description = i.description.text
      a.url = i.url.text
      a.pubdate = timestamp(i.pubdate.text)
      articles.append(a)
  logo()
  return articles

if DEBUG: # read_headlines()
  for a in read_headlines():
    logi(a)
    log(f"age = {(time.time() - a.pubdate) / 3600 :.0f} hrs")
    logo()
  exit()

publishers["Merkur"] = Publisher(read_headlines=read_headlines)
