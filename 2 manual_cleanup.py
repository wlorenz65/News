from GLOBALS import *; DEBUG = (__name__ == "__main__")
log(f"len(db.articles) = {len(db.articles)}")
log(f"len(db.block_patterns_and_topics) = {len(db.block_patterns_and_topics)}")

# ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# Move DerStandard links to article

if nDEBUG:
  for a in db.articles:
    if a.column == "Links" and a.publisher == "DerStandard":
      a.column = "Article"
      log(a)
  #db.savenow()
  exit()

# ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# Archive headlines with at least 3 blocking topics or 2 blocking patterns of the same topic

if nDEBUG:
  for a in db.articles.copy():
    if a.column == "Headlines":
      a.update_blocked(True)
      if a.blocked and (len(a.blocked) >= 3 or max(a.blocked.values()) >= 2):
        log(a)
        g.to_archive.append(a)
        db.articles.remove(a)
  log(f"{len(g.to_archive)} headlines removed and archived")
  #db.savenow()
  exit()

# ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# Call update_blocked() on all articles (when lots of new blocking patterns were added)

if nDEBUG:
  for a in db.articles:
    old_title, old_description = a.title, a.description
    a.update_blocked(True)
    if a.title != old_title: print("\n" + old_title + "\n" + a.title)
    if a.description != old_description: print("\n" + old_description + "\n" + a.description)
  #db.savenow()
  exit()

# ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# Find double patterns with and without *stars*

if nDEBUG:
  log("Finding double patterns with and without *stars*")
  for pattern in db.block_patterns_and_topics:
    if pattern.startswith("*") and pattern[1:] in db.block_patterns_and_topics \
    or pattern.endswith("*") and pattern[:-1] in db.block_patterns_and_topics:
      print(pattern)
  exit()

# ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# Save db.block_patterns_and_topics

if nDEBUG:
  if not db.block_patterns_and_topics: log("Error: db.block_patterns_and_topics is empty!"); exit(1)
  logi(f'saving {len(db.block_patterns_and_topics)} entries to file "2 restore db.block_patterns_and_topics.py"')
  import pprint
  with open("2 restore db.block_patterns_and_topics.py", "w") as f:
    f.write(f"""\
from GLOBALS import *; DEBUG = (__name__ == "__main__")

print(f"There were {{len(db.block_patterns_and_topics)}} entries in db.block_patterns_and_topics")

db.block_patterns_and_topics = {{
{pprint.pformat(db.block_patterns_and_topics, indent=0)[1:-1]},
}}

print(f" Restoring {{len(db.block_patterns_and_topics)}} entries to db.block_patterns_and_topics")
if "y" in input(f'\\nWrite file {{os.path.abspath("3 News.db")}} [yN]? '):
  db.savenow(); print("Ok.")
else: print("Not written.")
""")
  exit()

# ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# Translate headlines

if nDEBUG:
  log("Translating headlines")
  import online
  for a in db.articles:
    if a.category == "Other" and a.column == "Headlines":
      log(a.text)
      a.title, a.description = online.gt.translate(a.title + "\n\n" + a.description).split("\n\n")
      logo(a.text)
  #db.savenow()
  exit()

# ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# Translate articles by adding Google Translate to their URLs

if nDEBUG:
  log("Translating articles")
  import online
  for a in db.articles:
    if a.lang != "de":
      old_url = a.url
      a.url = online.translate_url(a)
      if a.url == old_url: print(a.url)
      else: logi(old_url); logo(a.url)
  #db.savenow()
  exit()

# ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# Move XKCD links to Computer

if nDEBUG:
  log("Moving XKCD links to Computer")
  for a in db.articles:
    if a.url.startswith("https://xkcd.com/"):
      log(a.url)
      a.category = "Computer"
  #db.savenow()
  exit()
