from GLOBALS import *; DEBUG = (__name__ == "__main__")

def read_headlines():
  log("Zeit.read_headlines()")
  with urllib.request.urlopen("https://newsfeed.zeit.de/") as f:
    feed = f.read().decode("utf-8").replace("<?xml ", "<html ").replace("link>", "url>")
  soup = bs4.BeautifulSoup(feed, "html.parser")
  articles = []
  for i in soup.find_all("item"):
    a = Article(publisher="Zeit")
    a.title = i.title.text
    a.description = i.description.text
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

def read_article(a):
  log(f"Zeit.read_article({a})")
  soup = url_to_soup(a.url)
  if soup.find("span", class_="zplus-badge__text"):
    a.url = "https://archive.li/newest/" + a.url
  a.column = "Links"

#https://www.zeit.de/digital/2024-01/ces-2024-tech-messe-usa-innovationen

if DEBUG: # read_article()
  url = "https://www.zeit.de/zeit-magazin/mode-design/2024-01/homewear-bequemlichkeit-stil"
  url = "https://www.zeit.de/wissen/2024-01/putzmittel-selber-machen-hausmittel-chemie-zitronensaeure-essig"
  url = "https://www.zeit.de/digital/mobil/2024-01/playstation-portal-remote-player-test"
  a = Article(url=url, category="Andere", pubdate=int(time.time()), id=0)
  g.cache_urls = True
  read_article(a)
  log(a.url)
  exit()

publishers["Zeit"] = Publisher(read_headlines=read_headlines, read_article=read_article)
