from GLOBALS import *; DEBUG = (__name__ == "__main__")
log(f"{len(db.articles)=}")
log(f"{len(db.block_patterns_and_topics)=}")

# ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# Archive Spam headlines

if nDEBUG:
  for a in db.articles.copy():
    if a.category == "Spam" and a.column == "Headlines":
      g.to_archive.append(a)
      db.articles.remove(a)
  #db.savenow()
  exit()

# ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# Add/remove blocking patterns

if nDEBUG:
  b = db.block_patterns_and_topics
  b[""] = ""
  #db.savenow()
  exit()

# ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# Archive headlines with at least 3 blocking topics or 2 blocking patterns of the same topic

if nDEBUG:
  for a in db.articles.copy():
    if a.column == "Headlines":
      a.update_blocked(True)
      if a.blocked and (len(a.blocked) >= 3 or max(a.blocked.values())) >= 2:
        log(a)
        g.to_archive.append(a)
        db.articles.remove(a)
  log(f"{len(g.to_archive)} headlines removed and archived")
  #db.savenow()
  exit()

# ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
# Save db.block_patterns_and_topics

if nDEBUG:
  if not db.block_patterns_and_topics: log("Error: db.block_patterns_and_topics is empty!"); exit(1)
  logi(f'saving {len(db.block_patterns_and_topics)} entries to {os.path.abspath("2 restore db.block_patterns_and_topics.py")}')
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
