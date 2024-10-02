from GLOBALS import *; DEBUG = (__name__ == "__main__")

def read_headlines():
  log("IEEE_Spectrum.read_headlines()")
  with urllib.request.urlopen("https://spectrum.ieee.org/feeds/feed.rss") as f:
    feed = f.read().decode("utf-8").replace("<?xml ", "<html ").replace("link>", "url>")
  soup = bs4.BeautifulSoup(feed, "html.parser")
  articles = []
  for i in soup.find_all("item"):
    a = Article(publisher="IEEE_Spectrum", lang="en")
    a.title = i.title.text
    a.description = re.sub(r"\s+", " ", bs4.BeautifulSoup(i.description.text, "html.parser").get_text()).strip()[:300] + "…"
    p = a.description.rfind(".")
    if p != -1: a.description = a.description[:p + 1]
    a.url = i.url.text
    a.pubdate = timestamp(i.pubdate.text)
    for c in i.find_all("category"):
      c = c.get_text().lower()
      if "artificial intelligence" in c: a.category = "KI"; a.read = True
      if c == "type:sponsored": a.title += " (Advertisement)"
      if c == "type:podcast": a.title += " (Podcast)"
    articles.append(a)
  return articles

if DEBUG: # read_headlines()
  for a in read_headlines():
    logi(a)
    log(f"age = {(time.time() - a.pubdate) / 3600 :.0f} hrs")
    logo()
  exit()

publishers["IEEE_Spectrum"] = Publisher(read_headlines=read_headlines)
