from GLOBALS import *; DEBUG = (__name__ == "__main__")

def read_headlines():
  logi("NYTimes.read_headlines()")
  articles = []
  for ressort in "Business", "Technology", "Science":
    log(ressort)
    with urllib.request.urlopen(f"https://rss.nytimes.com/services/xml/rss/nyt/{ressort}.xml") as f:
      feed = f.read().decode("utf-8").replace("<?xml ", "<html ").replace("atom:link", "atom:url").replace("link>", "url>")
    soup = bs4.BeautifulSoup(feed, "html.parser")
    for i in soup.find_all("item"):
      a = Article(publisher="NYTimes", lang="en", category="Other")
      a.title = i.title.text
      a.description = i.description.text if i.description else ""
      a.url = i.url.text # online.py translates with Google instead of using "https://archive.li/newest/" + i.url.text here
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

publishers["NYTimes"] = Publisher(read_headlines=read_headlines)
