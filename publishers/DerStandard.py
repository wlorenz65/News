from GLOBALS import *; DEBUG = (__name__ == "__main__")

def read_headlines():
  log("DerStandard.read_headlines()")
  articles = []
  urls = set()
  for web in ("/web", ""):
    with urllib.request.urlopen("https://www.derstandard.at/rss" + web) as f:
      feed = f.read().decode("utf-8").replace("<?xml ", "<html ").replace("link>", "url>")
    soup = bs4.BeautifulSoup(feed, "html.parser")
    for i in soup.find_all("item"):
      a = Article(publisher="DerStandard")
      a.category = "Computer" if web else "Andere"
      a.title = i.title.text
      a.description = add_punctuation(re.sub(r".*>", "", i.description.text), ".")
      a.url = re.sub(r"\?.*", "", i.url.text)
      a.pubdate = timestamp(i.pubdate.text)
      a.column = "Article" if web else "Headlines"
      if "/jetzt/livebericht/" in a.url: a.title += " (Ticker)"
      if a.url not in urls:
        articles.append(a)
        urls.add(a.url)
  return articles

if nDEBUG: # read_headlines()
  for a in read_headlines():
    logi(a)
    log(f"age = {(time.time() - a.pubdate) / 3600 :.0f} hrs")
    logo()
  exit()

def read_article(a):
  logi(f'DerStandard.read_article({a})')
  soup = url_to_soup(a.url, headers={"Cookie":"DSGVO_ZUSAGE_V1=true"})
  article = soup.article

  authors = []
  ao = article.find("div", class_="article-origins")
  if ao:
    for s in ao.find_all("span"): authors.append(s.text.strip())
  authors.append("DerStandard.at")

  for x in article.find_all("div"):
    if not x.attrs: x.unwrap()
  for x in article.find_all("div", {"class":["article-header", "article-body"]}): x.unwrap()
  for x in article.find_all("header"): x.unwrap()
  for x in article.find_all(("h2", "source", "button")): x.decompose()
  for x in article.find_all("div", {"class":["article-byline", "article-meta"]}): x.decompose()
  for x in article.find_all("div", {"data-section-type":"image"}): x.unwrap()
  for x in article.find_all("ad-container"): x.decompose()
  for x in article.find_all("aside"): x.decompose()
  for x in article.find_all("nav"): x.decompose()
  for x in article.find_all("div", {"data-section-type":"newsletter"}): x.decompose()
  for x in article.find_all("script", "js-embed-template"):
    x.replace_with(bs4.BeautifulSoup(html_.unescape(x.text), "html.parser"))

  lead_figure = ""
  for f in article.find_all("figure", {"data-type":"image"}):
    img = f.img
    src = img.get("src") or img.get("data-lazy-src") or img.get("data-fullscreen-src")
    caption = f.figcaption
    if caption: caption = caption.decode_contents()
    credits = f.footer
    if credits: credits = credits.decode_contents()
    figstr = figure(src=src, caption=caption, credits=credits)
    if not lead_figure:
      lead_figure = figstr
      f.decompose()
    else:
      f.replace_with(bs4.BeautifulSoup(figstr, "html.parser"))

  for video in article.find_all("div", {"data-section-type":"video"}):
    iframe = video.iframe
    if iframe:
      caption = decode_contents_and_trim_str(video.figcaption)
      credits = decode_contents_and_trim_str(video.footer)
      src = iframe.get("src", "")
      if "youtube.com" in src:
        video_id = re.search(r"/embed/([a-zA-Z0-9_-]{11})\b", src).group(1)
        video.replace_with(embed_youtube(video_id, caption, credits))

  for x in article.find_all("div", "js-embed-container"): x.unwrap()
  for x in article.find_all("figure", {"data-type":"html"}): x.unwrap()
  for x in article.find_all("div", {"data-section-type":"html"}): x.unwrap()
  for x in article.find_all("script", {"src":"https://platform.twitter.com/widgets.js"}): x.decompose()
  for x in article.find_all("script", {"class":"podigee-podcast-player"}): x.decompose()
  for x in article.find_all("iframe"):
    if "open.spotify.com" in x.get("src", ""): x.decompose()
  for x in article.find_all("div", {"data-section-type":"quote"}): x.unwrap()
  for x in article.find_all("figure", {"data-type":"quote"}): x.unwrap()

  show_source_of_unknown_tags(article, soup)
  a.html = cleanup(article, a.url)

  r = a.html.find("</p>")
  if r > 0 and a.html[r - 1].isalnum():
    a.html = a.html[:r] + "." + a.html[r:]

  r = a.html.rfind(")</p>")
  if r != -1:
    r += 1
    l = a.html[:r].rfind("(")
    if l != -1:
      a0 = re.sub(r",? ?\d{1,2}\.\d{1,2}\.20\d\d ?", "", a.html[l:r])[1:-1]
      if not a0.startswith(authors[0]): authors.insert(0, a0)
      if l and a.html[l - 1] == " ": l -= 1
      a.html = a.html[:l] + a.html[r:]
  aa = f'<p class="credits"><script>document.write(age({a.pubdate}))</script> by {", ".join(authors)}</p>'
  a.html = a.html.replace("</p>", f"</p>\n\n{aa}\n\n{lead_figure}", 1)

  logo()

# video ohne titel: https://www.derstandard.at/story/3000000213677/warum-kaufte-aurelios-kiamul-1350-liter-wein-im-antiken-aegypten

# videoartikel: https://www.derstandard.at/story/3000000214634/deutsche-polizei-beklagt-unklare-regelungen-bei-cannabis-im-verkehr

# forumsfragen:
# https://www.derstandard.at/story/3000000214581/umgang-mit-legasthenie-im-erwachsenenalter
# https://www.derstandard.at/story/3000000214579/staedte-oder-orte-die-ich-schon-immer-mal-besuchen-wollte-aber
# https://www.derstandard.at/story/3000000214586/projektbasierte-schulsysteme
# https://www.derstandard.at/story/3000000214588/e-mountain-bikes-radl-fuer-schwachmaten-oder-perfekte-ergaenzung-zum-klassischen-mtb

# doppelte autorennamen: https://www.derstandard.at/story/3000000213355/falschinformationen-zum-dritten-weltkrieg-tiktok
# https://www.derstandard.at/story/3000000214249/tischuhren-erleben-ein-zartes-revival

# leerzeichen im datum: https://www.derstandard.at/story/3000000213987/putin-ordnet-russische-variante-von-steam-an
# dailymotion video: https://www.derstandard.at/story/3000000214097/grenznahe-kontrollen-nach-cannabislegalisierung-in-deutschland

if DEBUG: # read_article()
  url = "https://www.derstandard.at/story/3000000225300/leopard-2-a-rc-30-ist-der-neue-roboterpanzer-aus-europa"
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

publishers["DerStandard"] = Publisher(read_headlines=read_headlines, read_article=read_article)
