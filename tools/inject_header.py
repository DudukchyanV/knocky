"""Put the shared header (shared/header.*) into a page between <!--KH:start--> and <!--KH:end-->.
Usage: python3 tools/inject_header.py page.html [page2.html ...]"""
import sys, pathlib
base = pathlib.Path(__file__).resolve().parent.parent / "shared"
block = ("<!--KH:start--><style id=\"kh-css\">" + (base / "header.css").read_text() + "</style>\n"
         + (base / "header.html").read_text() + "<script id=\"kh-js\">" + (base / "header.js").read_text() + "</script><!--KH:end-->")
for p in sys.argv[1:]:
    s = pathlib.Path(p).read_text()
    i, j = s.index("<!--KH:start-->"), s.index("<!--KH:end-->") + len("<!--KH:end-->")
    pathlib.Path(p).write_text(s[:i] + block + s[j:])
    print("header ->", p)
