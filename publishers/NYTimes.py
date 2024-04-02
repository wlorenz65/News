from GLOBALS import *; DEBUG = (__name__ == "__main__")

if nDEBUG: # runs on Linux but fails on Termux
  tstr = 'Sun, 31 Mar 2024 02:14:34 +0000' # German DST switching hour
  print(f"{tstr=}")
  tstruct = time.strptime(tstr, "%a, %d %b %Y %H:%M:%S %z")
  print(f"{tstruct=}")
  tstamp = int(time.mktime(tstruct)) # OverflowError: mktime argument out of range
  print(f"{tstamp=}")
  exit()

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
      try:
        a.pubdate = int(time.mktime(time.strptime(i.pubdate.text, "%a, %d %b %Y %H:%M:%S %z")))
      except:
        log(f"{i.pubdate.text=}")
        log(f'{time.strptime(i.pubdate.text, "%a, %d %b %Y %H:%M:%S %z")=}')
        loge()
        a.pubdate = time.time()
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
