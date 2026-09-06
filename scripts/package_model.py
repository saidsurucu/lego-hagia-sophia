"""Package the concrete delivery, source and local official geometry cache."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def package():
    dist = ROOT / "dist"
    required = ("ayasofya.ldr", "parca-listesi.csv", "bricklink-wanted.xml",
                "ayasofya.png", "ayasofya-arka.png", "yapim-rehberi.html",
                "dogrulama.json", "ldraw-geometri-dogrulama.json", "katalog-dogrulama.json")
    for name in required:
        if not (dist / name).is_file():
            raise FileNotFoundError(name)
    geometry = json.loads((dist / "ldraw-geometri-dogrulama.json").read_text())
    catalog = json.loads((dist / "katalog-dogrulama.json").read_text())
    structural = json.loads((dist / "dogrulama.json").read_text())
    if not geometry["passed"] or catalog["unknown_pairs"] or structural["collisions"] or structural["unsupported"]:
        raise ValueError("Delivery reports have unresolved failures")
    if catalog["bom_sha256"] != hashlib.sha256((dist / "parca-listesi.csv").read_bytes()).hexdigest():
        raise ValueError("Catalogue evidence does not match current BOM")
    checksums = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in sorted(dist.iterdir()) if p.is_file() and p.name != "teslim-manifest.json"}
    (dist / "teslim-manifest.json").write_text(json.dumps({
        "model": "Ayasofya", "pieces": structural["piece_count"],
        "dimensions_cm": [38.4, 38.4, structural["height_cm"]],
        "sha256": checksums,
    }, indent=2, ensure_ascii=False) + "\n")
    files = [ROOT / "README.md"]
    for folder in ("dist", "scripts", "tests", "assets", "docs"):
        files.extend(p for p in (ROOT / folder).rglob("*") if p.is_file()
                     and "__pycache__" not in p.parts
                     and p.name != ".DS_Store" and not p.name.endswith((".pyc", ".blend1")))
    output = ROOT / "ayasofya-seti.zip"
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(files):
            archive.write(path, "ayasofya-seti/" + path.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(output) as archive:
        problem = archive.testzip()
        if problem:
            raise ValueError(f"Archive integrity error: {problem}")
    print(f"Package: {output.name}, {len(files)} files, {output.stat().st_size/1024/1024:.2f} MiB; ZIP integrity passed")


if __name__ == "__main__":
    package()
