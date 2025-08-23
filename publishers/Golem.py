from GLOBALS import *; DEBUG = (__name__ == "__main__")

def read_headlines():
  log("Golem.read_headlines()")
  with urllib.request.urlopen("https://rss.golem.de/rss.php?feed=RSS2.0") as f:
    feed = f.read().decode("ISO-8859-1").replace("<?xml ", "<html ").replace("link>", "url>")
  soup = bs4.BeautifulSoup(feed, "html.parser")
  articles = []
  for i in soup.find_all("item"):
    a = Article(publisher="Golem", category="Computer", column="Links")
    a.title = i.title.text
    a.description = add_punctuation(re.sub(r" \(<a .*", "", i.description.text))
    a.url = i.url.text
    a.pubdate = timestamp(i.pubdate.text)
    articles.append(a)
  return articles

if nDEBUG: # read_headlines()
  for a in read_headlines():
    logi(a)
    log(f"age = {(time.time() - a.pubdate) / 3600 :.0f} hrs")
    logo()
  exit()

publishers["Golem"] = Publisher(read_headlines=read_headlines)
