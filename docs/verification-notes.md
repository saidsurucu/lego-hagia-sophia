# Doğrulama notları — ilk sürüm

6 Eylül 2026 teslimi: 2.427 parça, 17 tür, 6 renk, 44 katalog kalemi,
47 katman adımı. Fiziksel montaj yapılmadı.

## Tespit edilip giderilen sorunlar

- İlk çatı döşemesi, iç destek şeritleri arasına alttan bağlantısız küçük
  plakalar yerleştiriyordu. Büyük dikdörtgenleri önce döşemek parça sayısını
  2.771'den 2.424'e indirdi; kalan tek destek boşluğu bir iç payeyle giderildi.
  Son parça sayısı 2.427 oldu.
- İlk LDR önizlemesi bir dışa aktarım hatasını gösterdi. LDraw temel
  dikdörtgen parçalarında uzun kenar X eksenindedir; yerleşim motoru ise
  katalog adındaki kısa × uzun boyutları kullanır. Dönüşüm sınırda düzeltildi.
  Hem 3035 resmî boyutlarıyla regresyon testi hem tüm gerçek geometrileri
  bağımsız çözen denetim eklendi. Hatalı dönüşüm kasıtlı geri konduğunda
  bağımsız kontrol 40 LDU uyuşmazlığıyla başarısız oldu.
- BrickLink, LDraw 3068b karosunu 3068 altında listeliyor. Alışveriş kodu
  ayrı alana taşındı. Görsel katalog kanıtı bulunamayan iki Dark Tan 3031
  yerine Tan 3031 kullanıldı.
- Dış yükseklik, minare külahının 4 LDU uç çıkıntısını da kapsayacak şekilde
  23,84 cm olarak raporlandı; gövde sınırı 23,68 cm.

## Kontrol sonuçları

- 12 otomatik test geçti; kapsam ana README'de.
- 2.427 kaydın resmî LDraw mesh sınırlarında sıfır uyuşmazlık.
- Sıfır muhafazakâr gövde çakışması, sıfır alttan bağlantısız üst parça,
  tek bağlantı bileşeni, 3.821 parça bağlantısı.
- Bir studa bağlı 414 parçanın tamamı 1×1 parça. Bütün 49 yuvarlak 2×2
  tuğla ve dört külah, altlarında dört studa bağlı.
- Güncel CSV'nin SHA-256 özetiyle eşleşen 44/44 katalog kanıtı.
- İki 1800 × 1500 Blender önizlemesi görsel olarak incelendi.
- HTML rehberde 47 adım / 2.427 yerleşim; ileri/geri, son adım sınırı,
  tüm adımlar düğmesi ve yerel dosya bağlantıları çalışıyor.
- Masaüstünde ve 390 px mobil görünümde yatay taşma yok.

Bağımsız inceleme kritik/önemli bir yerleşim, montaj sırası veya dışa aktarma
hatası bulmadı. Mesh sınırı kontrolü ayrıntılı mekanik simülasyon değildir;
katalog görsel kaydı da güncel miktar/fiyat garantisi değildir.


# Fotoğraf referansına göre ikinci sürüm

Kullanıcının paylaştığı Ayasofya fotoğrafına göre ana kubbe basıklaştırıldı,
çatılar açık griye çevrildi, koyu kasnak inceltildi. Güney/kuzey cephesinde
büyük taş kemer deseni ve sıcak tuğla renkli alınlık oluşturuldu. Güneyde
üç küçük kubbeli ek yapı ve altın renkli alemler eklendi. Kemer dolu cephe
üzerinde plaka desenidir; gerçek açıklık değildir.

Sonuç: 2.702 parça, 18 tür, 9 renk, 57 katalog kalemi, 49 katman.
Taban 38,4 × 38,4 cm; en yüksek minare uç studu dahil 21,92 cm.
12 test ve 2.702 gerçek LDraw sınır kontrolü geçti. Sıfır çakışma, sıfır
alttan bağlantısız üst parça, tek bileşen, 4.109 bağlantı. 57/57 katalog
eşleşmesi doğrulandı; 3062b LDraw adı BrickLink 3062 olarak dışa aktarılır,
4073 değişmeden kalır. Bir studa bağlı 452 parçanın tamamı 1×1 ölçüsündedir.
Görseller aynı LDR'den tekrar üretildi. İlk sürüm archives/ayasofya-v1.zip
içinde korunur. Fiziksel montaj veya dayanım deneyi yapılmadı.


## Revizyon 03 — çok açılı fotoğraf iterasyonu

3.016 parça, 20 parça türü, 9 renk, 64 parça-renk kalemi; 56 katman adımı.
İlk turda 2.869 parçayla payandalar, yükseltilmiş kasnaklar ve ince minare
uçları karşılaştırıldı. İkinci turda dört ikincil yarım kubbe, doğu
pencereleri, yuvarlak tuğla minare ve farklı yükseklikte ek yapılar eklendi.
Yeni çatı yerleşiminin oluşturduğu iki desteksiz infill plakasının altına
düşey destek eklendi; ikincil kubbelerle kesişen yan nef çatı alanları çıkarıldı.

19 test geçti; 3.016 gerçek parça geometrisinin sınır kontrolünde hata yok.
64/64 katalog renk kartı doğrulandı. Gövde çakışması ve desteksiz parça sıfır;
4.618 bağlantıyla tek ağ. Tek studdan desteklenen 552 parçanın hepsi 1×1.
Yarım stud koordinatları ve 3942c/87580 merkez studları ayrıca test edildi.
Fiziksel kurulum ve tutunma kuvveti test edilmedi. Kaynaklar ve görsel
karşılaştırma [fotoğraf kaydında](photo-comparison.md).

Rehber tarayıcı kontrolü: 56 adım ve 3.016 yerleşim; sonraki adım ve
tüm adımları göster kontrolleri çalışıyor. 1280×900 görünümde yatay taşma yok.
Yarım stud yerleşim açıklaması mevcut.


## Revizyon04 — biçimli parça geometrisi

Son model3.482 yerleşim,31 tür,9 renk,75 alışveriş kalemi,53 katman adımıdır.
32 test geçer;3.482 gerçek LDraw ağının yerel orijini, kardinal dönüşümü ve
sınırları bağımsız denetimde eşleşir.75/75 katalog renk kartı doğrulanmıştır.
Çakışma/desteksiz/taban dışı parça sıfır;5.294 bağlantıyla tek bileşen.

15068/11477 yüksek alt sıralarının bir plaka boşluğu resmî alt parça
geometrisinden iki ayrı incelemeyle doğrulandı.196 plakayla bu boşluklar
dolduruldu.122 geniş kavisli parçada dört,74 dar kavisli parçada iki bağlantı
vardır.647 tek bağlantılı parçanın hepsi1×1. Kemer alt boşlukları çakışma
denetiminde muhafazakâr zarfla temsil edilir;6108 üst basamaklarının üç
farklı yüksekliği ile kavis altlarındaki boşluklar özel olarak modellenir.

Destek plakaları aynı katmandaki kavislerden önce sıralanır. JSON veLDR
yerleşim sırası için regresyon testi eklendi; bağımsız gerçek geometri
denetimi de bu sırayı kontrol eder. Rehberin ilgili adımlarında destek
vekaplama ayrı planlarda sunulur. Fiziksel montaj yapılmadı.

Revizyon04 rehber statik kontrolü:53 adım,3.482 yerleşim,24 ayrı iki aşamalı
çatı planı; yinelenenHTML/SVG kimliği veya eksik yerel bağlantı yok.


## Revizyon 05 — Architecture parçaları ve yan bağlantılar

3.605 parça, 46 tür, 9 renk, 100 alışveriş kalemi, 56 katman. 44 test geçti.
Gövde çakışması, desteksiz ve taban dışı parça sıfır; 5.440 bağlantıyla tek ağ.
Alt/üst pimlerin yanında 87087 ve 32952 taşıyıcılarının yan portları da
konum ve normal yönüyle modellenir. Düz yüzey teması bağlantı sayılmaz.
Yan parça pozu LDraw dışa aktarımında gerçek yerel eksenlerle hesaplanır.

Altı düşey 2412b ızgaranın ikişer, dört 98138 madalyonun birer yan bağlantısı
vardır. Sekiz 60592 çerçevenin iki alt pimi de desteklidir. 49308 şadırvan
kubbesinin dört alt bağlantısı vardır. Altı çanak merkezlerinden bağlanır.
776 tek bağlantılı parçanın 12'si 1×1'den büyüktür: altı çanak ve nişlerin
üzerinde bir studdan desteklenen altı 3004 tuğla. İkinciler üst sırada
3010 tuğlalarıyla bağlanır. Fiziksel dayanım testi yapılmadı.

Rehber statik kontrolü: 56 adımın yerleşim toplamı 3.605; on yan montaj
satırında doğru taşıyıcı, 1 tabanlı koordinat ve yön bulunur. Yan parçalar
üstten dik yerleşim planında yatay karo gibi gösterilmez. Taşıyıcı önce,
yan süs sonra takılır. Ana rehberde Revizyon 05 yazısı bulunur.

Bağımsız gerçek LDraw denetimi 3.605 kaydın tamamını ve on yan montajı
doğruladı; sınır veya yön uyuşmazlığı yok. Güncel CSV özetiyle eşleşen
100/100 parça-renk kartı doğrulandı. Rehberde 139 benzersiz HTML/SVG
kimliği ve yedi mevcut yerel görsel/dosya bağlantısı kontrol edildi.

Son dört önizleme yeni LDR dosyasından üretildi ve görsel olarak incelendi.
Ön ve kuzeydoğu 3840×3200, doğu ve batı 1800×1500 pikseldir. Dört PNG ve
dört Blender sahnesinin modelden sonra güncellendiği kontrol edildi.


## Revizyon 06 — kubbe eğrisi ve dik alt kuşak

3.849 yerleşim, 47 tür, 9 renk, 101 alışveriş kalemi, 61 katman.
Ana kubbe çapı 20 stud; yükselişi 12 yerine 18 plaka. Küresel başlık profili,
88 adet 3040b dik eğim ve üstte 64 dar kavisli parçayla kurulur. Gerçek
3040b dosyasının asimetrik orijini, tek üst studu ve iki alt bağlantısı
ayrıca kontrol edildi; BrickLink numarası 3040'tır.

45 test, 3.849 gerçek LDraw sınır/dönüş kontrolü ve 101/101 renk kaydı geçti.
Sıfır çakışma/desteksiz/taban dışı parça; 5.856 kenarla tek bağlantı ağı.
918 tek bağlantılı parçanın 12'si 1×1'den büyüktür: önceki altı çanak ve
altı niş üstü tuğla. Yeni 88 dik eğimin her biri iki, tüm 118 dar kavisin
her biri iki, 54 geniş kavisin her biri dört alt pime bağlanır.
172 yükseltilmiş alt sıra dolgusu kaplamadan önce yerleştirilir.
Gemini ile görsel inceleme, mekanik doğrulamadan ayrı tutuldu.

Revizyon 06 rehber statik kontrolü: 61 adım / 3.849 yerleşim, on yan
montaj satırı, 146 benzersiz HTML/SVG kimliği ve yedi mevcut yerel bağlantı.

Dört son PNG ve dört Blender sahnesi güncel modelden yeniden üretildi;
ön/arka 3840×3200, doğu/batı 1800×1500 boyutları ve güncellikleri doğrulandı.
Dört açı da görsel olarak incelendi.
