from GLOBALS import *; DEBUG = (__name__ == "__main__")

def read_headlines():
  logi("ORF.read_headlines()")
  try:
    articles = []
    for ressort in ("science", "help", "oesterreich"):
      log(ressort)
      with urllib.request.urlopen(f"https://rss.orf.at/{ressort}.xml") as f:
        feed = f.read().decode("utf-8").replace("<?xml ", "<html ").replace("link>", "url>")
      soup = bs4.BeautifulSoup(feed, "html.parser")
      for i in soup.find_all("item"):
        a = Article(publisher="ORF")
        a.title = i.title.text
        a.description = re.sub(r"\s+", " ", i.description.text).strip() if i.description else ""
        a.url = i.url.text
        a.pubdate = int(time.mktime(time.strptime(i.pubdate.text, "%a, %d %b %Y %H:%M:%S %z")))
        articles.append(a)
    return articles
  finally: logo()

if DEBUG: # read_headlines()
  for a in read_headlines():
    logi(a)
    log(f"age = {(time.time() - a.pubdate) / 3600 :.0f} hrs")
    logo()
  exit()

publishers["ORF"] = Publisher(read_headlines=read_headlines)
