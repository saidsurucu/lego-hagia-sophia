"""All delivery formats derive from the same immutable placement list."""
from collections import Counter
import csv
from dataclasses import asdict
import io
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from scripts.model_core import BRICKLINK_PART_IDS, COLORS, PARTS, ldraw_line, validate


def ldr_text(pieces):
    lines = ["0 Ayasofya - Hagia Sophia / 48 x 48 stud architectural model",
             "0 Name: ayasofya.ldr", "0 Author: Custom design for Said Surucu",
             "0 !LDRAW_ORG Model", "0 !LICENSE Redistributable under CC BY 4.0 : see README.md",
             "0 // Upright official parts only. Digital connection checks are not physical strength certification.",
             "0 // Build on a flat table; early base plates are tied together by the next layer."]
    previous = None
    for p in sorted(pieces, key=lambda p: (p.bottom, (2 if p.mount == "side" else 1 if p.part in ("15068", "11477") else 0), p.z, p.x, p.part)):
        if p.bottom != previous:
            if previous is not None:
                lines.append("0 STEP")
            lines.append(f"0 // Layer bottom {p.bottom} plates / {p.bottom * 3.2:g} mm")
            previous = p.bottom
        lines.append(ldraw_line(p))
    lines.append("0 STEP")
    return "\n".join(lines) + "\n"


def inventory(pieces):
    return Counter((p.part, p.color) for p in pieces)


def csv_text(pieces):
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(["part_id", "bricklink_part_id", "part_name", "ldraw_color_id", "bricklink_color_id", "color", "renk", "quantity", "catalog_url"])
    for (part, color), count in sorted(inventory(pieces).items()):
        c = COLORS[color]
        bricklink_id = BRICKLINK_PART_IDS.get(part, part)
        writer.writerow([part, bricklink_id, PARTS[part].name, color, c["bricklink"], c["name"], c["tr"], count,
                         f"https://www.bricklink.com/v2/catalog/catalogitem.page?P={bricklink_id}&idColor={c['bricklink']}"])
    return output.getvalue()


def wanted_xml(pieces):
    root = ET.Element("INVENTORY")
    for (part, color), count in sorted(inventory(pieces).items()):
        item = ET.SubElement(root, "ITEM")
        for tag, value in (("ITEMTYPE", "P"), ("ITEMID", BRICKLINK_PART_IDS.get(part, part)), ("COLOR", COLORS[color]["bricklink"]), ("MINQTY", count)):
            ET.SubElement(item, tag).text = str(value)
    ET.indent(root)
    return ET.tostring(root, encoding="unicode") + "\n"


def deliver(pieces, destination="dist"):
    out = Path(destination)
    out.mkdir(parents=True, exist_ok=True)
    report = validate(pieces)
    (out / "dogrulama.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    if report["collisions"] or report["unsupported"] or report["out_of_base"] or report["connected_components"] != 1:
        raise ValueError(f"Model validation failed; see {out / 'dogrulama.json'}")
    (out / "ayasofya.ldr").write_text(ldr_text(pieces), encoding="utf-8")
    (out / "parca-listesi.csv").write_text(csv_text(pieces), encoding="utf-8-sig")
    (out / "bricklink-wanted.xml").write_text(wanted_xml(pieces), encoding="utf-8")
    (out / "model.json").write_text(json.dumps([asdict(p) for p in pieces], ensure_ascii=False, indent=2) + "\n")
    from scripts.make_guide import guide
    guide(pieces, out / "yapim-rehberi.html")
    print(json.dumps(report, indent=2, ensure_ascii=False))
