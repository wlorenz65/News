from GLOBALS import *; DEBUG = (__name__ == "__main__")

def read_headlines():
  log("Spiegel.read_headlines()")
  with urllib.request.urlopen("https://www.spiegel.de/schlagzeilen/index.rss") as f:
    feed = f.read().decode("utf-8").replace("<?xml ", "<html ").replace("link>", "url>")
  soup = bs4.BeautifulSoup(feed, "html.parser")
  articles = []
  for i in soup.find_all("item"):
    a = Article(publisher="Spiegel")
    a.title = i.title.text
    a.description = i.description.text if i.description else ""
    a.url = re.sub(r"#.*", "", i.url.text)
    a.pubdate = int(time.mktime(time.strptime(i.pubdate.text, "%a, %d %b %Y %H:%M:%S %z")))
    if "/international/" in a.url: a.lang="en"; a.category = "Other"
    if "/sport/" in a.url: a.title += " (Sport)"
    articles.append(a)
  return articles

if DEBUG: # read_headlines()
  for a in read_headlines():
    logi(a)
    log(f"age = {(time.time() - a.pubdate) / 3600 :.0f} hrs")
    logo()
  exit()

def read_article(a):
  log(f'Spiegel.read_article({a})')
  soup = url_to_soup(a.url)
  if soup.find("div", {"data-area":"paywall"}):
    a.url = "https://archive.li/newest/" + a.url
  a.column = "Links"

if DEBUG: # read_article()
  url = "https://www.spiegel.de/auto/luxemburg-wie-der-kostenlose-nahverkehr-funktioniert-a-d7dacc37-bd79-4def-99ab-66226ff14c8b"
  a = Article(url=url, category="Andere", pubdate=int(time.time()))
  g.cache_urls = True
  read_article(a)
  log(a.url)
  exit()

publishers["Spiegel"] = Publisher(read_headlines=read_headlines, read_article=read_article)
