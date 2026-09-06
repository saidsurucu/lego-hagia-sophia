"""Generate a printable, offline Turkish layer-by-layer building guide."""
from collections import Counter, defaultdict
from html import escape
import json
from pathlib import Path

from scripts.model_core import BRICKLINK_PART_IDS, COLORS, PARTS, Piece


def label(index):
    return chr(65 + index) if index < 26 else "A" + chr(65 + index - 26)


def diagram(current, previous, codes, number):
    svg = [f'<svg viewBox="-3 -4 54 55" role="img" aria-label="Adım {number}: üstten parça yerleşim planı">',
           '<defs><pattern id="grid%d" width="1" height="1" patternUnits="userSpaceOnUse"><path d="M1 0H0V1" fill="none" stroke="#cbc4b9" stroke-width=".025"/></pattern></defs>' % number,
           '<rect width="48" height="48" fill="#faf8f3" stroke="#968c7c" stroke-width=".12"/>']
    for p in previous:
        x0, z0, x1, z1 = p.plan_bounds()
        svg.append(f'<rect x="{x0}" y="{z0}" width="{x1-x0}" height="{z1-z0}" fill="#e8e4dc" stroke="#cbc4b9" stroke-width=".035"/>')
    svg.append(f'<rect width="48" height="48" fill="url(#grid{number})"/>')
    for p in current:
        color = COLORS[p.color]["hex"]
        title = f'{PARTS[p.part].name} · {COLORS[p.color]["tr"]} · X={p.x+1}, Z={p.z+1} · {p.width}×{p.depth}'
        common = f'fill="#{color}" stroke="#37322c" stroke-width=".075"'
        if p.mount == "side":
            x0, z0, x1, z1 = p.plan_bounds()
            title = f'{PARTS[p.part].name} · Taşıyıcı X={p.x+1}, Z={p.z+1} · yana takılır'
            shape = f'<rect x="{x0}" y="{z0}" width="{x1-x0}" height="{z1-z0}" {common}/>'
        elif p.part in ("3941", "3942c", "4589", "3062b", "4073"):
            shape = f'<circle cx="{p.x + p.width/2}" cy="{p.z+p.depth/2}" r="{p.width/2-.035}" {common}/>'
        else:
            shape = f'<rect x="{p.x+.025}" y="{p.z+.025}" width="{p.width-.05}" height="{p.depth-.05}" rx=".06" {common}/>'
        if p.part == "87580":
            shape += f'<circle cx="{p.x+1}" cy="{p.z+1}" r=".31" fill="none" stroke="#37322c" stroke-width=".08"/>'
        if p.part in ("15068", "11477", "3039", "3040b", "54200"):
            # Bold edge is the high side of the slope, in plan coordinates.
            edges = {0: (p.x+.15, p.z+p.depth-.12, p.x+p.width-.15, p.z+p.depth-.12),
                     90: (p.x+.12, p.z+.15, p.x+.12, p.z+p.depth-.15),
                     180: (p.x+.15, p.z+.12, p.x+p.width-.15, p.z+.12),
                     270: (p.x+p.width-.12, p.z+.15, p.x+p.width-.12, p.z+p.depth-.15)}
            x1, y1, x2, y2 = edges[p.rotation]
            shape += f'<path d="M{x1} {y1}L{x2} {y2}" stroke="#37322c" stroke-width=".16"/>'
        if p.part == "98283":
            shape += f'<path d="M{p.x+.1} {p.z+p.depth/2}h{p.width-.2}" stroke="#6e604a" stroke-width=".045"/>'
        code = codes[p.part, p.color]
        ink = "#fff" if p.color in (0, 70, 72) else "#211f1a"
        svg.append(f'<g><title>{escape(title)}</title>{shape}<text x="{p.x+p.width/2}" y="{p.z+p.depth/2+.24}" text-anchor="middle" fill="{ink}" font-size=".68" font-family="Arial,sans-serif" font-weight="700">{code}</text></g>')
    for tick in range(0, 48, 2):
        svg.append(f'<text x="{tick+.5}" y="-.65" text-anchor="middle" font-size=".68" fill="#63594c">{tick+1}</text>')
        svg.append(f'<text x="-.65" y="{tick+.75}" text-anchor="end" font-size=".68" fill="#63594c">{tick+1}</text>')
    svg += ['<text x="24" y="-2.5" text-anchor="middle" font-size=".9" fill="#715139">BATI / GİRİŞ · Z=1</text>',
            '<text x="24" y="50" text-anchor="middle" font-size=".85" fill="#715139">DOĞU · Z=48</text>',
            '</svg>']
    return "".join(svg)


STYLE = """
:root{--ink:#29251f;--paper:#f6f2e9;--clay:#853f29;--line:#dcd4c7}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:15px/1.55 -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}
main{max-width:1160px;margin:auto;padding:44px 32px}a{color:var(--clay);text-underline-offset:4px}
.mast{display:flex;justify-content:space-between;border-top:2px solid var(--ink);padding:14px 0;letter-spacing:.14em;font-size:11px;text-transform:uppercase}
h1{font:clamp(54px,9vw,108px)/1 Georgia,serif;letter-spacing:-.065em;margin:34px 0 8px}h2{font:36px/1.15 Georgia,serif;margin:10px 0 20px}h3{font-size:16px;margin:0 0 10px}.sub{font:22px Georgia,serif;color:#7c6d5c}
.hero{width:100%;display:block;margin:30px 0 0;border:1px solid var(--line)}.caption{font-size:12px;color:#70685d;margin:8px 0 22px}
.stats{display:grid;grid-template-columns:repeat(4,1fr);border-top:1px solid var(--line);border-bottom:1px solid var(--line);margin:28px 0}.stats div{padding:19px 18px;border-right:1px solid var(--line)}.stats div:last-child{border:0}.stats strong{display:block;font:32px Georgia,serif}.stats span{font-size:11px;text-transform:uppercase;letter-spacing:.09em}
.downloads{display:flex;gap:12px;flex-wrap:wrap;margin:20px 0 32px}.downloads a,button{padding:10px 16px;border:1px solid var(--clay);border-radius:2px;background:transparent;color:var(--clay);font:inherit;cursor:pointer;text-decoration:none}.downloads a:first-child{background:var(--clay);color:white}button:disabled{opacity:.35;cursor:default}button:focus-visible,a:focus-visible,select:focus-visible{outline:3px solid #a66638;outline-offset:3px}
.intro{display:grid;grid-template-columns:1fr 1fr;gap:30px;margin:30px 0 42px}.intro p{margin:8px 0}.note{border-left:3px solid var(--clay);padding:12px 18px;background:#eee7db}.toolbar{position:sticky;top:0;z-index:3;background:#f6f2e9f5;backdrop-filter:blur(8px);display:flex;gap:10px;align-items:center;padding:14px 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line);flex-wrap:wrap}.toolbar select{font:inherit;max-width:280px;padding:11px;background:#fff;border:1px solid var(--line)}.toolbar .spacer{flex:1}
.step{padding:30px 0 50px;border-bottom:1px solid var(--line)}.step header{display:flex;justify-content:space-between;gap:25px;align-items:start}.step h2{margin-top:0}.kicker{font-size:11px;letter-spacing:.12em;color:var(--clay);text-transform:uppercase;margin-bottom:9px}.height{font-size:13px;color:#716456}.step-layout{display:grid;grid-template-columns:minmax(0,2fr) minmax(220px,1fr);gap:28px}.diagram{background:#fff;border:1px solid var(--line);padding:10px}.diagram svg{display:block;width:100%;height:auto}.legend{display:grid;gap:8px;align-content:start}.part{display:grid;grid-template-columns:30px 1fr auto;gap:8px;align-items:center;padding:10px 0;border-bottom:1px solid var(--line)}.part small{display:block;color:#746c61;font-size:11px}.swatch{height:29px;width:29px;border:1px solid #7c7469;display:grid;place-items:center;font-weight:700}.qty{font:22px Georgia,serif}.sections{max-width:650px;color:#756b5b;font-size:13px}.foot{font-size:12px;color:#786e60;border-top:1px solid var(--line);padding-top:20px;margin-top:32px}.side-assembly{margin-top:16px;font-size:12px}.side-assembly table{width:100%;border-collapse:collapse;text-align:left}.side-assembly td,.side-assembly th{padding:3px 8px;border-bottom:1px solid var(--line)}.step[hidden]{display:none}.instruction{font-size:12px;color:#756b5b}
@media(max-width:760px){main{padding:22px 16px}.intro,.step-layout{grid-template-columns:1fr}.stats{grid-template-columns:repeat(2,1fr)}.stats strong{font-size:25px}.mast{font-size:9px}.toolbar select{max-width:190px}.toolbar .spacer{display:none}.step header{display:block}.legend{grid-template-columns:1fr 1fr}.part{font-size:12px}.height{text-align:left}.downloads a{flex:1;text-align:center}.toolbar button{padding:8px 11px}.part{grid-template-columns:25px 1fr auto}.swatch{height:24px;width:24px}}
@media print{@page{size:A4;margin:12mm}body{background:white;font-size:10px;-webkit-print-color-adjust:exact;print-color-adjust:exact}main{max-width:none;padding:0}.toolbar,.downloads,.screen-only{display:none!important}.cover{break-after:page}.hero{max-height:125mm;object-fit:contain;margin-top:10px}.mast{font-size:8px}h1{font-size:54px;margin:15px 0 5px}.sub{font-size:16px}.stats{margin:12px 0}.stats div{padding:10px}.stats strong{font-size:24px}.intro{gap:15px;margin:16px 0}.intro p{font-size:10px}.note{padding:8px}.step,.step[hidden]{display:block!important;break-before:page;break-inside:avoid;padding:0;border:0}.step h2{font-size:26px}.step-layout{display:block}.diagram.two-phase{width:100%;display:grid;grid-template-columns:1fr 1fr;gap:3mm}.diagram{width:138mm;margin:auto;padding:0;border:0}.legend{grid-template-columns:repeat(3,1fr);gap:4px 14px;margin-top:3mm}.part{padding:3px 0;grid-template-columns:20px 1fr auto;font-size:9px}.part small{font-size:8px}.swatch{width:20px;height:20px}.qty{font-size:16px}.height,.sections,.instruction{font-size:9px}.kicker{font-size:9px;margin-bottom:4px}.foot{font-size:9px}}
"""


def guide(pieces, destination="dist/yapim-rehberi.html"):
    layers = defaultdict(list)
    for p in sorted(pieces, key=lambda p: (p.bottom, p.z, p.x, p.part)):
        layers[p.bottom].append(p)
    count = len(pieces)
    types = len({p.part for p in pieces})
    height = max(p.top * .32 + PARTS[p.part].stud_height_ldu * .04 for p in pieces)
    page = [f'<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Ayasofya · Yapım rehberi</title><style>{STYLE}</style></head><body><main>',
            '<section class="cover"><div class="mast"><span>İstanbul · Özel mimari model</span><span>Model 001 / Revizyon 07</span></div>',
            '<h1>Ayasofya.</h1><div class="sub">Bir anıtı, parça parça yeniden kur.</div>',
            '<img class="hero" src="ayasofya.png" alt="Ayasofya modelinin gerçek LEGO parça geometrisinden üretilmiş üç boyutlu görünümü">',
            '<p class="caption">Görsel, aynı klasördeki ayasofya.ldr dosyasından üretildi. Mimari yorum; birebir rölöve değildir.</p>',
            f'<div class="stats"><div><strong>{format(count, ",").replace(",", ".")}</strong><span>Parça</span></div><div><strong>48 × 48</strong><span>Stud taban</span></div><div><strong>{format(height, ".1f").replace(".", ",")} cm</strong><span>Yükseklik</span></div><div><strong>{len(layers)}</strong><span>Yapım adımı</span></div></div>',
            '<div class="downloads"><a href="ayasofya.ldr" download>Modeli indir · .ldr</a><a href="parca-listesi.csv" download>Parça listesi · CSV</a><a href="bricklink-wanted.xml" download>BrickLink · XML</a><a href="ayasofya-arka.png">Kuzeydoğu</a><a href="ayasofya-dogu.png">Doğu</a><a href="ayasofya-bati.png">Batı</a></div>',
            f'<div class="intro"><div><h3>Başlamadan önce</h3><p>Taban 38,4 × 38,4 cm. {types} parça türünü renklerine göre ayır. Geniş, düz bir masa üzerinde çalış; ilk taban katı, sonraki iki kat eklendiğinde birbirine bağlanır.</p><p>Her adım aynı yükseklikte başlayan parçaları gösterir. LEGO tuğlası 3 plaka; bir plaka 3,2 mm yüksekliğindedir. Minareler bazı adımlarda birden fazla plaka yüksekliğinde yükselir.</p></div>',
            '<div><h3>Planları nasıl okuyacaksın?</h3><p>Üstten görünümde <b>batı/giriş üstte, doğu altta, kuzey solda</b>. X soldan sağa, Z yukarıdan aşağıya 1–48 olarak sayılır. Bir küçük kare bir stud yeridir. Yarım değerli koordinatlar (örneğin 24,5) yarım stud kaymayı gösterir: 87580 merkez çıkıntılı plakanın üzerindeki alem ve 3942c külahın üzerindeki 4589 uç, alt parçanın tam ortasına bağlanır.</p><p>Soluk gri parçalar daha önce yerleştirildi. Renkli parçalar bu adımda eklenir. Harfler sağdaki parça listesine karşılık gelir; çizginin kapladığı kare sayısı parçanın yönünü belirler. Eğimli parçanın kalın çizgili kenarı yüksek tarafıdır. Kavisli parçalardan önce alt dolgu plakalarını tak; alçak sıra zemine, yüksek sıra bir plaka yüksekliğindeki dolguya oturur. Kemerler uç sütunlardan desteklenir; 6108 büyük kemerin üst dolgu tuğlaları basamaklarına bağlanır. Yan cephe parçaları, ilgili adımın altındaki koordinat ve yön tablosuyla en son takılır. Bilgisayarda parçanın üzerine gelerek koordinatını görebilirsin.</p></div></div>',
            '<p class="note"><b>Doğrulama:</b> Parça gövdeleri, stud bağlantıları, montaj sırası ve gerçek LDraw geometri sınırları sayısal olarak kontrol edildi. Fiziksel kurulum, tutunma kuvveti ve taşıma dayanımı test edilmedi. Minareleri tutarak kaldırma; modeli tabanının altından iki elle destekle.</p></section>',
            '<nav class="toolbar" aria-label="Yapım adımları"><button id="prev" type="button">← Önceki</button><label for="step-select">Adım</label><select id="step-select">']
    for i, bottom in enumerate(layers, 1):
        page.append(f'<option value="{i-1}">{i:02d} / {len(layers)} · {bottom} plaka</option>')
    page += ['</select><button id="next" type="button">Sonraki →</button><span class="spacer"></span><button id="all" type="button">Tüm adımlar</button><button id="print" type="button">Yazdır</button></nav>']
    previous = []
    for i, (bottom, current) in enumerate(layers.items(), 1):
        counts = Counter((p.part, p.color) for p in current)
        codes = {key: label(j) for j, key in enumerate(sorted(counts))}
        page.append(f'<section class="step" id="adim-{i}" data-piece-count="{len(current)}"><header><div><div class="kicker">Ayasofya / Yapım sırası</div><h2>Adım {i:02d}</h2></div><div class="height">Bu adımda <b>{len(current)} parça</b><br>Katman / taşıyıcı tabanı: {bottom} plaka · {bottom*3.2:g} mm</div></header>')
        sections = "; ".join(dict.fromkeys(p.section for p in current))
        side = [p for p in current if p.mount == "side"]
        upright = [p for p in current if p.mount == "up"]
        caps = [p for p in upright if p.part in ("15068", "11477")]
        supports = [p for p in upright if p.part not in ("15068", "11477")]
        if caps and any("kavis altı dolgu" in p.section for p in supports):
            plans = ('<div class="phase"><p class="instruction"><b>1. Destek plakalarını ve diğer alt parçaları yerleştir.</b></p>'
                     + diagram(supports, previous, codes, i * 100)
                     + '</div><div class="phase"><p class="instruction"><b>2. Kavisli kaplamaları tak; yüksek alt sıra dolgu plakasına oturur.</b></p>'
                     + diagram(caps, previous + supports, codes, i) + '</div>')
        else:
            plans = diagram(upright, previous, codes, i)
        phase_class = " two-phase" if 'class="phase"' in plans else ""
        page.append(f'<p class="sections">{escape(sections)}</p><div class="step-layout"><div class="diagram{phase_class}">{plans}</div><div class="legend">')
        for key, code in codes.items():
            part, color = key
            p = PARTS[part]
            c = COLORS[color]
            ink = "white" if color in (0, 70, 72) else "#221d16"
            bricklink = BRICKLINK_PART_IDS.get(part, part)
            page.append(f'<div class="part"><span class="swatch" style="background:#{c["hex"]};color:{ink}">{code}</span><div><b>{bricklink}</b> · {escape(c["tr"])}<small>{escape(p.name)} · {p.height} plaka</small></div><span class="qty">{counts[key]}×</span></div>')
        page.append('</div></div>')
        if side:
            directions = {0: "Batı / planın üstü", 90: "Güney / planın sağı", 180: "Doğu / planın altı", 270: "Kuzey / planın solu"}
            page.append('<div class="note side-assembly"><b>Son olarak: yana takılan cephe parçaları</b><p>Önce yukarıdaki taşıyıcıları yerleştir. Aşağıdaki parçaları taşıyıcının dışa bakan pimlerine tak; üst yüzeye yatırma. Izgaralar düşey durur. X/Z, taşıyıcının plandaki konumudur.</p><table><thead><tr><th>Parça</th><th>Taşıyıcı</th><th>X</th><th>Z</th><th>Baktığı yön</th></tr></thead><tbody>')
            for p in side:
                page.append(f'<tr data-side-placement="1"><td>{codes[p.part,p.color]} · {BRICKLINK_PART_IDS.get(p.part,p.part)}</td><td>{p.host_part}</td><td>{p.x+1:g}</td><td>{p.z+1:g}</td><td>{directions[p.rotation]}</td></tr>')
            page.append('</tbody></table></div>')
        page.append('<p class="instruction">Renkli alanları yerleştir. Kavis altı dolgular kaplamalardan, yan taşıyıcılar cephe süslerinden önce takılır.</p></section>')
        previous.extend(current)
    page += ['<footer class="foot">Özel Ayasofya tasarımı · Resmî LEGO ürünü değildir. Model tasarımı: CC BY 4.0; resmî parça geometrileri: LDraw katkıcıları, CC BY 4.0. Katalog kaydı güncel stok veya fiyat garantisi değildir. Ayrıntılar README.md ve doğrulama raporlarında.</footer>',
             '''</main><script>
const steps=[...document.querySelectorAll('.step')],select=document.querySelector('#step-select');
let current=0,all=false;
function show(){steps.forEach((s,i)=>s.hidden=!all&&i!==current);select.value=current;document.querySelector('#prev').disabled=all||current===0;document.querySelector('#next').disabled=all||current===steps.length-1;document.querySelector('#all').textContent=all?'Tek adım':'Tüm adımlar';}
select.addEventListener('change',()=>{current=Number(select.value);all=false;show();});
document.querySelector('#prev').addEventListener('click',()=>{current=Math.max(0,current-1);show();});
document.querySelector('#next').addEventListener('click',()=>{current=Math.min(steps.length-1,current+1);show();});
document.querySelector('#all').addEventListener('click',()=>{all=!all;show();});
document.querySelector('#print').addEventListener('click',()=>window.print());show();
</script></body></html>''']
    Path(destination).write_text("\n".join(page), encoding="utf-8")
    print(f"Guide: {len(layers)} steps, {count} placements -> {destination}")


if __name__ == "__main__":
    data = json.loads(Path("dist/model.json").read_text())
    guide([Piece(**row) for row in data])
