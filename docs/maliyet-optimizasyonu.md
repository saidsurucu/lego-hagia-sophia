# İç dolgu optimizasyonu — 9 Eylül 2026

4.149 → 3.951 parça; 198 parça (%4,77) azalma. Değiştirilen kapalı iç
bölgelerde 529 yerleşim yerine 331 yerleşim kullanıldı. Yeni yerleşimlerde
124 adet 3007 (2×8), 5 adet 2456 (2×6), 10 adet 3009 (1×6) gri tuğla var.
Diğer yerleşimler dar alanları ve plaka yüksekliğindeki farkları tamamlar.

Dıştan erişilebilir boşluklar yalnız sıradan dikdörtgen tuğla ve plakalarla
sınırlanarak bulunur. Pencere, kemer, kavis gibi özel parçalar bu hesapta
boş sayılır; dolayısıyla yalnız kutu sınırıyla bir pencereyi kapalı sayma
hatası yapılmaz. Açık havaya komşu herhangi bir hücresi bulunan parçanın
tamamı korunur. Tabanın üç şaşırtmalı katına dokunulmaz.

Kalan iç parçalar bölüm bazında aynı dolu hacme yeniden döşenir; gizli renk
ayrımları açık mavimsi griye birleştirilir. Üç plaka yüksekliği uygun
olduğunda bir tuğla kullanılır; kalan yükseklik plakalarla tamamlanır.
Bir bölümde yeni döşeme parça sayısını düşürmüyorsa eski parçalar korunur.
Boşluk doldurulmaz; dış kabuğun parça kimliği, rengi, yönü ve konumu korunur.

48 test geçti: tam hacim eşitliği, dış parçaların korunması, tabanın korunması,
açılan deliğin gizli parçayı görünür yapması, montaj sırası ve mevcut geometri
kontrolleri dahil. 3.951 gerçek LDraw geometrisinde sınır hatası yok;
98/98 parça-renk eşleşmesi katalog görsel kayıtlarında doğrulandı.
Tek bağlantı ağı, sıfır çakışma, sıfır desteksiz parça. Fiziksel montaj yapılmadı.

Bu işlem parasal fiyat minimumunu bulmaz. BrickLink fiyat sayfası kullanılabilir
teklif döndürmedi. Büyük tuğlaların güncel fiyatlarının, kaldırılan parçaların
toplamından düşük olduğu ayrıca satıcı bazında kontrol edilmelidir.
`dist/parca-degisimleri.csv` miktar farklarını verir; pozitif fark alınacak,
negatif fark azaltılacak miktardır. Aynı durum/para birimindeki birim fiyatla
çarpılan farkların toplamı parça bedeli değişimidir; kargo ayrıca eklenir.
Nadir görünen dış parçaların şekli veya yüzey dokusu değiştirilmedi.

Model ve rapor: `python3 -m scripts.build_model`.
Optimizasyonsuz önceki yerleşimler: `scripts.build_model.build(optimize=False)`.
