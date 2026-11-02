# Gün 4 — PNG ve CSV kaydı

Tam kaynak dosya: `ros_ws/src/drone_alignment/drone_alignment/dataset_recorder.py`.

## Oturum düzeni

```text
datasets/platform/
  scene01/
    session_20261025_...
      manifest.csv
      scene01_session_20261025_..._frame000001.png
```

Her oturum kendi `manifest.csv` dosyasını tutar. Bu, farklı oturumların aynı dosyaya eşzamanlı yazmasını önler. Sonraki toplu veri araçları oturum manifestlerini birlikte okuyacak. `image_path`, satırın bulunduğu manifestin klasörüne göre dosya adıdır.

Başlık alanları:

```text
image_id,scene_id,session_id,image_path,source_stamp_ns,width,height,platform_variant,ground_variant,light_variant,nominal_height_m,notes,camera_profile
```

`source_stamp_ns` görüntünün kendi kamera zaman damgasıdır. Kayıt sıklığı bu damgaların farkıyla sınırlandırılır. Varsayılan oturum adı her çalıştırmada üretilir; elle aynı oturum kimliği verilirse var olan oturumun üzerine yazılmaz.

## Yeni parametreler

- `nominal_height_m`: Komutla hedeflenen yaklaşık yükseklik; ölçülmüş telemetri değildir. Varsayılan `-1.0`, CSV'de boş alan olarak saklanır. Yerde yapılan testlerde yüksekliği uydurma.
- `platform_variant`, `ground_variant`, `light_variant`: Oturumun fiziksel koşulları.
- `camera_profile`: Varsayılan `iris_wide_640x480_hfov2_zoom1`; kamera profilini değiştirdiğinde bu bilgiyi de düzelt.
- `notes`: Serbest oturum açıklaması. Virgül/tırnak/satır sonları CSV yazıcısı tarafından işlenir.

Parametreler başlangıçta okunur. İrtifa değiştiğinde nominal yükseklik kendiliğinden değişmez: kaydı durdur, yeni yükseklikte sabitlen, doğru parametreyle yeni oturum başlat. Aynı sahnenin bütün yükseklikleri aynı `scene_id` altında ve aynı veri kümesi bölümünde kalır.

## İlk araç testi

Gazebo, SITL ve görüntü köprüsü açıkken ayrı Ubuntu terminalinde:

```bash
source /opt/ros/jazzy/setup.bash
cd ~/projects/aeroalign
source .venv/bin/activate

python ros_ws/src/drone_alignment/drone_alignment/dataset_recorder.py \
  --ros-args -p use_sim_time:=true \
  -p scene_id:=recorder_csv_check \
  -p save_interval_s:=1.0
```

5 kayıt logundan sonra Ctrl+C ile durdur. Bu yerde yapılan araç testidir; eğitim verisi değildir.

## Gerçek veri toplama

Kamera aşağı bakarken ve drone hedef yükseklikte sabitlendikten sonra kaydı başlat. Örneğin 5 metrelik oturum:

```bash
python ros_ws/src/drone_alignment/drone_alignment/dataset_recorder.py \
  --ros-args -p use_sim_time:=true \
  -p scene_id:=scene01 \
  -p nominal_height_m:=5.0 \
  -p save_interval_s:=1.0
```

8 ve 10 metre oturumlarında sırasıyla `8.0` ve `10.0` kullan. Uçuş tarafında seçilen ara yükseklik 8 metredir; kaydedicinin ROS parametresi ondalıklı sayı olduğu için `8.0` yazılır. Kalkış, irtifa değiştirme veya iniş görüntülerini sabit yükseklik oturumuna katma. Yakın kopyalar üretmek yerine farklı yatay konum/kadrajlar topla. Ayrıntılı bütçe ve bölme kuralları [veri toplama planında](dataset-collection-plan.md).

## Doğrulama durumu

Windows'ta gerçek dosyalarla beş test geçti: PNG/CSV eşleşmesi ve metin kaçışları, mevcut görüntüyü koruma, kısmi CSV yazma hatasında geri alma/yeniden deneme, eksik manifestte PNG bırakmama ve bilinmeyen yüksekliği boş bırakma. Testler üretimdeki I/O fonksiyonunu değiştirmeden çalıştırır; Windows'ta ROS bağımlılıkları yüklenmez.

Python sözdizimi kontrolü geçti. Kullanıcının Ubuntu'da aldığı 5/8/10 metre oturumları SSH üzerinden kontrol edildi: 141 PNG ve 141 CSV satırı eşleşiyor; görüntüler açılıyor, boyutlar ve zaman damgaları tutarlı. Ayrıntılar [denetim raporunda](../reports/recording_audit_2026-10-25.md). Etiketleme ve veri çeşitliliği çalışmaları henüz tamamlanmadı.
