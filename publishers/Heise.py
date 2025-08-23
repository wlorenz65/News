from GLOBALS import *; DEBUG = (__name__ == "__main__")

def read_headlines():
  log("Heise.read_headlines()")
  with urllib.request.urlopen("https://www.heise.de/rss/heise.rdf") as f:
    feed = f.read().decode("utf-8").replace("<?xml ", "<html ").replace("link>", "url>")
  soup = bs4.BeautifulSoup(feed, "html.parser")
  articles = []
  for i in soup.find_all("item"):
    a = Article(publisher="Heise", category="Computer", column="Article")
    a.title = i.title.text.replace("\u200b", " ").strip()
    a.description = i.description.text.replace("\u200b", " ").strip()
    a.url = re.sub(r"\?.*", "", i.url.text)
    a.pubdate = timestamp(i.pubdate.text)
    if a.title.startswith("heise+ | "): a.url = "https://archive.li/newest/" + a.url
    if not a.url.startswith("https://www.heise.de/") or "/download/" in a.url or "/bestenlisten/" in a.url: a.column = "Links"
    articles.append(a)
  return articles

if nDEBUG: # read_headlines()
  for a in read_headlines():
    logi(a)
    log(f"age = {(time.time() - a.pubdate) / 3600 :.0f} hrs")
    logo()
  exit()

def read_article(a):
  logi(f'Heise.read_article({a})')
  soup = url_to_soup(a.url + "?seite=all")
  article = soup.h1.parent.parent.parent
  if article.name != "article": raise AssertionError()

  authors = [a.text.strip() for a in article.find_all("li", {"class":"creator__name"})]
  editor = article.find("a", {"class":"redakteurskuerzel__link"})
  if editor: editor = editor.get("title")
  if editor and editor not in authors: authors.append(editor)
  authors.append("Heise.de")

  a.forum_url = urllib.parse.urljoin(a.url, article.find("a", {"class":"a-button"})["href"])

  for x in article.find_all("div", {"class":"a-article-header__service"}): x.decompose()
  for x in article.find_all("div", {"class":"a-article-header__publish-info"}): x.decompose()
  for x in article.find_all("aside", {"class":"article-layout__header-wrbng"}): x.decompose()
  for x in article.find_all("aside", {"class":"affiliate-info"}): x.decompose()
  for x in article.find_all("div", {"class":"ad-label"}): x.decompose()
  for x in article.find_all("a-paternoster", {"class":"a-paternoster-ad"}): x.decompose()
  for x in article.find_all("div", {"class":"ad-mobile-group-1"}): x.decompose()
  for x in article.find_all("div", {"class":"ad ad--inread"}): x.decompose()
  for x in article.find_all("div", {"class":"ad ad--inline"}): x.decompose()
  for x in article.find_all("div", {"class":"a-u-inline"}): x.decompose()
  for x in article.find_all("a-opt-in", {"type":"Preisvergleichinternetservices"}): x.decompose()
  for x in article.find_all("a-opt-in", {"type":"Opinary"}): x.decompose()
  for x in article.find_all("a-collapse"): x.decompose()
  for x in article.find_all("span", {"class":"redakteurskuerzel ISI_IGNORE"}): x.decompose()
  for x in article.find_all("footer", {"class":"article-layout__footer"}): x.decompose()
  for x in article.find_all("section", {"class":"article-sidebar"}): x.decompose()
  for x in article.find_all("figure", {"class":"a-inline-image a-u-inline"}): x.decompose()
  for x in article.find_all("div", {"id":"wtma_teaser_ho_vertrieb_inline_branding"}): x.decompose()
  for x in article.find_all("div", {"class":"a-article-header__label"}): x.decompose()
  for x in article.find_all("div", {"class":"inread-cls-reduc"}): x.decompose()
  for x in article.find_all("div", {"class":"incontent3-cls-reduc"}): x.decompose()
  for x in article.find_all("div", {"class":"a-article-header__podcast-teaser"}): x.decompose()
  for x in article.find_all("a-opt-in", {"type":"Podigee"}): x.decompose()
  for x in article.find_all("div", {"class":"paywall-delimiter"}): x.decompose()
  for x in article.find_all("a-img", {"alt":"Eigenwerbung Fachdienst heise KI PRO"}): x.parent.parent.decompose()
  for x in article.find_all("div", {"class":"ad-mobile-group-3"}): x.decompose()
  for x in article.find_all("a-gift"): x.decompose()
  for x in article.find_all("details", {"class":["notice-banner"]}): x.decompose()

  for x in article.find_all("header", {"class":"a-article-header"}): x.unwrap()
  for x in article.find_all("div", {"class":"article-layout__header-container"}): x.unwrap()
  for x in article.find_all("div", {"class":"article-layout__content-container"}): x.unwrap()
  for x in article.find_all("div", {"class":"article-layout__content article-content"}): x.unwrap()
  for x in article.find_all("div", {"class":"article-layout__content"}): x.unwrap()
  for x in article.find_all("div", {"class":"article-content"}): x.unwrap()
  for x in article.find_all("div", {"class":"article-image__gallery-container"}): x.unwrap()
  for x in article.find_all("a", {"class":"heiseplus-lnk"}): x.unwrap()
  for x in article.find_all("a-code"): x.unwrap()
  for x in article.find_all("section"): x.unwrap()

  for x in article.find_all("div", {"class":["text", ""]}): x.name = "p"
  for x in article.find_all("span", {"class":"tx_caps"}): x.name = "i"
  for x in article.find_all("span", {"class":"tx_smaller"}): x.name = "b"
  for x in article.find_all("span", {"class":"tx_blue"}):
    x.name = "blockquote"
    if x.parent.name == "p": x.parent.unwrap()
  for x in article.find_all("h2"): x.name = "h3"
  for x in article.find_all("h3"):
    if x.next_element.next_element.next_element.name == "h3": x.decompose()

  for lb in article.find_all("a-lightbox"):
    for x in lb.find_all("a-img"): x.decompose()
    caption = lb.find("p", class_="a-caption__text")
    if caption: caption = caption.decode_contents()
    text = lb.find("p", class_="text")
    if text: caption += text.decode_contents()
    credits = lb.find("p", class_="a-caption__source")
    if credits: credits = credits.decode_contents()
    figstr = figure(src=lb["src"], srcset=lb.img.get("srcset"), caption=caption, credits=credits)
    lb.replace_with(bs4.BeautifulSoup(figstr, "html.parser"))

  def read_gallery(url):
    out = []
    for i in range(10):
      log(f'Heise.read_gallery("{url}?bild={i}")')
      soup = url_to_soup(f"{url}?bild={i}")
      if not out: out.append(f"<h3>Bilderstrecke {soup.h1.text}</h3>")
      c = soup.find("div", {"class":"bilderstrecke_nojs container ho"})
      src = c.img['src']
      link = re.sub("^.*_www-heise-de_", "", src)
      for x in c.find_all("div", {"class":"tik4-rich-text"}): x.unwrap()
      for x in c.find_all("div", {"class":"notranslate"}): x.decompose()
      for p in c.find_all("div", {"class":"elementToProof"}): p.name = "p"
      for x in c.find_all("p"):
        if x.parent.name == "p": x.unwrap()
      caption = ""
      for p in c.find_all("p"): caption += p.decode_contents()
      credits = ""
      for p in c.find_all("span", class_="bilderstrecke_nojs_img_source"): credits += p.decode_contents()
      out.append(figure(src=src, link=link, caption=caption, credits=credits))
      if "bild=0" in c.find("a", {"class":"bilderstrecke_nojs_navi_next"})["href"]: break
    else:
      out.append(f'<p><i>(<a href="{url}?bild={i+1}">More images online</a>)</i></p>')
    return bs4.BeautifulSoup("\n\n".join(out), "html.parser")
  for g in article.find_all("a-bilderstrecke", {"class":"gallery"}):
    g.replace_with(read_gallery(urllib.parse.urljoin(a.url, re.sub(r"\?.*", "", g["data-data-url"]))))

  for oi in article.find_all("a-opt-in", {"type":"Youtube"}):
    for x in oi.find_all("figure", {"class":"opt-in__bg-image"}): x.decompose()
    v = re.sub(r"^.*embed/", "", oi.noscript.figure.find("a-iframe")["src"])
    oi.replace_with(embed_youtube(v))

  for oi in article.find_all("a-opt-in", {"type":"Vimeo"}):
    v = re.search(r"\d{7,}", oi.noscript.find("a-iframe")["src"]).group(0)
    oi.replace_with(embed_vimeo(v))

  for oi in article.find_all("a-opt-in", {"type":"Kaltura"}):
    img = oi.figure.find("a-video")
    if img: img = img["preview-image-url"]
    out = []
    if img:
      out.append("<figure>")
      out.append(f'<img src=\"{img}\">')
      out.append("<figcaption>")
    out.append(f'<p><i>(<a href="{a.url}">This article online with embedded Kaltura video</a>)</i></p>')
    if img:
      out.append("</figcaption>")
      out.append("</figure>")
    oi.replace_with(bs4.BeautifulSoup("\n".join(out), "html.parser"))

  for et in article.find_all("embetty-tweet"):
    et.replace_with(bs4.BeautifulSoup(f'<i>(<a href="{a.url}">This article online with embedded X Tweet</a>)</i>', "html.parser"))

  for em in article.find_all("embetty-mastodon"):
    em.replace_with(bs4.BeautifulSoup(f'<i>(<a href="{a.url}">This article online with embedded Mastodon Toot</a>)</i>', "html.parser"))

  for oi in article.find_all("a-opt-in"):
    me = oi.noscript.find("iframe", {"class":"mastodon-embed"})
    if me:
      src = re.sub(r"/embed$", "", me["src"])
      oi.replace_with(bs4.BeautifulSoup(f'<p><i>(<a href="{src}">Embedded Mastodon Toot</a>)</i></p>', "html.parser"))

  for p in article.find_all("p", {"class":["frage", "antwort"]}):
    b = soup.new_tag("b")
    b.string = "Q: " if "frage" in p["class"] else "A: "
    p.insert(0, b)

  for div in article.find_all("div", {"class":["pro", "contra"]}):
    pm = "⊕" if "pro" in div["class"] else "⊖"
    lines = []
    for li in div.find_all("li"): lines.append(pm + " " + li.string); li.decompose()
    for ul in div.find_all("ul"): ul.unwrap()
    if lines: div.replace_with(bs4.BeautifulSoup("<p>" + "<br>".join(lines) + "</p>", "html.parser"))
    else: div.name = "p"

  show_source_of_unknown_tags(article, soup)
  aa = f'</p>\n\n<p class="credits"><script>document.write(age({a.pubdate}))</script> by {", ".join(authors)}</p>'
  a.html = cleanup(article, a.url).replace("</p>", aa, 1)
  logo()

if DEBUG: # read_article()
  url = "https://www.heise.de/news/Betrugsmail-Cyberversicherung-muss-Schaden-nicht-ersetzen-10215212.html"
  a = Article(url=url, category="Computer", pubdate=int(time.time()), id=0)
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

def read_forum(a):
  comments = []
  page = url
  while page:
    print(f'Heise.read_forum("{page}")')
    r = urllib.request.Request(page, headers={"Cookie":"u2uforum_properties=eNqrVoqPL8nMTS0uScwtULIyNLM0NDc2NzU10FGKL85MUbJSqnDzDAtIdikzMizPVKoFAHC%2BDq8%3D_X_3850ad6c1d486b583fbeabb7c5ab6b483eb6ba36"})
    with urllib.request.urlopen(r) as f: html = f.read().decode("utf-8")
    soup = bs4.BeautifulSoup(html, "html.parser")
    ttl = soup.find("ol", {"id":"tree_thread_list"})
    for pe in ttl.find_all("li", {"class":"posting_element"}):
      c = Comment()
      d = 0; p = pe
      while p != ttl: p = p.parent; d += 1
      ps = pe.find("a", {"class":"posting_subject"})
      c.url = ps["href"]
      c.subject = ps.text.strip()
      c.user = pe.find("span", {"class":"tree_thread_list--written_by_user"}).text.strip()
      c.time = pe.time["data-mysql-beautify-date"]
      c.depth = d // 2
      comments.append(c)
    page = soup.find("a", {"class":"older shortcut-d"})
    if page: page = page["href"]
  return Forum(url=url, comments=comments)

if nDEBUG: # read_forum()
  f = read_forum('https://www.heise.de/forum/heise-online/Kommentare/LaMDA-KI-und-Bewusstsein-Blake-Lemoine-wir-muessen-philosophieren/forum-498574/comment/')
  for c in f.comments:
    print()
    print(c)
  print()
  print(len(f.comments), "comments")
  exit()

def read_comment(c):
  print(f'Heise.read_comment("{c.url}")')
  assert not c.html
  with urllib.request.urlopen(c.url) as f: html = f.read().decode("utf-8")
  soup = bs4.BeautifulSoup(html, "html.parser")
  if nDEBUG: open("DEBUG read_comment prettified.html", "w").write(soup.prettify())
  out = []
  for p in soup.find("div", {"class":"bbcode_v1"}).children:
    if isinstance(p, bs4.element.Tag):
      out.append(str(p).replace("<code>", "<pre><code>").replace("</code>", "</code></pre>"))
  c.html = "\n\n".join(out)

if nDEBUG: # read_comment()
  c = Comment(url='https://www.heise.de/forum/heise-online/Kommentare/Fehlersuche-Guard-Clauses-den-Code-auf-Fehler-vorbereiten/Da-lobe-ich-mir-das-gute-alte-assert/posting-42989835/show/')
  read_comment(c)
  print()
  print(c.html)
  exit()

if nDEBUG: # cache forum with comments
  f = read_forum("https://www.heise.de/forum/heise-online/Kommentare/LaMDA-KI-und-Bewusstsein-Blake-Lemoine-wir-muessen-philosophieren/forum-498574/comment/")
  for i, c in enumerate(f.comments):
    print(f"[{i}/{len(f.comments)}] {c.url}")
    while not c.html:
      try:
        read_comment(c)
      except Exception as e:
        print(f"\033[31m  {e}\033[m")
        time.sleep(30)
    time.sleep(3)
  with open("DEBUG forum.pickle", "wb") as p: pickle.dump(f, p)
  exit()

if nDEBUG: # cleanup Heise comment
  with open("DEBUG forum.pickle", "rb") as p: f = pickle.load(p)
  with open("DEBUG forum.html", "w") as out:
    out.write("<style>blockquote {color:darkred; border-top:0; border-bottom:0; border-right:0; border-style:solid; margin-left:0; padding-left:0.5em;}</style>\n\n")
    for i, c in enumerate(f.comments):
      if i == i:
        soup = bs4.BeautifulSoup(c.html, "html.parser")
        for tag in soup.find_all("span", {"class":"italic"}): tag.name = "i"; tag.attrs = {}
        for tag in soup.find_all("span", {"class":"underline"}): tag.name = "u"; tag.attrs = {}
        for tag in soup.find_all("blockquote"): tag.attrs = {}
        html = str(soup)
        #html = html.replace(" </i>", "</i> ").replace("  ", " ")

        html = re.sub(r"\W<br/>", "</p>\n<p>", html)



        out.write(f"<p>[{i}] <b>{c.subject}</b></p>\n\n")
        out.write(html.replace("\n", "\n\n"))
        out.write("\n\n<hr/>\n")
  exit()

publishers["Heise"] = Publisher(read_headlines=read_headlines, read_article=read_article)#, read_forum=read_forum, read_comment=read_comment)
