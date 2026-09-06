# Ayasofya — özel LEGO parça modeli

**4.149 parça · 43 parça türü · 9 renk · 96 alışveriş kalemi · 64 yapım adımı**

Taban **48 × 48 stud = 38,4 × 38,4 cm**. En yüksek minarenin uç çıkıntısı
dahil yükseklik **23,84 cm**. Gövde yüksekliği 23,68 cm'dir.

![Ayasofya modelinin gerçek parça geometrisinden önizlemesi](dist/ayasofya.png)

[Tam seti indir (ZIP)](https://github.com/saidsurucu/lego-hagia-sophia/releases/latest/download/ayasofya-seti.zip) · [Yapım rehberi](dist/yapim-rehberi.html) · [LDraw modeli](dist/ayasofya.ldr)

## Dosyalar

| Dosya | Kullanım |
|---|---|
| [ayasofya.ldr](dist/ayasofya.ldr) | BrickLink Studio / LDraw model dosyası; 64 STEP adımı |
| [Yapım rehberi](dist/yapim-rehberi.html) | Çevrimdışı açılan, yazdırılabilir katman planları |
| [Parça listesi](dist/parca-listesi.csv) | Parça, renk, adet ve katalog bağlantıları |
| [BrickLink alışveriş listesi](dist/bricklink-wanted.xml) | Wanted List'e aktarılabilir XML |
| [Doğu cephesi](dist/ayasofya-dogu.png) | Yarım kubbeler ve apsis görünümü |
| [Batı cephesi](dist/ayasofya-bati.png) | Giriş ve çatı kademeleri |
| [Diğer açı](dist/ayasofya-arka.png) | Karşı yönden gerçek model önizlemesi |
| [Blender sahnesi](dist/ayasofya.blend) | Düzenlenebilir önizleme sahnesi |

ZIP paketini tamamen açıp içindeki `dist/yapim-rehberi.html` dosyasını tarayıcıda
açın; görseller ve indirme bağlantıları aynı klasördeki dosyaları kullanır.
Rehberde her adımın harfli parça planı ve parça listesi bulunur. Plandaki kareler
birer studdur. Batı/giriş üstte, kuzey soldadır; X sağa, Z aşağıya artar.
Alem ve minare uçlarında 87580 merkez çıkıntılı plaka veya 3942c külahın
merkez studu kullanılır; bu yerleşimler yarım stud koordinatındadır.
Koordinatlar rehberde 1'den, kaynak JSON'da 0'dan başlar. Renkli parçalar o adımda
eklenir; soluk gri parçalar önceki adımlardan kalır. Baskıda bütün adımlar açılır.

## Açma ve parça siparişi

1. [BrickLink Studio](https://www.bricklink.com/v3/studio/download.page) içinde
   **File → Open** ile `ayasofya.ldr` dosyasını açın. Studio, LDraw dosyalarını
   [doğrudan açabilir](https://www.bricklink.com/v2/build/studiohelp.page).
2. Parçaları almak için BrickLink hesabınızda yeni bir Wanted List oluşturun.
   **Want → Upload → Upload BrickLink XML format** bölümünde
   `bricklink-wanted.xml` içeriğini aktarın ve hedef listenizi seçin.
   [BrickLink XML açıklaması](https://www.bricklink.com/help.asp?helpID=207).
3. Satıcı, parça durumu ve kargoyu kendiniz seçin. Bu çalışma sipariş vermez;
   fiyat veya belirli miktarda güncel stok garantisi içermez.

CSV'deki `part_id`, LDraw dosyasının parça adıdır; `bricklink_part_id` alışveriş
kataloğu numarasıdır. Örneğin **LDraw 3062b → BrickLink 3062**. Eski sürümdeki 3068b için de
3068 eşleştirmesi desteklenir; 3070b de 3070, 3040b ise 3040 olarak aktarılır. Benzer şekilde
LDraw 72 (koyu mavimsi gri), BrickLink 85'tir. XML bu dönüşümleri içerir.

## Yapı ve doğrulama

Model Ayasofya'nın geniş basık ana kubbesini, doğu/batı yarım kubbelerini,
pencere sıralarını, yan neflerini, payandalarını ve dört minaresini yorumlar.
LEGO Architecture Taj Mahal ve Notre-Dame yapım kılavuzlarından yararlanıldı.
43 parça türü arasında gerçek pencere çerçeveleri, yana bağlanan pencere
ızgaraları, taş dokulu tuğlalar, kavisli eğimler ve yuvarlak şerefeler bulunur.
32952 ve 87087 yana bakan pimli tuğlalar cephe ayrıntılarını taşır.

Yedinci sürümde çok açılı fotoğraflar ve zemin planıyla karşılaştırma yapıldı.
Dört minarenin gövdeleri uzatıldı; kare balkonların yerine 60474 yuvarlak
plakalar eklendi. Kubbe kasnağı 3 plakadan 6 plakaya yükseltildi. Ana kubbenin
20 stud çapı korunurken kavisli başlığın yükselişi 16 plakaya ayarlandı;
önceki 12 plakalı basık profile dönülmedi. Büyük kemerin altında yedi alt ve
beş üst pencere, yana bağlı dikey ızgaralarla oluşturuldu. Payandaların
tepelerine kavisli taş başlıklar eklendi, yivli süsleme azaltıldı. Batıdaki
sütunlu revak kapalı ve daha alçak bir nartekse dönüştürüldü. Güney eklerinin
yükseklikleri farklılaştırıldı ve küçük kubbelerin kavisleri yükseltildi.

Kaynak sayfalar, uygulanan teknikler ve önce/sonra görselleri
[mimari LEGO incelemesinde](docs/architecture-inspiration.md) bulunur.
Kubbe revizyonunun kaynakları ve Gemini ile üç turlu görsel incelemesi
[kubbe kaydında](docs/dome-comparison.md) bulunur.
Ayasofya'nın çok açılı fotoğraf kaynakları [fotoğraf kaydındadır](docs/photo-comparison.md).
Model mimari bir yorumdur; iç mekân işlenmemiştir, birebir rölöve değildir.

Üç katlı şaşırtmalı plaka tabanı, iki stud kalınlığında dış duvarlar, iç destek
şeritleri ve çatı bağlama plakaları kullanılır. Kubbelerin iç taşıyıcıları plaka katmanlarıdır; görünen yüzeyleri kavisli ve
eğimli parçalarla kaplanır. Eğimin yüksek kenarı merkeze yönelir. Büyük kemerin
üst dolguları resmî parçanın farklı yükseklikteki pimlerine oturur. Özel parça, yapıştırıcı,
kesme, eğme veya gerilim altında bağlantı yoktur.

Gerçekleştirilen kontroller:

- **4.149 yerleşim:** muhafazakâr gövde zarflarında sıfır çakışma;
  taban üzerindeki bütün parçalar önceden yerleştirilmiş bir parçaya
  alt veya özel olarak modellenen yan pimleriyle bağlanır.
- **Tek bağlantı ağı:** 6.212 parça-parça bağlantısı. Yerleşim sırasındaki
  üst parçalar, önceden eklenen taşıyıcı parçaya bağlanıyor.
- **Gerçek LDraw sınırları:** resmî üçgen/dörtgen geometrisi bağımsız olarak
  çözülüp dışa aktarılan 4.149 parçanın boyut ve konumlarıyla karşılaştırıldı;
  sıfır sınır uyuşmazlığı.
- **96/96 parça-renk eşleşmesi:** BrickLink'in ilgili parçasına ait renk
  görsel kayıtlarıyla doğrulandı. Kaynak ve kanıtlar raporda yer alıyor.
- **45 otomatik test:** çakışma, havada kalan parça, düz yan temasın bağlantı
  sayılmaması, yönü eşleşen yan pim ve yuvalar, yarım stud çakışmaları, merkez studları, karoların üst yüzeyi, dışa aktarma eksenleri, dış ölçüler,
  yapım sırası ve CSV/XML/LDR tutarlılığı.

Raporlar: [bağlantı kontrolü](dist/dogrulama.json),
[gerçek geometri kontrolü](dist/ldraw-geometri-dogrulama.json),
[katalog kanıtları](dist/katalog-dogrulama.json).

**Fiziksel montaj yapılmadı.** Bunlar dijital geometri ve bağlantı
kontrolleridir; tutunma kuvveti, esneme, burulma veya taşıma dayanımı
simülasyonu değildir. 1.104 parça tek pimden bağlanır. 24 düşey pencere
ızgarası ve dört taş madalyon için yan bağlantılar ayrıca modellenmiştir.
54 geniş kavisli parça dörder, 142 dar kavisli parça ve 88 dik eğim ikişer
pimle desteklenir. Kavisli parçaların yüksek alt sıralarındaki dolgu plakaları
kaplamalardan önce takılır. Rehber bu katmanları iki planla, yan cephe
parçalarını ise taşıyıcı koordinatı ve yön tablosuyla gösterir.
Minareleri tutarak kaldırmayın; tabanı alttan
iki elle destekleyin. İlk taban katını düz bir masa üzerinde dizin, sonra
diğer iki katla bağlayın. Önizlemeler resmî LDraw geometrilerinden Blender ile
alındı. Ön ve kuzeydoğu görselleri 3840×3200 piksel, diğer cepheler
1800×1500 pikseldir; AI tarafından üretilmiş bir konsept görsel değildir.

## Yeniden üretim

Model üretimi ve testler Python 3 standart kütüphanesiyle çalışır. Komutları
proje kökünde çalıştırın:

```sh
python3 -m unittest discover -s tests -v
python3 -m scripts.build_model
python3 scripts/audit_ldraw.py
python3 scripts/verify_catalog.py
python3 -m scripts.package_model
```

Model üretim komutu LDR, CSV, XML, JSON raporu ve HTML rehberi yeniden üretir.
Katalog doğrulaması internete bağlanır. Aynı makinedeki daha önce alınmış
sayfalarla `python3 scripts/verify_catalog.py --offline` kullanılabilir.
Son komut, teslim dosyalarının SHA-256 manifestini ve `ayasofya-seti.zip`
paketini üretir; model değiştiyse paketlemeden önce görselleri de yenileyin.

Resmî geometri önbelleği `assets/ldraw` içinde, kaynak ve SHA-256 bilgileri
`assets/ldraw/manifest.json` içindedir. Yeni parça eklenirse:

```sh
python3 scripts/fetch_parts.py --model dist/ayasofya.ldr
```

Önizlemeleri üretmek için Blender gerekir. Bu makinede kullanılan sürüm 5.2.1:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --python scripts/render_model.py -- dist/ayasofya.ldr dist/ayasofya.png hero 4k
/Applications/Blender.app/Contents/MacOS/Blender --background --python scripts/render_model.py -- dist/ayasofya.ldr dist/ayasofya-arka.png rear 4k
```

Parçalar değiştirildiğinde model, alışveriş listesi, rehber, raporlar ve dört
önizleme birlikte yeniden üretilmelidir. Render işlemi geometriyi küçültmeden
bağlı mesh örnekleriyle çalışır. Blender sahneleri parça meshlerini içerir;
LDraw eklentisi gerektirmez. Bu Mac'te sandbox altında Metal başlangıcı hata
verdiğinden render normal uygulama erişimiyle çalıştırılmıştır.

## Kaynaklar ve lisans

- [LDraw dosya biçimi](https://www.ldraw.org/article/218.html): 20 LDU stud
  aralığı, 24 LDU tuğla ve 8 LDU plaka gövde yüksekliği.
- [LDraw resmî parça kütüphanesi](https://library.ldraw.org/): geometri.
- [Katalog doğrulama yöntemi](docs/catalog-sources.md): gerçek renk kayıtları.
- [Kültür ve Turizm Bakanlığı Ayasofya mimarisi](https://www.ktb.gov.tr/genel/SanalMuzeler/ayasofya/bilgi.htm):
  ana mekân, yan nefler ve narteks için mimari başvuru. Bu eski sayfanın
  ziyaret bilgileri veya müze statüsü güncel bilgi olarak kullanılmadı.

Özgün model yerleşimi, üretici kodu ve rehber **CC BY 4.0** ile paylaşılır;
atıf adı: “Ayasofya custom model — Said Sürücü”. LDraw parça geometrileri
ilgili LDraw katkıcılarınındır; dosyalardaki yazar ve lisans başlıkları
korunmuştur. [LDraw lisans metni](assets/ldraw/CAlicense4.txt) ve
[katkıcı bildirimi](assets/ldraw/CAreadme.txt) pakette bulunur.

Bu, resmî veya LEGO tarafından onaylanmış bir set değildir.
