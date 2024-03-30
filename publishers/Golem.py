from GLOBALS import *; DEBUG = (__name__ == "__main__")

def read_headlines():
  log("Golem.read_headlines()")
  with urllib.request.urlopen("https://rss.golem.de/rss.php?feed=RSS2.0") as f:
    feed = f.read().decode("ISO-8859-1").replace("<?xml ", "<html ").replace("link>", "url>")
  soup = bs4.BeautifulSoup(feed, "html.parser")
  articles = []
  for i in soup.find_all("item"):
    a = Article(publisher="Golem", category="Computer", column="Article")
    a.title = i.title.text
    a.description = add_punctuation(re.sub(r" \(<a .*", "", i.description.text))
    a.url = i.url.text
    a.pubdate = int(time.mktime(time.strptime(i.pubdate.text, "%a, %d %b %Y %H:%M:%S %z")))
    articles.append(a)
  return articles

if nDEBUG: # read_headlines()
  for a in read_headlines():
    logi(a)
    log(f"age = {(time.time() - a.pubdate) / 3600 :.0f} hrs")
    logo()
  exit()

def read_article(a):
  logi(f"Golem.read_article({a})")
  out = ""
  img_urls = []
  page = a.url
  while page:
    soup = url_to_soup(page, headers={"Cookie":"golem_consent20=cmp|220101"})
    article = soup.article
    next_page = soup.find("a", {"id":"atoc_next"})
    if next_page: next_page = urllib.parse.urljoin(page, next_page["href"])

    if not out:
      authors = article.find("span", {"class":"authors__name"}).text + ", Golem.de"
      f = soup.find("section", {"id":"comments"})
      if f: a.forum_url = f.a["href"]
    else:
      for h in article.find_all("h1"): h.name = "h3"

    for x in article.find_all("header"): x.unwrap()
    for x in article.find_all("hgroup"): x.unwrap()
    for x in article.find_all("span", {"class":["dh1", "dh2", "implied"]}): x.unwrap()
    for x in article.find_all("script"): x.decompose()
    for x in article.find_all("div", {"class":"authors"}): x.decompose()
    for x in article.find_all("ul", {"class":"social-tools"}): x.decompose()
    for x in article.find_all("div", {"id":"narando-placeholder"}): x.decompose()
    for p in article.find_all("span", {"class":"big-image-sub"}): p.name = "p"
    for p in article.find_all("span", {"class":"big-image-lic"}): p.name = "p"; p.attrs = {"class":"credits"}
    for x in article.find_all("div", {"class":"formatted"}): x.unwrap()
    for x in article.find_all("section"): x.unwrap()
    for x in article.find_all("aside"): x.decompose()
    for x in article.find_all("div", {"class":"toc"}): x.decompose()
    for h in article.find_all("h2"): h.name = "h3"
    for x in article.find_all("div", {"class":"topictags"}): x.decompose()
    for x in article.find_all("figure"):
      if x.find("style"): x.decompose()
    for x in article.find_all("table", {"id":"table-jtoc"}): x.decompose()
    for x in article.find_all("ul", {"class":"social-tools"}): x.decompose()
    for x in article.find_all("ol", {"class":"list-pages"}): x.decompose()
    for x in article.find_all("a"):
      if "golem.de/specials/" in x["href"]: x.unwrap()
    for x in article.find_all("h3"):
      tag = x
      for i in range(2):
        tag = next_sibling_tag(tag)
        if not tag: break
        if tag.name == "h3":
          x.decompose()
          break

    for gallery in article.find_all("a", {"class":"golem-gallery2-nojs"}):
      g = []
      for img in gallery.ul.find_all("img"):
        img_url = img['data-src-full']
        if img_url not in img_urls:
          img_urls.append(img_url)
          caption = img["title"]
          credits = re.search(r"\(Bild: .*\)$", caption)
          if credits: credits = credits.group(0); caption = caption[:-(len(credits) + 1)]
          g.append("<figure>")
          g.append(f"""<a href="{img['data-src-full']}"><img src="{img['data-src']}"/></a>""")
          if caption or credits:
            g.append("<figcaption>")
            if caption: g.append(f"<p>{caption}</p>")
            if credits: g.append(f'<p class="credits">{credits}</p>')
            g.append("</figcaption>")
          g.append("</figure>")
      gallery.replace_with(bs4.BeautifulSoup("\n".join(g), "html.parser"))

    for td in article.find_all("div", {"class":"golem_tablediv"}):
      for tt in td.find_all("div", {"class":"golem_tabletitle"}):
        td.name = "figure"
        tt.name = "p"
        tt.wrap(soup.new_tag("figcaption"))

    for inline in article.find_all("div", {"class":"htmlinline"}):
      if inline.find("iframe", {"class":"survey-frame"}):
        survey = f'<p><i>(<a href="{a.url}">This article online with embedded Golem survey</a>)</i></p>'
        inline.replace_with(bs4.BeautifulSoup(survey, "html.parser"))

    for gvideo in article.find_all("figure", {"class":"gvideofig"}):
      v = re.sub("gvideo_", "", gvideo["id"])
      v = f'<p><i>(<a href="https://video.golem.de/audio-video/{v}/">Watch embedded Golem Video online</a>)</i></p>'
      gvideo.replace_with(bs4.BeautifulSoup(v, "html.parser"))

    for frame in article.find_all("iframe", {"title":"YouTube video player"}):
      if frame.parent.name in ("div", "p"): frame.parent.unwrap()
      v = re.search(r"(?<=/embed/)[\w-]{11,14}", frame["src"]).group()
      frame.replace_with(embed_youtube(v))

    show_source_of_unknown_tags(article, soup)
    out += cleanup(article, a.url)
    page = next_page
  out = out.replace("\n</article><article>\n", "")
  aa = f'</p>\n\n<p class="credits"><script>document.write(age({a.pubdate}))</script> by {authors}</p>'
  a.html = out.replace("</p>", aa, 1)
  logo()

if DEBUG: # read_article()
  url = "https://www.golem.de/news/mintboard-bastler-baut-bluetooth-tastatur-in-bonbondose-2402-181881.html"
  a = Article(url=url, category="Computer", pubdate=int(time.time()))
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

publishers["Golem"] = Publisher(read_headlines=read_headlines, read_article=read_article)
