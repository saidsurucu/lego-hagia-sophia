# Parça ve renk katalog kanıtı

`scripts/verify_catalog.py`, `dist/parca-listesi.csv` dosyasındaki her parça–renk
çiftini BrickLink Reference Catalog'un ilgili parçaya ait **Color Images**
sayfasındaki gerçek görsel kartlarıyla karşılaştırır.

Kaynak adresi: `https://www.bricklink.com/catalogColors.asp?itemType=P&itemNo=PARCA`.
Örnek: [3942c renk görselleri](https://www.bricklink.com/catalogColors.asp?itemType=P&itemNo=3942c).

Bir eşleşmenin doğrulanması için kartın bağlantısında doğru parça ve BrickLink
renk numarası, hemen içindeki görsel yolunda da aynı parça ve renk bulunmalıdır.
Genel renk açılır listeleri veya yalnızca adres çubuğundaki `idColor` parametresi
kanıt kabul edilmez. Buradaki “doğrulandı”, katalogda o parça–renk için bir görsel
kaydı bulunduğunu ifade eder; LEGO üretim veritabanının veya set envanterlerinin
bağımsız doğrulaması değildir.

LDraw ve alışveriş kataloğu numaraları farklı olabilir. CSV'de
`bricklink_part_id` varsa sorgular bu alanı kullanır. Örneğin LDraw `3068b`
(oluklu 2×2 karo), güncel [BrickLink 3068](https://www.bricklink.com/v2/catalog/catalogitem.page?P=3068)
altında aranır. [3068 renk görselleri](https://www.bricklink.com/catalogColors.asp?itemType=P&itemNo=3068)
sayfasında Dark Bluish Gray (`85`) kartı bulunur.

Altın kubbe tepeliğindeki LDraw `3062b`, alışverişte
[BrickLink 3062](https://www.bricklink.com/catalogColors.asp?itemType=P&itemNo=3062)
olarak geçer; Pearl Gold (`115`) için gerçek renk görseli ve `6060800` element
kaydı vardır. Yuvarlak 1×1 plaka için
[BrickLink 4073](https://www.bricklink.com/catalogColors.asp?itemType=P&itemNo=4073)
korunur; aynı renk için görsel ve `4523159` element kaydı bulunur.
`6141` renk sayfasının genel Color Guide'a yönlenmesi, bu parça için kanıt
sayılmamıştır.

İnce minare tepeleri için [4589](https://www.bricklink.com/catalogColors.asp?itemType=P&itemNo=4589)
ve [87580](https://www.bricklink.com/catalogColors.asp?itemType=P&itemNo=87580)
parçalarının Light Bluish Gray (`86`) gerçek görsel kartları doğrulanmıştır.
[3941](https://www.bricklink.com/catalogColors.asp?itemType=P&itemNo=3941)
yuvarlak tuğlada Reddish Brown (`88`) kartı bulunur; Dark Orange (`68`)
görsel kartı bulunmadığı için bu renk aynı yöntemle doğrulanmış sayılmaz.

## Ayrıntılı model için araştırılan biçimli parçalar

Aşağıdaki adaylar gerçek BrickLink renk kartlarıyla kontrol edilmiştir. Bu liste
modelde hepsinin kullanıldığı anlamına gelmez; son CSV ve JSON raporu belirleyicidir.
`2` Tan, `69` Dark Tan, `150` Medium Nougat, `86` Light Bluish Gray'dir.

| LDraw parçası | Resmî LDraw adı | BrickLink ID | Doğrulanan aday renkler |
|---|---|---|---|
| 15068 | Slope Brick Curved 2 x 2 x 0.667 | 15068 | 2, 69, 150, 86 |
| 11477 | Slope Brick Curved 2 x 1 | 11477 | 2, 69, 150, 86 |
| 25269 | Tile 1 x 1 Corner Round | 25269 | 2, 69, 150, 86 |
| 3039 | Slope Brick 45 2 x 2 | 3039 | 2, 69, 150, 86 |
| 3040b | Slope Brick 45 2 x 1 | 3040 | 2, 69, 150, 86 |
| 3659 | Arch 1 x 4 | 3659 | 2, 69, 150, 86 |
| 6060 | Arch 1 x 6 x 3.333 with Curved Top and Two Studs | 6060 | 86 |
| 4490 | Arch 1 x 3 | 4490 | 2, 86 |
| 98283 | Brick 1 x 2 with Embossed Bricks | 98283 | 2, 69, 150, 86 |
| 2412b | Tile 1 x 2 Grille with Groove | 2412b | 86 |
| 85080 | Brick 2 x 2 Corner Round w Stud Notch and Reinforced Underside | 85080 | 2, 69, 150, 86 |
| 6108 | Arch 1 x 12 x 3 | 6108 | 2, 86 |
| 3068b | Tile 2 x 2 with Groove | 3068 | 2, 69, 86 |
| 3069b | Tile 1 x 2 with Groove | 3069 | 2, 69, 86 |
| 2431 | Tile 1 x 4 | 2431 | 2, 69, 86 |
| 54200 | Slope Brick 31 1 x 1 x 0.667 | 54200 | 2, 86 |

Biçim kaynakları: `https://library.ldraw.org/library/official/parts/ID.dat` ve
gereken alt parçalar için `https://library.ldraw.org/library/official/parts/s/ID.dat`.
Örneğin [15068](https://library.ldraw.org/library/official/parts/15068.dat),
[15068 alt parçası](https://library.ldraw.org/library/official/parts/s/15068s01.dat),
[3039](https://library.ldraw.org/library/official/parts/3039.dat).
Renk kaynağı her satırın BrickLink ID'siyle yukarıdaki `catalogColors.asp` şablonudur.

Yerleşim açısından kritik geometri: 15068 ve 11477'nin gövdesi yerel Y ekseninde
`-16..0`, Z ekseninde `-20..20` aralığındadır; kavis Z pozitif yönde yükselir.
Alt yüzeyleri basamaklıdır: Z negatif sırada alt düzlem Y=0, Z pozitif sırada
Y=-8'dir. Üstlerinde bağlantı pimi yoktur. 3039'un gövdesi X=`-20..20`,
Y=`0..24`, Z=`-30..10`; üst pim sırası Z=0, alçak eğim ucu Z=-30'dur.
3659 kemerin alt bağlantıları yalnız iki uçtadır; orta iki pimlik açıklık
dolu tuğla olarak modellenmemelidir. Bu yerleşim notları resmî geometri
dosyalarının yorumudur; fiziksel kavrama/sağlamlık testi yerine geçmez.

[6108 büyük kemerin](https://library.ldraw.org/library/official/parts/6108.dat)
yerel gövde sınırları X=`-120..120`, Y=`0..72`, Z=`-10..10`'dur. Altta yalnız
X=±110, Z=0 noktaları Y=72 düzleminde bağlanır. Üst pimleri basamaklıdır:
X=±110 için Y=48, X=±90 için Y=24 ve X=-70,-50,-30,-10,10,30,50,70 için
Y=0. Böylece üstteki on iki pim aynı düzlemdeymiş gibi destek sayılmaz.
[6108 renk kartları](https://www.bricklink.com/catalogColors.asp?itemType=P&itemNo=6108)
Tan ve Light Bluish Gray'i doğrular. Alternatif 14707 için de aynı iki renk
kartı gözlenmiştir; bu, iki kalıbın geometrik olarak birebir değiştirilebilir
olduğuna ilişkin bir doğrulama değildir.

[54200 küçük eğimin](https://library.ldraw.org/library/official/parts/54200.dat)
yuvarlatılmış gerçek gövdesi X/Z=`-10..10`, Y=`-15.6..0` aralığındadır.
Alt bağlantı merkezde Y=0'dadır; üst pim yoktur. Alçak kenar Z=-10/Y=-4,
yüksek yassı tepe Z=10/Y=-15.6'dır. Tan ve Light Bluish Gray
[renk kartları](https://www.bricklink.com/catalogColors.asp?itemType=P&itemNo=54200)
doğrulanmıştır.

## LEGO Architecture 21056 incelemesi

Resmî [21056 talimat sayfası](https://www.lego.com/en-us/service/building-instructions/21056)
üzerindeki [6398433 PDF](https://www.lego.com/cdn/product-assets/product.bi.core.pdf/6398433.pdf)
yalnız araştırma için geçici klasöre indirilmiştir; sayfaları teslim paketine
konulmamıştır. PDF'nin basılı 116. sayfasında ana kubbenin yanlara bağlantılı
çekirdek ve dört büyük kavisli panelle kurulması; 121–122. sayfalarda açık
taşıyıcı halka üstüne küçük düz kubbe, çanak ve ince tepelik yerleştirilmesi;
124–126. sayfalarda ince kule gövdesinin geniş halka ve çanaklarla bölünmesi
incelenmiştir. Ayasofya'ya aktarılan tasarım ilkeleri, küçük kubbelerde düzgün
kavis, belirgin kornişler, açık korkuluklar ve cepheye farklı yönlerde takılan
detaylardır. Tac Mahal'in soğan kubbe silueti Ayasofya için doğrudan kopyalanmaz.

Küçük kubbenin kesin parça kimliği **49308**, ayrıca
[BrickLink 21056 envanterinde](https://www.bricklink.com/catalogItemInv.asp?S=21056-1&bt=1&sortAsc=A&sortBy=0&viewCodes=Y)
doğrulanmıştır. 86500 farklı bir 4×4 düz kubbe kabuğudur; üst pimi yoktur ve
standart alt pim yuvaları varsayılamaz. Bu nedenle 49308'in doğrudan eşdeğeri
olarak kullanılmaz.

Yeni adaylarda gerçek renk kartı doğrulaması (stok garantisi değildir):

| BrickLink ID | İşlev | Kartı bulunan hedef renkler |
|---|---|---|
| 49308 | 3×3 açık üst pimli küçük kubbe | 86, 69, 115 |
| 3960 | 4×4 çanak / geniş korniş | 2, 86, 69, 115 |
| 4740 | 2×2 çanak / başlık | 2, 86, 69, 115 |
| 4032 | 2×2 yuvarlak plaka; LDraw 4032a | 2, 86, 69, 115 |
| 30055 | 1×4×2 açık parmaklıklı korkuluk | 2, 86, 115 |
| 3633 | 1×4 kafes korkuluk | 2, 86, 115 |
| 60592 | 1×2×2 pencere çerçevesi | 2, 86, 115 |
| 30044 | Kemerli pencere çerçevesi | 2, 86 |
| 30046 | Kafes pencere eki | 115 |
| 2877 | Çift yönlü oluklu 1×2 tuğla | 2, 86 |
| 30136 | Yuvarlak kabartmalı 1×2 tuğla | 2, 86, 69 |
| 4070 | Gömülü yan pimli 1×1 tuğla | 2, 86, 69 |
| 87087 | Yan pimli 1×1 tuğla | 2, 86, 69 |
| 98138 | 1×1 yuvarlak karo | 2, 86, 69, 115 |
| 3070 | 1×1 karo; LDraw 3070b | 2, 86, 69, 115 |
| 3794b | Tek merkez pimli 1×2 plaka | 2, 86 |
| 64644 | Teleskop / ince sütun adayı | 2, 86, 115 |
| 43888 | Destek / sütun adayı | 2, 86, 115 |
| 32952 | Yan bağlantılı cephe desteği | 2 |

Her satır, aynı ID ile `catalogColors.asp` sayfasındaki eşleşen görsel kartından
doğrulanmıştır. Bu aday tablosu kullanım taahhüdü değildir; geometriye uygun
bağlantı ve son CSV doğrulaması ayrıca gerekir.

Makine tarafından okunabilir sonuç `dist/katalog-dogrulama.json` içindedir.
Her kaynak için alınma zamanı (UTC), yanıtın SHA-256 özeti ve gözlenen renk
numaraları; her çift için gerçek HTML kanıtı ve görsel adresi saklanır. CSV'nin
SHA-256 özeti, sonucun hangi alışveriş listesine ait olduğunu gösterir.

Yeniden çalıştırma:

```sh
python3 scripts/verify_catalog.py
```

Kaydedilmiş ham sayfalar varsayılan olarak `/tmp/ayasofya-bricklink-catalog`
klasöründedir. Aynı yerel kanıtlarla çevrimdışı tekrarlamak için
`python3 scripts/verify_catalog.py --offline` kullanılabilir. Geçici önbellek
teslim paketinin parçası değildir; rapor ilgili kanıt kesitlerini içerir.

Kapsam dışı: güncel satıcı stoğu, fiyat, istenen miktarın bulunabilirliği,
nadirlik, kargo, parçanın fiziksel durumu ve modelin yapısal sağlamlığı.
Doğrulanamayan çiftler `unknown` olarak kalır ve komut başarısız çıkış kodu verir.
