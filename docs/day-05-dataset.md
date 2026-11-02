# Gün 5 — platform_v1 veri kümesi

Sahne ve ayrım kararı [`configs/dataset_v1.json`](../configs/dataset_v1.json) dosyasındadır. Bu dosya veri kümesinin sürümüdür (`platform_v1`); yeni veri eklenirse yeni bir sürüm dosyası açılır, bu dosya değiştirilmez.

## Sahne grupları ve ayrım

| Sahne | Zemin | Işık | Platform | Seed | Küme |
|---|---|---|---|---:|---|
| `sim01` | gri | varsayılan | turuncu | 501 | train |
| `sim02` | gri | alçak güneş | mavi | 502 | train |
| `sim03` | gri | loş | turuncu | 503 | **test** |
| `sim04` | kum | varsayılan | mavi | 504 | train |
| `sim05` | kum | alçak güneş | turuncu | 505 | train |
| `sim06` | kum | loş | mavi | 506 | **val** |
| `sim07` | asfalt | varsayılan | turuncu | 507 | train |
| `sim08` | asfalt | alçak güneş | mavi | 508 | **test** |
| `sim09` | asfalt | loş | turuncu | 509 | train |
| `sim10` | çim | varsayılan | mavi | 510 | train |
| `sim11` | çim | alçak güneş | turuncu | 511 | **val** |
| `sim12` | çim | loş | mavi | 512 | train |

Gerekçe:

- Train kümesinde her zemin 2 kez, her ışık en az 2 kez, her platform görünümü 4 kez var.
- Val ve test kümelerinin her birinde iki platform görünümü de var.
- Val/test sahnelerindeki zemin ve ışık eğitimde ayrı ayrı görülür, ama aynı zemin+ışık ikilisi hiçbir train sahnesinde yoktur: "eğitime benzer ama aynı olmayan" koşul.
- Bir sahnenin 5, 8 ve 10 metre oturumlarının hepsi aynı kümededir.

Her sahne `scene_capture.py` ile çekildi: her yükseklikte 12 pozitif + 3 negatif, yani sahne başına 45 görüntü. Kamera konumu, yaw, platformun kadrajdaki yeri ve dikkat dağıtıcılar her karede değişir; kayıt sıklığını artırarak sayı doldurulmadı.

## Uçuş görüntüleri: `flight_eval`

25 Ekim'de uçuşla alınan 141 görüntü (`scene01`, gri zemin, turuncu platform) `flight_eval` adlı ayrı kümededir. Bunlar gerçek gimbal kamerasından gelir. Simülasyon kamerasıyla eğitilen modelin gerçek uçuş görünümüne ne kadar taşındığını ölçmek için kullanılır; eğitimde kullanılmaz. Bu kümede negatif yoktur ve hepsi aynı sahnedendir. Bu yüzden sonuçları ayrı raporlanır.

Hariç tutulanlar: `recorder_check`, `recorder_csv_check` (araç testleri) ve `pilot04_*` (Gün 4 sahne kontrolü).

## Ayrımı üretmek

```bash
cd ~/projects/aeroalign
source .venv/bin/activate
python scripts/build_split.py --backup
```

Betik şunları yapar:

1. Her oturumu doğrular: manifest satırları ve PNG dosyaları birebir eşleşmeli, görüntüler açılmalı, boyutları manifestle aynı olmalı, zaman damgaları artmalı, zorunlu alanlar boş olmamalı.
2. Her çekim sahnesinde her yükseklik için tam bir oturum olduğunu kontrol eder.
3. Birebir aynı PNG'leri (SHA-256) ayıklar; ilk görülen kalır.
4. `datasets/platform/platform_v1/split_manifest.csv` (`image_id,scene_id,session_id,split,image_path`) ve `summary.json` yazar. `image_path`, `datasets/platform/` klasörüne göredir.
5. `--backup` verilirse ham sahneleri ve ayrımı `datasets/backups/platform_v1_raw.tar.gz` dosyasına yedekler.

`split_manifest.csv` zaten varsa betik durur. Ayrım eğitimden önce sabitlenir.

## Sonuç (2 Kasım 2026)

36 oturum çekildi; bütün oturumlar denetimden geçti. 540 simülasyon görüntüsünden 7'si ayıklandı: düz zeminde nesnesiz negatif kare her yükseklikte pikseli pikseline aynı göründüğü için başka bir yükseklikteki kopyası atıldı. Her sahnede bu karelerden en fazla biri kalır.

| Küme | Sahne | Görüntü | Pozitif | Negatif |
|---|---:|---:|---:|---:|
| train | 8 | 357 | 288 | 69 |
| val | 2 | 88 | 72 | 16 |
| test | 2 | 88 | 72 | 16 |
| **Toplam simülasyon** | 12 | **533** | 432 | 101 |
| flight_eval | 1 | 141 | 141 | 0 |

- Negatif oranı %19. Planlanan bütçe (her yükseklikte 3/15 = %20) ayıklanan boş karelerle hafifçe düştü.
- Her kümede üç yükseklik de var: train'de yükseklik başına 118–120, val ve test'te 28–30 görüntü.
- Hiçbir sahne birden fazla kümede değil.
- Yedek: `datasets/backups/platform_v1_raw.tar.gz` (681 PNG: 540 simülasyon + 141 uçuş, artı ayrım dosyaları).

Görsel kontrolde dikkat çekenler:

- Asfalt zeminde platformun koyu çerçevesi zeminle neredeyse kaynaşıyor. Etiket yine de çerçeveyi içerir.
- Pozitiflerin bir kısmında platform görüntü kenarından taşıyor. Bunlar kısmi görünüm örnekleri; Gün 6'da kutuları görüntü içinde kırpılarak etiketlenir.

Henüz yapılmayanlar: etiketler (Gün 6) ve eğitim (Gün 7).
