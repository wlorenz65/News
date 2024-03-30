from GLOBALS import *; DEBUG = (__name__ == "__main__")

def read_headlines():
  log("Press24.read_headlines()")
  r = urllib.request.Request("https://press24.net/rss/all", headers=user_agent)
  with urllib.request.urlopen(r) as f:
    feed = f.read().decode("utf-8").replace("<?xml ", "<html ").replace("link>", "url>")
  soup = bs4.BeautifulSoup(feed, "html.parser")
  articles = []
  for i in soup.find_all("item"):
    a = Article(publisher="Press24")
    a.title = i.title.text
    d = description(i, end="…")
    d = re.sub(r".* Kommentare Drucken Teilen ", "", d)
    d = re.sub(r".* \d+ Bilder \d+ Bilder ", "", d)
    a.description = d
    a.url = i.url.text
    a.pubdate = int(time.mktime(time.strptime(i.pubdate.text, "%a, %d %b %Y %H:%M:%S %z")))
    if not a.title.endswith(("(Heise Online)", "(derStandard)", "(Spiegel)", "(FAZ)")):
      articles.append(a)
  return articles

if DEBUG: # read_headlines()
  for a in read_headlines():
    logi(a)
    log(f"age = {(time.time() - a.pubdate) / 3600 :.0f} hrs")
    logo()
  exit()

def read_article(a):
  logi(f'Press24.read_article({a})')
  soup = url_to_soup(a.url, headers=user_agent)
  a.url = urllib.parse.urljoin(a.url, soup.find("a", class_="article-title")["href"])
  log(a.url)
  a.column = "Links"
  logo()

if nDEBUG: # read_article()
  url = "https://press24.net/news/29403957/wieder-beim-discounter-aldi-verkauft-aeg-r-ckfahrkamera-im-angebot"
  a = Article(url=url, category="Andere", pubdate=int(time.time()), id=0)
  g.cache_urls = True
  read_article(a)
  exit()

publishers["Press24"] = Publisher(read_headlines=read_headlines, read_article=read_article)
