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
    a.pubdate = timestamp(i.pubdate.text)
    articles.append(a)
  return articles

if nDEBUG: # read_headlines()
  for a in read_headlines():
    logi(a)
    log(f"age = {(time.time() - a.pubdate) / 3600 :.0f} hrs")
    logo()
  exit()

def read_article(a):
  log(f"Zeit.read_article({a})")
  soup = url_to_soup(a.url)
  if "dpa-infocom" not in soup.text and "Link kopieren" not in soup.text: a.url = "https://archive.li/newest/" + a.url
  a.column = "Links"

# Z+ registerwall nicht erkannt:
# https://www.zeit.de/2024/10/menschenaffen-emotionen-gefuehle-weinen-primatenforschung
# https://www.zeit.de/2024/10/martinshorn-erfinder-feuerwehr-alarm
# https://www.zeit.de/2024/14/cannabis-legalisierung-plantage-relzow
# https://www.zeit.de/2024/14/erinnerung-kleinkinder-kindheit-gedaechtnis
# https://www.zeit.de/2024/13/kuechenschraenke-trend-farben-preis

# Z+ paywall nicht erkannt:
# https://www.zeit.de/gesellschaft/schule/2024-03/schulversuche-pisa-studie-grundschule-reform

# keine registerwall, keine paywall, kein Z+ logo:
# https://www.zeit.de/news/2024-04/05/wie-china-mit-solar-seine-probleme-loest
# https://www.zeit.de/news/2024-04/05/viele-unterrichtsstunden-an-saechsischen-schulen-ausgefallen
# https://www.zeit.de/digital/2024-01/ces-2024-tech-messe-usa-innovationen

if DEBUG: # read_article()
  url = "https://www.zeit.de/2024/10/menschenaffen-emotionen-gefuehle-weinen-primatenforschung"
  a = Article(url=url, pubdate=int(time.time()), id=0)
  g.cache_urls = True
  read_article(a)
  log(a.url)
  exit()

publishers["Zeit"] = Publisher(read_headlines=read_headlines, read_article=read_article)
