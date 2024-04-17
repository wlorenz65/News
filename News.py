from GLOBALS import *; DEBUG = (__name__ == "__main__")
import bottle, online, atexit

def build_table():
  t = "<table>\n<tr class='head'>"
  for col in columns: t += f"<td>{col}</td>"
  t += "</tr>\n"
  for cat in categories:
    t += "<tr>"
    for col in columns:
      t += "<td>"
      if col == "Category":
        t += cat
      else:
        total = ready = 0
        for a in db.articles:
          if a.column == col and a.category == cat:
            total += 1
            ready += 1
            ready -= (col == "Article" and not a.offline)
            ready -= (col == "Forum")
        if total:
          if ready < total: ready = f"{ready} / {total}"
          t += f"<a href='/{col}/{cat}'><button>{ready}</button></a>"
        else:
          t += "-"
      t += "</td>"
    t += "</tr>\n"
  t += "</table>"
  return t

@bottle.route("/")
def index():
  with open("templates/index.html") as f: style = f.read()
  html = re.sub(r"(?s)<table>.*</table>", build_table(), style)
  if online.thread:
    html = html.replace("<!--refresh-->", "<meta http-equiv='refresh' content='2'>")
    buttons = "<p>\n<a href='/Stop'><button>Stop updating</button></a>\n</p>\n"
    progress = "<h3>Progress:</h3>\n"
    for s in g.log_indent_strings:
      if s: progress += "<p>" + html_.escape(s) + "</p>\n"
  else:
    buttons = "<p>\n<a href='/Update'><button>Update</button></a>\n</p>\n"
    progress = ""
  if g.log_errors:
    e = f'<pre class="error">{html_.escape(g.log_errors[-1])}</pre>'
    errors = f'<h3>Last of {len(g.log_errors)} new errors in "4 errors.log":</h3>\n{e}\n'
  else:
    errors = ""
  html = re.sub(r"(?s)<!--buttons-->.*<!--/buttons-->", "\1", html).replace("\1", buttons)
  html = re.sub(r"(?s)<!--errors-->.*<!--/errors-->", "\1", html).replace("\1", errors)
  html = re.sub(r"(?s)<!--progress-->.*<!--/progress-->", "\1", html).replace("\1", progress)
  return html

@bottle.route("/Update")
def Update():
  if not online.thread:
    online.thread = threading.Thread(target=online.Update)
    online.thread.start()
  bottle.redirect("/")

@bottle.route("/Stop")
def Stop():
  g.log_stop_threads.add(online.thread)
  online.thread = None
  bottle.redirect("/")

def translate_url(a):
  if a.lang == "de" and a.category != "Other": return a.url
  for x in "translate.goog", "archive.li", "techcrunch.com", "xkcd.com", "ansys.com":
    if x in a.url: return a.url
  slash = a.url.index("/", 8)
  return a.url[:slash].replace(".", "-") + ".translate.goog" + a.url[slash:] + "?_x_tr_sl=en&_x_tr_tl=de&_x_tr_hl=de&_x_tr_pto=wapp"

def Links_item(a): return f"""\
<hr>
<a onclick="read({a.id})" href="{translate_url(a).replace('archive.li', 'archive.ph')}">
 <h4>{a.title}</h4>
 <p>{a.description}</p>
</a>"""

@bottle.route("/Links/<category>")
def Links(category):
  with open("templates/Links.html") as f: style = f.read()
  out = [f"<article>\n\n<h1>Links in {category}</h1>"]
  id_ms = []
  for a in reversed(db.articles): # stapel abarbeiten
    if a.column == "Links" and a.category == category:
      if len(out) - 1 == 10: break
      out.append(Links_item(a))
      id_ms.append(f"{a.id}:0")
  else:
    style = re.sub(r".*submit\('Links'\).*", "", style)
  out.append("</article>")
  html = re.sub("(?s)<article>.*</article>", "\1", style).replace("\1", "\n\n".join(out))
  html = re.sub("(?<=id_ms = {).*(?=})", ",".join(id_ms), html)
  html = html.replace("{category}", category)
  return html

@bottle.route("/submit_Links/<category>")
def submit_Links(category):
  q = bottle.request.query
  for id, s in eval(q.id_s).items():
    a = article(id)
    if s: a.read = s
    g.to_archive.append(a)
    db.articles.remove(a)
  db.autosave()
  if q.next == "Links": return bottle.redirect("/Links/" + category)
  bottle.redirect("/")

def Headline_item(a):
  pb = ""
  if a.read == False:
    pb += f" ({a.publisher}"
    if a.blocked: pb += ", blocked: " + ", ".join(a.blocked)
    pb += ")"
  class_ = "read" if a.read else "block" if a.read is False else "ignore"
  return f"""\
<tr id="{a.id}" class="{class_}" onclick="onClick()"><th></th><td>
 <h4>{a.title}</h4>
 <p>{a.description}{pb}</p>
</td></tr>
"""

@bottle.route("/Headlines/<category>")
def Headlines(category):
  with open("templates/Headlines.html") as f: style = f.read()
  out = ["<table>"]
  for a in db.articles:
    if a.column == "Headlines" and a.category == category:
      if len(out) - 1 == 50: break
      out.append(Headline_item(a))
  else:
    style = re.sub(r".*submit\('Headlines'\).*", "", style)
  out.append("</table>")
  html = style.replace("{category}", category)
  html = re.sub("(?s)<table>.*</table>", "\1", html).replace("\1", "\n\n".join(out))
  return html

def remove_buttons(out, a, tag, l, r):
  to_remove = set()
  a.update_blocked(True, to_remove, tag, l, r)
  if not to_remove: return
  out.append('<form method="dialog">')
  for wt in to_remove:
    def quotinghell(w):
      w = w.replace("\\", "(backslash)")
      w = w.replace("'", "(singlequote)")
      w = w.replace('"', "(doublequotes)")
      return "'" + w + "'"
    out.append(f'<p align="center"><button value="remove(id={a.id},pattern={quotinghell(wt[0])})">Remove</button> ')
    color, us = ("green", "u") if wt[1] in ("Read", "Ignore", "Don't block") else ("red", "s")
    pattern = wt[0]; l_star = r_star = ""
    if pattern.startswith("*"): l_star = "*"; pattern = pattern[1:]
    if pattern.endswith("*"): r_star = "*"; pattern = pattern[:-1]
    out.append(f'<span style="color:{color}">{l_star}<{us}>{pattern}</{us}>{r_star}</span>')
    out.append(f' from {wt[1]}</p>')
  out.append('</form>')
  out.append('<hr>')

def trim_buttons(out):
  out.append("""
    <p align="center">
    <button onclick="select(-5, 0)">Word &lt;&lt;</button>
    <button onclick="select(-1, 0)">&nbsp; &lt; &nbsp;</button>
    <button onclick="select(+1, 0)">&nbsp; &gt; &nbsp;</button>
    <button onclick="star(-1)">*star</button>
    <button onclick="star(+1)">star*</button>
    <button onclick="select(0, -1)">&nbsp; &lt; &nbsp;</button>
    <button onclick="select(0, +1)">&nbsp; &gt; &nbsp;</button>
    <button onclick="select(0, +5)">&gt;&gt; Word</button>
    </p>
  """)

def allow_buttons(out):
  out.append("""
    <p align="center">
    <button value="Read"><u style="color:green">Read</u></button>
    <button value="Ignore"><u style="color:green">Ignore</u></button>
    <button value="Don't block"><u style="color:green">Don't block</u> overlaps</button>
    <button value="">Cancel</button>
    </p>
  """)

def block_buttons(out):
  out.append('<p align="center" style="line-height:2.2">')
  for topic, count in g.topics_and_counts.items():
    font_size = 0.4 + math.log10(count + 1) / math.log10(2500)
    out.append(f'<button value="{topic}" style="font-size:{font_size}rem">{topic}</button>')
  out.append("</p>")

def block_dialog(a, tag, text, pos):
  text = text.replace("-", " ")
  l = max(0, pos - 2)
  r = min(pos + 2, len(text))
  while l > 0 and text[l - 1].isalnum(): l -= 1
  while r < len(text) and text[r].isalnum(): r += 1
  l_star = ""
  r_star = "" if r - l < 7 else "*"
  out = []
  remove_buttons(out, a, tag, l, r)
  out.append('<h3 align="center"></h3>')
  trim_buttons(out)
  out.append('<form method="dialog">')
  allow_buttons(out)
  block_buttons(out)
  out.append('</form>')
  return f"block_dialog({a.id},{repr('^' + text + '$')},{l + 1},{r + 1},{repr(l_star)},{repr(r_star)}," + repr("".join(out)) + ")"

@bottle.route("/click(id=<id:int>,tag='<tag:path>',pos=<pos:int>)")
def click(id, tag, pos):
  a = article(id)
  text = untag(a.title) if tag == "H4" else untag(a.description)
  if a.read == None or tag not in ("H4", "P") or pos >= len(text):
    a.read = {None:True, True:False, False:None}[a.read]
    return f"Headline_item({a.id},{repr(Headline_item(a))})"
  return block_dialog(a, tag, text, pos)

@bottle.route("/block(id=<id:int>,pattern='<pattern:path>',topic='<topic:path>')")
def block(id, pattern, topic):
  a = article(id)
  db.block_patterns_and_topics[pattern] = topic
  g.min_block_pattern_len = min(g.min_block_pattern_len, len(pattern))
  g.max_block_pattern_len = max(g.max_block_pattern_len, len(pattern))
  a.update_blocked(True)
  return f"Headline_item({a.id},{repr(Headline_item(a))})"

@bottle.route("/remove(id=<id:int>,pattern='<pattern:path>')")
def remove(id, pattern):
  a = article(id)
  pattern = pattern.replace("(backslash)", "\\")
  pattern = pattern.replace("(singlequote)", "'")
  pattern = pattern.replace("(doublequotes)", '"')
  del db.block_patterns_and_topics[pattern]
  a.update_blocked(True)
  return f"Headline_item({a.id},{repr(Headline_item(a))})"

@bottle.route("/submit_Headlines/<category>")
def submit_Headlines(category):
  q = bottle.request.query
  for id in q.ids.split(","):
    a = article(id)
    if a.read:
      a.column = "Article" if publishers[a.publisher].read_article else "Links"
    else:
      g.to_archive.append(a)
      db.articles.remove(a)
  db.autosave()
  if q.next == "Headlines": return bottle.redirect("/Headlines/" + category)
  bottle.redirect("/")

read_article_start = None

@bottle.route("/Article/<category>")
def Article(category):
  global read_article_start
  a0 = None
  flags = ["hide_next_article"]
  for a in db.articles:
    if a.column == "Article" and a.category == category and a.offline:
      if os.path.isfile("offline/" + filename(a)):
        if not a0: a0 = a
        else: flags = []; break
      else: a.offline = False
  if a0:
    if publishers[a0.publisher].read_forum:
      if category == "KI.de" or category == "AI.en" : flags.append("check_read_forum")
    else: flags.append("hide_read_forum")
    if not a0.forum_url: flags.append("hide_forum_url")
    read_article_start = time.time()
    return bottle.redirect("/" + filename(a0) + ("?" + "&".join(reversed(flags)) if flags else ""))
  bottle.redirect("/")

@bottle.route("/submit_Article/<category>")
def submit_Article(category):
  global read_article_start
  q = bottle.request.query
  a = article(q.id)
  if read_article_start:
    a.read = round(time.time() - read_article_start)
    read_article_start = None
  if q.read_forum:
    a.column = "Forum"
  else:
    g.to_archive.append(a)
    db.articles.remove(a)
  db.autosave()
  if q.next == "Article": return Article(category)
  bottle.redirect("/")

@bottle.route("/<filename:path>")
def get(filename):
  return bottle.static_file(filename, root="offline")

atexit.register(lambda: db.savenow())
print(g.bottle_msg_color)
bottle.run(host='localhost', port=8080)
