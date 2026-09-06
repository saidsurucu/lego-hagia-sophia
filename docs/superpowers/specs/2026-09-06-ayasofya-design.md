# Ayasofya LEGO modeli — onaylanan tasarım

Kullanıcı 6 Eylül 2026 tarihinde yaklaşık 2.000 parçalık, yaklaşık 40 × 40 cm
tabanlı Ayasofya modelini, LDraw dosyasını, alışveriş listesini ve önizlemeyi
onayladı. Bu klasör başlangıçta boştu ve Git deposu değildi.

## Model

- Taban: 48 × 48 stud, 38,4 × 38,4 cm; hedef 1.500–2.500 parça.
- Dış mimari: basık ana kubbe, doğu/batı yarım kubbeleri, dört farklı minare,
  cephe pencereleri, payandalar, bej taş ve tuğla renkleri.
- Yalnız katalogda bulunan LEGO parça/renk eşleşmeleri. Özel baskı, kesme,
  yapıştırma, parça esnetme ve özel üretilmiş geometri yok.
- Standart dikey stud bağlantıları, şaşırtmalı plaka tabanı, iç destekler.
- İç mekân sergilemesi ve birebir rölöve bu ölçeğin kapsamına dahil değil.

## Teslimler

`dist/ayasofya.ldr`, `dist/parca-listesi.csv`, `dist/bricklink-wanted.xml`,
`dist/ayasofya.png`, yapım sırasını açıklayan Türkçe rehber ve katman adımları.
LDR içindeki STEP satırları parçalar eklenirken takip edilebilir olmalı.
Üretici kodu, katalog kaynakları ve doğrulama raporu da teslim edilir.

## Doğrulamanın kapsamı

Parça gövdelerinin hacim çakışması, standart stud bağlantılarından oluşan tek
bağlantı bileşeni, her eklenen üst parçanın alt desteği, parça/renk katalog
eşleşmeleri ve LDraw/CSV/XML adet tutarlılığı kontrol edilir. Yuvarlak parçalar
için muhafazakâr dikdörtgen dış zarf kullanılır. Fiziksel dayanım ve tolerans
simülasyonu yapılmış gibi sunulmaz; fiziksel montaj yapılmadığı belirtilir.

## Teknik yapı

Python standart kütüphanesiyle deterministik model, doğrulama ve dışa aktarım.
Resmî LDraw parça geometrisinden Blender ile önizleme. Üretici, geometri
doğrulaması ve sunum araçları ayrı dosyalarda tutulur. Ağ bağlantısı sadece
parça geometrisini ve katalog kanıtlarını edinirken gerekir.
