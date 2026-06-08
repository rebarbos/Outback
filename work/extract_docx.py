from pathlib import Path
from lxml import etree
import json

base = Path("work/extracted")
doc = etree.parse(str(base / "word/document.xml"))
rels = etree.parse(str(base / "word/_rels/document.xml.rels"))

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
REL = "{http://schemas.openxmlformats.org/package/2006/relationships}"

relmap = {}
for rel in rels.getroot():
    rid = rel.get("Id")
    target = rel.get("Target")
    if target and target.startswith("media/"):
        relmap[rid] = "assets/" + Path(target).name

items = []

def text_of(node):
    return "".join(node.itertext()).strip()

for child in doc.getroot().find(f".//{W}body"):
    tag = etree.QName(child).localname
    if tag == "p":
        txt = text_of(child)
        imgs = []
        for blip in child.findall(f".//{A}blip"):
            rid = blip.get(f"{R}embed")
            if rid in relmap:
                imgs.append(relmap[rid])
        if txt or imgs:
            style = child.find(f".//{W}pStyle")
            items.append({
                "type": "p",
                "style": style.get(f"{W}val") if style is not None else None,
                "text": txt,
                "images": imgs,
            })
    elif tag == "tbl":
        rows = []
        for tr in child.findall(f"{W}tr"):
            cells = [text_of(tc) for tc in tr.findall(f"{W}tc")]
            if any(cells):
                rows.append(cells)
        if rows:
            items.append({"type": "table", "rows": rows})

Path("work/doc_items.json").write_text(json.dumps(items, ensure_ascii=False, indent=2))
for i, item in enumerate(items):
    print(i, item["type"], item.get("style"), item.get("text", "")[:120], item.get("images", ""))
