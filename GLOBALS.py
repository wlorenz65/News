import types, threading, urllib.request, urllib.parse, bs4, io, re, os, time, datetime, pickle, json, math, html as html_

DEBUG = (__name__ == "__main__")
nDEBUG = False
class g: pass
if "IS_QPY3" in os.environ: os.chdir("/storage/emulated/0/qpython/Desktop")
g.terminal_width = 120 if os.environ.get("USER") == "wlorenz65" else 70
g.bottle_msg_color = "\033[36m"

g.log_indent_strings = []
g.log_insert_newline = False
g.log_errors = []
g.log_stop_threads = set()
def log(s):
  if g.log_indent_strings: g.log_indent_strings.pop()
  s = str(s)
  i = len(g.log_indent_strings)
  nl = (2 * i + len(s) > 2 * g.terminal_width)
  if nl or g.log_insert_newline: print()
  g.log_insert_newline = nl
  print("  " * i, f"\033[{(95, 33, 36, 32)[i % 4]}m● \033[m", s, g.bottle_msg_color, sep="")
  g.log_indent_strings.append(s)
  t = threading.current_thread()
  if t in g.log_stop_threads:
    g.log_stop_threads.remove(t)
    raise KeyboardInterrupt
def log_(s):
  g.log_insert_newline = True
  log(s)
  g.log_insert_newline = True
def logi(s = None):
  if (s != None): log(s)
  g.log_indent_strings.append(None)
def logo(s = None):
  if s: log(s)
  if g.log_indent_strings: g.log_indent_strings.pop()
def loge(e = None, reset_indent = None):
  if reset_indent == None: reset_indent = (e == None)
  if e: e = e.strip()
  else:
    import traceback
    e = traceback.format_exc().strip()
    if e.endswith("KeyboardInterrupt"): exit(2)
  print("\n\033[91m" + e + g.bottle_msg_color)
  g.log_insert_newline = True
  g.log_errors.append(e)
  with open("4 errors.log", "a+") as f:
    f.seek(0)
    if e not in f.read():
      if f.tell(): f.write("_" * g.terminal_width + "\n")
      for i, s in enumerate(g.log_indent_strings):
        if s: f.write("\n" + "  " * i + s + "\n")
      f.write("\n" + e + "\n")
  if reset_indent: g.log_indent_strings.clear()

class Data(types.SimpleNamespace):
  def __getattr__(a, name):
    if name.startswith('__') and name.endswith('__'): raise AttributeError
    return None

def untag(t): return re.sub(r"</?\w( .+?)?>", "", t)

class Article(Data):
  lang = "de"
  category = "Andere"
  column = "Headlines"
  description = ""
  blocked = {} # dangerous

  @property
  def text(a):
    t = a.title
    if a.description: t += " | " + a.description
    return untag(t)

  def update_blocked(a, update_read=None, to_remove=None, tag=None, click_l=None, click_r=None):
    a.has_reads = a.has_ignores = False
    a.blocked = {}
    already_blocked_patterns = set()
    def search(text, clicked):
      text = "^" + untag(text) + "$"

      # collect matching patterns
      reads, ignores, dontblocks, activeblocks, disabledblocks = [], [], [], [], []
      for l in range(0, len(text) - g.min_block_pattern_len):
        l_in_pattern = (l > 0 and text[l - 1].isalnum() and text[l].isalnum())
        for r in range(l + g.min_block_pattern_len, min(l + g.max_block_pattern_len, len(text)) + 1):
          r_in_pattern = (text[r - 1].isalnum() and r < len(text) and text[r].isalnum())
          patterns = ["*" + text[l:r] + "*"]
          if not l_in_pattern:
            patterns.append(text[l:r] + "*")
          if not r_in_pattern:
            patterns.append("*" + text[l:r])
            if not l_in_pattern: patterns.append(text[l:r])
          for p in patterns:
            p = p.replace("-", " ")
            topic = db.block_patterns_and_topics.get(p)
            if topic:
              match = Data(l=max(1, l), r=min(r, len(text) - 1), pattern=p, topic=topic, tag="u")
              if topic == "Read": reads.append(match); a.has_reads = True
              elif topic == "Ignore": ignores.append(match); a.has_ignores = True
              elif topic == "Don't block": dontblocks.append(match)
              else: match.tag = "s"; activeblocks.append(match)

      # populate dialog remove buttons
      if clicked and to_remove is not None:
        for b in activeblocks + dontblocks:
          if b.l < click_r + 1 and b.r > click_l + 1:
            to_remove.add((b.pattern, b.topic))

      def overlap(b1, b2):
        #        |l---b1---|r
        # |l-----|r   b2   |l-----|r
        if b2.r <= b1.l or b2.l >= b1.r: return False
        return True

      # disable blocks that are overlapped by dontblocks
      for b in activeblocks.copy():
        for d in dontblocks:
          if overlap(d, b):
            disabledblocks.append(b)
            activeblocks.remove(b)
            break

      # sum up blocked topics
      for b in activeblocks:
        if b.pattern not in already_blocked_patterns:
          a.blocked[b.topic] = a.blocked.get(b.topic, 0) + 1
          already_blocked_patterns.add(b.pattern)

      def positions(matches):
        positions = []
        for m in matches:
          positions.append(Data(pos=m.l, tag=m.tag))
          positions.append(Data(pos=m.r, tag="/" + m.tag))
        return sorted(positions, key=lambda p:p.pos, reverse=True)

      def mark(text, matches):
        for p in positions(matches):
          text = text[:p.pos] + "<" + p.tag + ">" + text[p.pos:]
        return text[1:-1]

      return mark(text, reads + ignores + dontblocks + activeblocks + disabledblocks)

    a.title = search(a.title, tag == "H4")
    a.description = search(a.description, tag == "P")

    if update_read and a.read in (None, True, False):
      if a.has_reads: a.read = True
      elif a.has_ignores: a.read = None
      elif a.blocked: a.read = False

    del a.has_reads, a.has_ignores
    if a.read is None and "read" in a.__dict__: del a.read
    if not a.blocked: del a.blocked

class Comment(Data): pass
class Publisher(Data): pass

publishers = {}
categories = ("KI", "Computer", "Andere", "Spam")
columns = ("Links", "Category", "Article", "Headlines")
user_agent = {"User-Agent":"Mozilla/5.0 (Android 8.1.0; Mobile; rv:109.0) Gecko/117.0 Firefox/117.0"}

g.to_archive = []
class DB(Data):
  def savenow(db):
    print("Saving", os.path.abspath("3 News.db"))
    keep_files = False
    if keep_files and not os.path.isdir("archive"): os.mkdir("archive")
    with open("4 archived_Article_objects.log", "a") as f:
      while g.to_archive:
        a = g.to_archive.pop(0)
        if a.offline:
          for fn in os.listdir("offline"):
            if re.match(rf"0*{a.id}(i\d+)?-", fn):
              if keep_files: os.rename("offline/" + fn, "archive/" + fn)
              else: os.remove("offline/" + fn)
          del a.offline
        f.write(repr(a) + "\n")
    with open("3 News.db", "wb") as f: pickle.dump(db, f)
    db.last_save = time.time()
  def autosave(db):
    if time.time() - db.last_save >= 120: db.savenow()
try:
  with open("3 News.db", "rb") as f: db = pickle.load(f)
except FileNotFoundError:
  db = DB()
  db.next_id = 0
  db.known_urls = {}
  db.articles = []
  db.block_patterns_and_topics = {}
db.last_save = time.time()

# parse db.block_patterns_and_topics
g.topics_and_counts = {}
g.min_block_pattern_len = 999
g.max_block_pattern_len = 0
for pattern, topic in db.block_patterns_and_topics.items():
  if topic not in ("Read", "Ignore", "Don't block"):
    g.topics_and_counts[topic] = g.topics_and_counts.get(topic, 0) + 1
  g.min_block_pattern_len = min(g.min_block_pattern_len, len(pattern))
  g.max_block_pattern_len = max(g.max_block_pattern_len, len(pattern))
g.topics_and_counts = dict(sorted(g.topics_and_counts.items()))

def article(id):
  id = int(id)
  for a in db.articles:
    if a.id == id: return a

def timestamp(pubdate, format="%a, %d %b %Y %H:%M:%S %z"):
  dt = datetime.datetime.strptime(pubdate, format)
  ts = datetime.datetime.timestamp(dt)
  return int(ts)

def add_punctuation(s, char="."):
  s = s.strip()
  if s:
    if s[-1] in ",:": s = s[:-1]
    if s and not "." in s[-2:] and not "!" in s[-2:] and not "?" in s[-2:]:
      s += char
  return s

def description(item, end="."):
  t = item.description or item.summary or ""
  if t:
    t = bs4.BeautifulSoup(t.text, "html.parser").text.strip()
    if re.search(r'\w["“”«»]?$', t): t += end
  return t

def next_sibling_tag(tag):
  parent = tag.parent
  while 1:
    tag = tag.next_element
    if not tag or (tag.name and tag.parent is parent):
      return tag

def show_source_of_unknown_tags(article, soup):
  while True:
    for tag in article.find_all():
      if tag.name not in ("h1", "h3", "h5", "p", "ul", "ol",
      "li", "figure", "img", "figcaption", "hr", "br", "a",
      "b", "strong", "i", "em", "del", "sub", "sup", "code",
      "pre", "table", "thead", "tbody", "tfoot", "tr", "th",
      "td", "blockquote", "span", "footer"):
        pre = soup.new_tag("pre")
        pre.attrs = {"class":"error"}
        pre.string = tag.prettify()
        loge(pre.string)
        tag.replace_with(pre)
        break
    else: return

def cleanup(html, base_url):
  soup = bs4.BeautifulSoup(str(html), "html.parser")
  for x in soup.find_all("span"): x.unwrap()
  for tag in soup.find_all():
    comments = [c for c in tag.children if isinstance(c, bs4.Comment)]
    for c in comments: c.extract()
    if tag.name == "p" and tag.attrs == {"class":["credits"]}:
      pass
    elif tag.name == "img":
      tag.attrs = dict(src=urllib.parse.urljoin(base_url, tag["src"]).replace(" ", "\1"))
    elif tag.name == "a" and "href" in tag.attrs:
      tag.attrs = dict(href=urllib.parse.urljoin(base_url, tag["href"]).replace(" ", "\1"))
    elif tag.name in ("tr", "td"):
      tag.attrs.pop("class", None)
      tag.attrs.pop("id", None)
    elif tag.name == "pre":
      if tag.attrs != {"class":["error"]}:
        tag.attrs = {}
    else:
      tag.attrs = {}
  s = str(soup)
  r = 0
  while True:
    l = s.find("<pre", r)
    if l == -1: break
    l += 5
    r = s.index("/pre>", l)
    s = s[:l] + s[l:r].replace(" ", "\1").replace("\t", "\2").replace("\n", "\3") + s[r:]
  s = re.sub(r"\s+", " ", s)
  s = re.sub(r" ?<br/> ?", "<br/>", s)
  s = re.sub(r"(<br/>){2,}", "</p>\n<p>", s)
  s = re.sub(r"<br/></p>", "</p>", s)
  s = s.replace("<code> ", " <code>").replace(" </code>", "</code> ")
  s = s.replace("<td> </td>", "<td>\1</td>").replace("<th> </th>", "<th>\1</th>")
  blocktags = "(article|h\d|p|pre|ol|ul|li|div|iframe|figure|figcaption|footer|blockquote|hr|table|thead|tbody|tfoot|tr|td|th)"
  s = re.sub(f" ?(<{blocktags}( .+?)?>) ?", "\n\\1", s)
  s = re.sub(f" ?(</{blocktags}>) ?", "\\1\n", s)
  s = re.sub(r"<(\w+)></(\1)>", "", s) # <tag></tag>
  s = s.replace("<figure>", "<figure>\n").replace("</figure>", "\n</figure>")
  s = re.split("\n+", s)
  d = 0
  for i in range(len(s)):
    d1 = s[i] in ( "<figure>", "<figcaption>", "<footer>", "<ol>", "<ul>", "<blockquote>", "<table>", "<thead>", "<tbody>", "<tfoot>", "<tr>")
    d -= s[i] in ("</figure>", "</figcaption>", "</footer>", "</ol>", "</ul>", "</blockquote>", "</table>", "</thead>", "</tbody>", "</tfoot>", "</tr>")
    s[i] = d * " " + s[i]
    d += d1
    if not d: s[i] += "\n"
  s = "\n".join(s)
  s = s.replace("\1", " ").replace("\2", "\t").replace("\3", "\n")
  s = re.sub(r"(<a .+?>) ?(<img .+?>) ?(</a>)", r"\1\2\3", s)
  s = s.replace("</figure>\n\n<figure>", "</figure>\n<br/>\n<figure>")
  return s.strip()

if nDEBUG: # cleanup(html, base_url):
  html = """
<article>
<!--1a-->_<!--2a--><!--2b-->_<!--3a--><!--3b--><!--3c-->_<!--1b-->
</article>
"""
  #with open("DEBUG cleanup input.html") as f: html = f.read()
  log_("repr(html) = " + repr(html))
  clean = cleanup(html, "https://debug.me/")
  log_("repr(clean) = " + repr(clean))
  log_("clean = " + clean)
  exit()

def style_article(a):
  with open("templates/Article.html") as f: style = f.read().replace('<html lang="de">', f'<html lang="{a.lang}">')
  a.html = re.sub("(?s)<article>.*</article>", "\1", style).replace("\1", a.html)
  a.html = a.html.replace("{category}", a.category)
  a.html = a.html.replace("{a.id}", str(a.id))
  a.html = a.html.replace("{a.url}", a.url)
  if a.forum_url: a.html = a.html.replace("{a.forum_url}", a.forum_url)

substitute_illegal_filename_chars = str.maketrans(r'<>:"/\|?*', "﹤﹥ː“-⧹⼁？﹡") # prevent ugly ⧸ in Android Firefox address line
def url_to_filename(url):
  fn = re.sub(r"\bhttps?://(www\.)?", "", url)
  fn = fn.translate(substitute_illegal_filename_chars)
  if not re.search(r"\.\w{1,7}$", fn): fn += ".html"
  return fn

g.cache_urls = False
def url_to_soup(url, headers={}):
  if g.cache_urls:
    fn = "DEBUG " + url_to_filename(url)
    if os.path.isfile(fn):
      with open(fn) as f: return bs4.BeautifulSoup(f.read(), "html.parser")
  r = urllib.request.Request(url, headers=headers)
  with urllib.request.urlopen(r) as f: html = f.read().decode("utf-8", errors="ignore")
  soup = bs4.BeautifulSoup(html, "html.parser")
  if g.cache_urls:
    with open(fn, "w") as f: f.write(soup.prettify())
  return soup

def filename(a):
  return f"{a.id:05d}-{url_to_filename(a.url)}"

def download_images_and_store_article(a):
  if not os.path.isdir("offline"): os.mkdir("offline")
  for i, img in enumerate(re.findall(r'(?<=<img src=").+?(?=" ?/>)', a.html)):
    fn = url_to_filename(re.sub(r"^.*/", "", img))
    fn = f"{a.id:05d}i{i}-{fn}"
    log(fn)
    p = os.path.join("offline", fn)
    with urllib.request.urlopen(img.replace(" ", "%20")) as f: data = f.read()
    with open(p, "wb") as f: f.write(data)
    if i == 0:
      a.html = a.html.replace("article {", "article {\n  padding-top: 100vh;")
      a.html = a.html.replace(img, fn + "\" onload=\"document.querySelector('article').style.paddingTop='0'")
    else:
      a.html = a.html.replace(img, fn)
  with open(os.path.join("offline", filename(a)), "w") as f: f.write(a.html)

if nDEBUG: # download_images_and_store_article(a)
  import Heise
  a = Article(url="https://www.heise.de/news/Python-Plaene-fuer-effizienteres-Multithreading-ohne-Global-Interpreter-Lock-9232435.html")
  Heise.read_article(a)
  logi()
  style_article(a)
  download_images_and_store_article(a)
  logo()
  exit()

def decode_contents_and_trim_str(tag):
  if not tag: return ""
  s = tag.decode_contents()
  s = re.sub(r"^(\s|<br/>)+", "", s)
  s = re.sub(r"(\s|<br/>)+$", "", s)
  return s

def figure(*, src=None, srcset=None, link=None, caption=None, credits=None):
  target_width = 600
  target_ext = "webp"
  assert src or srcset
  if srcset:
    if isinstance(srcset, str):
      s = []
      for s_w in srcset.split(","):
        m = re.match(r"\s*(\S+)\s+(\d+)w\s?", s_w)
        s.append((int(m.group(2)), m.group(1)))
      srcset = s
    shortest_distance, chosen_width = 1<<30, None
    for s in srcset:
      d = abs(s[0] - target_width)
      if d < shortest_distance:
        chosen_width, shortest_distance = s[0], d
    srcset = [s for s in srcset if s[0] == chosen_width]
    for s in srcset:
      if re.search(fr"(?i)\.{target_ext}\b", s[1]):
        srcset = [s]; break
    if not link: link = src
    src = srcset[0][1]
  out = "<figure>\n "
  if link: out += f'<a href="{link}">'
  out += f'<img src="{src}" />'
  if link: out += "</a>"
  if caption: out += f'\n <figcaption>{caption.strip()}</figcaption>'
  if credits: out += f'\n <footer>{credits.strip()}</footer>'
  out += "\n</figure>"
  return out

def embed_youtube(video_id, caption="", credits=""):
  caption = re.sub(r"\s+", " ", str(caption)).strip()
  credits = re.sub(r"\s+", " ", str(credits)).strip()
  log(f'embed_youtube({video_id=}, {caption=}, {credits=})')
  video_url = "https://www.youtube.com/watch?v=" + video_id
  oembed_url = "https://www.youtube.com/oembed?url=" + video_url
  try:
    with urllib.request.urlopen(oembed_url) as f: info = json.loads(f.read())
    if not caption: caption = info["title"]
    if not caption.startswith("Video"): caption = "Video: " + caption
    if not credits: credits = info["author_name"]
    out = figure(src=info["thumbnail_url"], link=video_url, caption=caption, credits=credits)
  except Exception:
    out = f'<pre class="error">Video not available: <a href="{video_url}">{video_url}</a></pre>'
  return(bs4.BeautifulSoup(out, "html.parser"))

if nDEBUG: # embed_youtube()
  video_id = "YD_DoKo5Dg8"
  caption = "The Latest Top 10 Is...Sh*t<br/>Hier analysiert der Musiker und Youtuber Rick Beato die Top 10 der Spotify-Charts aus musikalischer Sicht."
  credits = 'Rick Beato'
  print(embed_youtube(video_id, caption, credits))
  exit()

def embed_vimeo(v):
  log(f'embed_vimeo("{v}")')
  a = "https://vimeo.com/" + v
  url = "https://vimeo.com/api/oembed.json?url=" + a
  try:
    with urllib.request.urlopen(url) as f: info = eval(f.read().decode("utf-8"))
    tn = info.get("thumbnail_url")
    if tn:
      tn = tn.replace("\\", "")
      out = f"""
        <figure>
        <img src="{tn}"/>
        <figcaption>
        <p>Video: {info["title"]}</p>
        <p><a href="{a}">{a}</a></p>
        </figcaption>
        </figure>
      """
    else:
      out = f'<p><i>(<a href="{a}">Embedded Vimeo video: {a}</a>)</i></p>'
  except Exception:
    out = f'<pre class="error">Video not available: <a href="{a}">{a}</a></pre>'
  return(bs4.BeautifulSoup(out, "html.parser"))

if nDEBUG: # embed_vimeo()
  print(embed_vimeo("752949495")) # 841462055 752949495
  exit()
