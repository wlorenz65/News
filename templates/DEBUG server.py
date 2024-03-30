import bottle, os
@bottle.route("/<filename:path>")
def get(filename): return bottle.static_file(filename, root="/storage/emulated/0/qpython/Desktop/styles" if "IS_QPY3" in os.environ else "")
bottle.run(host="0.0.0.0", port=8080)
