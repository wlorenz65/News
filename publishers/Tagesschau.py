from GLOBALS import *; DEBUG = (__name__ == "__main__")

def read_headlines():
  log("Tagesschau.read_headlines()")
  with urllib.request.urlopen("https://www.tagesschau.de/infoservices/alle-meldungen-100~rdf.xml") as f:
    feed = f.read().decode("utf-8").replace("<?xml ", "<html ").replace("link>", "url>")
  soup = bs4.BeautifulSoup(feed, "html.parser")
  articles = []
  for i in soup.find_all("item"):
    a = Article(publisher="Tagesschau")
    a.title = i.title.text
    a.description = re.sub(r" Von [\w .-]{3,40}\.$", "", i.description.text)
    a.url = i.url.text
    a.pubdate = timestamp(i.pubdate.text)
    if a.title.startswith("Liveblog"): a.title += " (Ticker)"
    articles.append(a)
  return articles

if nDEBUG: # read_headlines()
  for a in read_headlines():
    logi(a)
    log(f"age = {(time.time() - a.pubdate) / 3600 :.0f} hrs")
    logo()
  exit()

def read_article(a):
  logi(f"Tagesschau.read_article({a})")
  soup = url_to_soup(a.url)
  article = soup.article

  authors = []
  ala = article.find("div", class_="authorline__author")
  if ala:
    authors.append(ala.text.replace("Von ", "").replace(", tagesschau.de", "").strip())
    for x in article.find_all("div", class_="copytext-element-wrapper"):
      if x.find("div", class_="authorline"): x.decompose()
  authors.append("Tagesschau.de")

  for x in article.find_all("div", class_="seitenkopf"): x.unwrap()

  h1 = article.find("div", class_="seitenkopf__data")
  headline = h1.find("span", class_="seitenkopf__topline").text.strip() + ": " + h1.find("span", class_="seitenkopf__headline--text").text.strip()
  h1.replace_with(bs4.BeautifulSoup(f"<h1>{headline}</h1>\n", "html.parser"))

  for h2 in article.find_all("h2", class_="meldung__subhead"): h2.name = "h3"

  for x in article.find_all("div", class_="copytext-element-wrapper"):
    if x.find("div", class_="teaser-absatz__teaserinfo"): x.decompose()
  for x in article.find_all("div", class_="meldungsfooter"): x.decompose()

  for picture in article.find_all("picture"):
    img = picture.img
    src = img["src"]
    caption, credits = img["title"].split(" | ")
    picture.replace_with(bs4.BeautifulSoup(f'<figure>\n<img src="{src}" />\n<figcaption>\n<p>{caption}</p>\n<p class="credits">{credits}</p>\n</figcaption>\n</figure>\n', "html.parser"))

  for pw in article.find_all("div", class_="ts-picture__wrapper"):
    for x in pw.find_all("noscript"): x.decompose()
    pw.unwrap()
  for x in article.find_all("div", class_="seitenkopf__media"): x.unwrap()
  for x in article.find_all("div", class_="absatzbild"): x.unwrap()
  for x in article.find_all("div", class_="absatzbild__media"): x.unwrap()
  for x in article.find_all("div", class_="absatzbild__info"): x.unwrap()

  for x in article.find_all("div", class_="infobox"): x.unwrap()
  for h3 in article.find_all("div", class_="infobox__headline--textonly"): h3.name = "h3"



  show_source_of_unknown_tags(article, soup)
  a.html = cleanup(article, a.url)
  aa = f'</p>\n\n<p class="credits"><script>document.write(age({a.pubdate}))</script> by {", ".join(authors)}</p>'
  a.html = a.html.replace("</p>", aa, 1)
  logo()

if DEBUG: # read_article()
  url = "https://www.tagesschau.de/ausland/asien/brennpunkte-naher-osten-100.html"
  a = Article(url=url, pubdate=int(time.time()), id=0)
  g.cache_urls = True
  read_article(a)
  logi()
  style_article(a)
  #download_images_and_store_article(a)
  logo()
  with open("DEBUG read_article output.html", "w") as f: f.write(a.html)
  log(a.html.strip())
  del a.html
  log(a)
  exit()

publishers["Tagesschau"] = Publisher(read_headlines=read_headlines, read_article=read_article)
