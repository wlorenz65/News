from GLOBALS import *; DEBUG = (__name__ == "__main__")

def read_headlines():
  log("The_Decoder.read_headlines()")
  with urllib.request.urlopen("https://the-decoder.de/feed/") as f:
    feed = f.read().decode("utf-8").replace("<?xml ", "<html ").replace("link>", "url>")
  soup = bs4.BeautifulSoup(feed, "html.parser")
  articles = []
  for i in soup.find_all("item"):
    a = Article(publisher="The_Decoder", category="KI", read=True)
    a.title = i.title.text
    try: a.description = re.search(r"<p>        (.+?)</p>", i.description.text).group(1)
    except: a.description = i.description.text
    a.url = i.url.text
    a.pubdate = timestamp(i.pubdate.text)
    articles.append(a)
  return articles

if DEBUG: # read_headlines()
  for a in read_headlines():
    logi(a)
    log(f"age = {(time.time() - a.pubdate) / 3600 :.0f} hrs")
    logo()
  exit()

publishers["The_Decoder"] = Publisher(read_headlines=read_headlines)
