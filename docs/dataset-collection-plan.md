# Veri toplama planı — ilk sürümde 5–10 metre

Karar tarihi: 25 Ekim 2026.

Kullanıcı platformun farklı yüksekliklerden bulunmasını ve takip edilmesini istedi; geniş görüş alanının sabit kalmasını seçti. Ardından ilk sürümün üst çalışma yüksekliğini asistanın önermesini istedi. Mevcut kamera ve işlem hattını koruyarak ilk hedef aralık 5–10 metre olarak seçildi.

## Sabit koşullar

- Platformun fiziksel boyutu tüm kayıtlarda 2 × 2 metre kalır.
- Kamera aşağı bakar; yatay görüş açısı 2.0 radyan (yaklaşık 114,6 derece) ve zoom 1 olarak sabit tutulur.
- Mevcut ham görüntü 640 × 480 pikseldir. Modelin 416 giriş boyutu ilk deney ayarıdır; ham görüntüler orijinal çözünürlükte saklanır.
- Veri toplama yükseklikleri yaklaşık 5, 8 ve 10 metredir. Kullanıcı uçuş komutunda 7,5 için `Bad alt` aldığını bildirdiğinden ara yükseklik 8 metreye değiştirildi. İlk kapalı çevrim hizalanma deneyi yol haritasındaki yaklaşık 5 metre koşulunu korur. Diğer yüksekliklerde hareket kontrolü ayrıca doğrulanır.
- 10 metre bu sürümün doğrulanacak üst hedefidir; henüz eğitilmiş modelle kanıtlanmış menzil değildir.

## Görüntüdeki hedef boyutu

İdeal, aşağı bakan ve platformla eksenleri hizalı kamera için hesap:

```text
f_x = görüntü_genişliği / (2 × tan(yatay_görüş_açısı / 2))
platform_genişliği_px ≈ f_x × platform_genişliği_m / kamera_platform_mesafesi_m
```

| Yaklaşık mesafe | Ham 640 piksel genişlikte platform | 416 girişe ölçeklendiğinde |
|---|---:|---:|
| 5 m | 82,2 px | 53,4 px |
| 8 m | 51,4 px | 33,4 px |
| 10 m | 41,1 px | 26,7 px |

Bunlar geometrik tahminlerdir. Kamera ile platform arasındaki gerçek mesafe, yaw, platformun kadrajdaki yeri ve kamera ayarları gerçek kutuyu etkiler. Kaynak: [OpenCV kamera izdüşüm modeli](https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html). Model girişinde görüntü ölçekleme/padding davranışı için [Ultralytics belgesi](https://docs.ultralytics.com/modes/predict/#inference-arguments).

20 metrede ham genişlik yaklaşık 20,5 piksel, 50 metrede 8,2 piksel olur. Bu uzaklıklar bu sürümün başarı iddiasına dahil değildir. Daha sonra geniş görüşü koruyan yüksek çözünürlük ve uygun çıkarım seçenekleriyle ayrı bir aşama olarak incelenebilir.

## Önce küçük bir pilot

1. Kaydediciye görüntüyle eşleşen `manifest.csv` kaydını ekle. En az sahne, oturum, kaynak zaman damgası, boyutlar, kamera profili ve nominal yükseklik belli olsun.
2. Her yükseklikte 10–15 farklı kadraj al. Platform merkezde, kenarlarda ve birkaç yatay ofsette görünsün; yalnızca aynı konumda bekleyerek sayıyı doldurma.
3. Orijinal PNG'leri ve modelin kullanacağı giriş boyutuna küçültülmüş görünümü incele. 10 metre grubunda fiziksel dış sınırın etiketlenebildiğini kontrol et.
4. Hatalı görüntü, yanlış kamera yönü veya tutarsız metadata varsa büyük toplama oturumundan önce düzelt.

Yerde yapılan `recorder_check` kayıtları araç testidir; eğitim verisine eklenmez. Nominal yükseklik komutla hedeflenen yaklaşık değerdir; gerçek ölçüm alanı gibi kullanılmaz.

## İlk veri kümesi bütçesi

Başlangıç önerisi: 12 bağımsız sahne grubu × 3 yükseklik × 15 kullanılabilir görüntü = yaklaşık 540 görüntü. Bu sayı başarı garantisi değildir; ilk eğitim ve hata incelemesinden sonra ihtiyaç olan koşullara yeni veri eklenir.

Her sahne/yükseklik grubunda yaklaşık 12 pozitif ve 3 negatif görüntü hedeflenir: toplamda 432 pozitif, 108 negatif. Pozitiflerin farklı kadrajlar içermesi esastır.

Sahne grupları 2–3 platform görünümü, 3–4 zemin ve farklı ışık/gölge koşullarına dağıtılır. Negatifler platformun bulunmadığı gerçek simülasyon görüntüleridir; benzer renkli zemin işaretleri veya farklı nesneler de içerebilir. Aynı platform kategorisini bir görüntüde pozitif, diğerinde negatif olarak etiketleme.

## Bölme ve takip değerlendirmesi

- Sahne gruplarını baştan ayır: 8 eğitim, 2 doğrulama, 2 test. Planlanan bütçede yaklaşık 360/90/90 görüntü olur.
- Bir sahnenin 5, 8 ve 10 metre oturumları aynı kümede kalır. Aynı sahneye yeni oturum adı vermek onu bağımsız sahne yapmaz.
- Her kümede üç yükseklik de temsil edilir. Performans her yükseklik için ayrı raporlanır: kaçırılan hedefler, yanlış pozitifler ve merkez hatası.
- Takip değerlendirmesi için ayrıca kaynak zaman damgalı ardışık sekanslar tutulur. Saniyede bir PNG toplamak tek başına hızlı ve kararlı takip kanıtı değildir. Tespit kesintileri, merkez titreşimi ve gecikme bu sekanslarda değerlendirilir.

## Mevcut durum

CSV'li tam kaynak dosyada dosya eşleşmesi/hata durumları beş testle doğrulandı. Kullanıcının Ubuntu'da topladığı 141 görüntülük 5/8/10 metre pilotu da [canlı kayıt denetiminden](../reports/recording_audit_2026-10-25.md) geçti. Her oturum kendi manifestini tutar; `image_path` o manifestin klasörüne göredir. Parametreler ve komutlar [kayıt kılavuzunda](day-04-recording.md). Sahne çeşitleri, negatif örnekler, etiketleme ve eğitilmiş model değerlendirmesi henüz tamamlanmadı.
