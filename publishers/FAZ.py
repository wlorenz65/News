from GLOBALS import *; DEBUG = (__name__ == "__main__")

def read_headlines():
  log("FAZ.read_headlines()")
  with urllib.request.urlopen("https://www.faz.net/rss/aktuell/") as f:
    feed = f.read().decode("utf-8").replace("<?xml ", "<html ").replace("atom:link", "atom:url").replace("link>", "url>")
  soup = bs4.BeautifulSoup(feed, "html.parser")
  articles = []
  for i in soup.find_all("item"):
    a = Article(publisher="FAZ")
    a.title = i.title.text
    a.description = description(i)
    a.url = i.url.text
    a.pubdate = timestamp(i.pubdate.text)
    if "/sport/" in a.url: a.title += " (Sport)"
    if "/podcasts/" in a.url: a.title += " (Podcast)"
    articles.append(a)
  return articles

if nDEBUG: # read_headlines()
  for a in read_headlines():
    logi(a)
    log(f"age = {(time.time() - a.pubdate) / 3600 :.0f} hrs")
    logo()
  exit()

def read_article(a):
  log(f'FAZ.read_article({a})')
  soup = url_to_soup(a.url)
  if soup.find("section", class_="js-atc-ContainerPaywall atc-ContainerPaywall"):
    a.url = "https://archive.li/newest/" + a.url
  a.column = "Links"

#das ist paywall und wird nicht erkannt
#da hilft kein archive.li https://www.faz.net/aktuell/wissen/medizin-ernaehrung/schmerzen-nach-operationen-werden-opioide-zu-freizguegig-verschrieben-19654830.html
#https://www.faz.net/aktuell/rhein-main/region-und-hessen/wie-ein-blackout-die-landwirtschaft-gefaehrden-wuerde-19546412.html
# https://m.faz.net/aktuell/wirtschaft/unternehmen/weltwirtschaftsforum-ki-ist-in-davos-nachmieter-der-russen-19452071.html
# https://m.faz.net/aktuell/wirtschaft/kuenstliche-intelligenz/ki-revolution-ohne-europa-weltwirtschaftsforum-in-davos-zeigt-realitaet-19454178.html
# https://www.faz.net/aktuell/stil/quarterly/co2-aus-der-luft-holen-carbon-capture-soll-die-klima-katastrophe-abwenden-19617614.html

if DEBUG: # read_article()
  url = "https://www.faz.net/aktuell/wissen/forschung-politik/gefaelschte-forschung-wie-organisationen-ergebnisse-fuer-profit-erfinden-19416217.html"
  a = Article(url=url, category="Andere", pubdate=int(time.time()), id=0)
  g.cache_urls = True
  read_article(a)
  log(a.url)
  exit()

publishers["FAZ"] = Publisher(read_headlines=read_headlines, read_article=read_article)
