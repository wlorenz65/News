from GLOBALS import *; DEBUG = (__name__ == "__main__")
log(f"{len(db.articles)=}")
log(f"{len(db.block_patterns_and_topics)=}")

if not db.block_patterns_and_topics: log("Error: db.block_patterns_and_topics is empty!"); exit(1)
logi(f'saving {len(db.block_patterns_and_topics)} entries to {os.path.abspath("restore-db.block_patterns_and_topics.py")}')
import pprint
with open("restore-db.block_patterns_and_topics.py", "w") as f:
  f.write(f"""\
from GLOBALS import *; DEBUG = (__name__ == "__main__")

print(f"There were {{len(db.block_patterns_and_topics)}} entries in db.block_patterns_and_topics")

db.block_patterns_and_topics = {{
{pprint.pformat(db.block_patterns_and_topics, indent=0)[1:-1]},
}}

print(f" Restoring {{len(db.block_patterns_and_topics)}} entries to db.block_patterns_and_topics")
if "y" in input(f'\\nWrite file {{os.path.abspath("News.db")}} [yN]? '):
  db.savenow(); print("Ok.")
else: print("Not written.")
""")
