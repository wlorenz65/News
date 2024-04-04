from GLOBALS import *; DEBUG = (__name__ == "__main__")

def read_headlines():
  log("TechCrunch.read_headlines()")
  with urllib.request.urlopen("https://techcrunch.com/feed/") as f:
    feed = f.read().decode("utf-8").replace("<?xml ", "<html ").replace("link>", "url>")
  soup = bs4.BeautifulSoup(feed, "html.parser")
  articles = []
  for i in soup.find_all("item"):
    a = Article(publisher="TechCrunch", lang="en", category="Other")
    a.title = i.title.text
    a.description = re.search(r"<p>(.+?)</p>", i.description.text).group(1).replace(" [&#8230;]", "…")
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

# nix archive.today + https://techcrunch.com/2024/01/06/data-ownership-is-leading-the-next-tech-megacycle/?guccounter=1

publishers["TechCrunch"] = Publisher(read_headlines=read_headlines)
