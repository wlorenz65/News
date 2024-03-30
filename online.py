from GLOBALS import *; DEBUG = (__name__ == "__main__")

from publishers import (
  The_Decoder, Heise, Golem, DerStandard, Tagesschau,
  ORF, Spiegel, Merkur, FAZ, Zeit, Welt, Focus,
  ExtremNews, Press24, XKCD, IEEE_Spectrum, TechXplore,
  TechCrunch, Wired, NYTimes
)

import deep_translator
gt = deep_translator.GoogleTranslator(source="auto", target="de")

def is_KI(a):
  if re.search(r"\bKI\b|OpenAI|Chat-?GPT|Mid[Jj]ourney|Dall.E|Robot|ünstliche.+ntelligen|\bBard\b|\bLlama\b|\bGemini\b", a.text):
    return True

def read_new_headlines():
  dbg = []
  for pname, p in publishers.items():
    try:
      for a in reversed(p.read_headlines()):
        if a.url not in db.known_urls:
          dbg.append(f"\n{a=}")
          if a.publisher != pname: raise ValueError(f"{a.publisher=} != {pname=}")
          if a.column not in columns: raise ValueError(f"{a.column=} not in {columns=}")
          if a.category not in categories: raise ValueError(f"{a.category=} not in {categories=}")
          if a.lang != "de":
            a.title, a.description = gt.translate(a.title + "\n\n" + a.description).split("\n\n")
            dbg.append(f"{a.lang=} => translating headline")
          t_old, d_old = a.title, a.description
          cleanup(a)
          if a.title != t_old: dbg.append(f"cleanup(a) => {a.title=}")
          if a.description != d_old: dbg.append(f"cleanup(a) => {a.description=}")
          a.update_blocked("read" not in a.__dict__)
          dbg.append(f"a.update_blocked(update_read={('read' not in a.__dict__)=}) => {a.blocked=}, {a.read=}")
          if a.read == False:
            a.category = "Spam"
            a.column = "Headlines"
            dbg.append(f"{a.read=} => {a.category=}, {a.column=}")
          elif is_KI(a):
            a.category = "KI.de" if a.lang == "de" else "AI.en"
            if a.read == None: a.read = True
            dbg.append(f"is_KI(a) => {a.category=}, {a.read=}")
          if a.read and a.column == "Headlines":
            a.column = "Article" if publishers[a.publisher].read_article else "Links"
            dbg.append(f"(a.read and a.column == 'Headlines') => {a.column=}")
          if a.publisher == "Press24" and a.read != False: a.title = re.sub(r" \([\w .!-:]{2,}\)$", "", a.title)
          a.id = db.next_id; db.next_id += 1
          db.articles.append(a)
        db.known_urls[a.url] = time.time()
    except: loge()
  #with open("DEBUG read_new_headlines.log", "w") as f: f.write("\n".join(dbg))

def cleanup(a):
  def norm_chars(t):
    t = t.replace("\xAD", "")
    t = re.sub("[\x00-\x20\xA0\u2000-\u200F\u202F\u205F\u3000\uFEFF]+", " ", t)
    t = re.sub("[\u2010-\u2015\u2212\u2500\u2501\u2574\u2576\u2578\u257A\uFE63\uFF0D]", "-", t)
    t = re.sub("[\xAB\xBB\u201C\u201D\u201E\u201F\u2E42\u301D\u301E\u301F\uFF02]", '"', t)
    t = re.sub("[\x60\u02BC\u02CB\u07F4\u07F5\u2018-\u201B\u2039\u203A\u275B\u275C\u275F\u276E\u276F\uFF40]", "'", t)
    return t.strip().replace(" - ", " – ")
  a.title = norm_chars(a.title).replace("?:", "?").replace("!:", "!").replace(" :", ":").replace(" .", ".").replace(" ,", ",")
  a.description = norm_chars(a.description)
  if a.description.endswith((",", ":", "-")):
    a.description = a.description[:-1].rstrip()
    if a.description and a.description[-1].isalnum():
      a.description += "…"

def remove_outdated_urls():
  for url, time_last_seen in db.known_urls.copy().items():
    age = time.time() - time_last_seen
    if age >= 10 * 86400:
      del db.known_urls[url]

def download_new_articles():
  for _ in range(2):
    for a in db.articles.copy():
      if a.column == "Article" and not a.offline:
        try:
          publishers[a.publisher].read_article(a)
          if a.column != "Article": continue
          logi()
          style_article(a)
          download_images_and_store_article(a)
          a.offline = True
          time.sleep(3)
          logo()
        except: loge()
        finally:
          if a.html: del a.html

def move_buggy_articles_to_links():
  for a in db.articles:
    if a.column == "Article" and not a.offline:
      a.column = "Links"

def update_blocked_patterns():
  logi("Updating blocked patterns")
  try:
    for ai, a in enumerate(db.articles.copy()):
      log(f"{ai}/{len(db.articles)}")
      print("\033[1A", end="", flush=True)
      a.update_blocked(True)
  except: loge()
  finally: logo()

thread = None

def Update():
  global thread
  g.log_errors.clear()
  read_new_headlines()
  remove_outdated_urls()
  download_new_articles()
  move_buggy_articles_to_links()
  #update_blocked_patterns()
  db.savenow()
  log_("Update finished.")
  g.log_stop_threads.discard(thread)
  thread = None
