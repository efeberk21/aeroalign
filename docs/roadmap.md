# Görsel Platforma Hizalanan Drone — 15 Günlük Uygulama Planı

> **Uygulayıcı için:** Bu belgeyi gün gün, sırayla uygula. Kodlama bir ajanla yürütülürse `executing-plans` yaklaşımıyla tek bir adımı uygula, doğrula ve sonraki adıma geç. İşaret kutuları ilerlemeyi takip etmek içindir. Bu belge bir yol haritasıdır; aşağıdaki kurulumlar ve uçuş denemeleri henüz yapılmış değildir.

**Amaç:** Gazebo'daki drone'un aşağı bakan kamera görüntüsünde, kendi topladığın verilerle eğittiğin modeli kullanarak teslimat platformunu bulması ve komut verdiğinde platformun üzerinde hizalanıp havada beklemesi.

**Mimari:** Gazebo fizik ve kamera görüntüsünü, ArduPilot SITL uçuş kontrolünü sağlar. Görüntü ROS 2'ye taşınır; algılama düğümü platformu bulur, yaklaşma düğümü yatay hız isteği üretir, uçuş arayüzü bunu MAVLink üzerinden gönderir. Mission Planner uçuşu başlatmak ve izlemek için kullanılır.

**Teknolojiler:** Windows, VMware içindeki Ubuntu 24.04, ROS 2 Jazzy, Gazebo Harmonic, ArduPilot SITL, MAVProxy, Mission Planner, Python, OpenCV, PyTorch, Ultralytics YOLO11n ve ONNX Runtime.

**Kapsamın kaynağı:** Bu dosyanın 1–7. bölümleri, konuşmada belirlenen projenin tasarımını ve uygulama kararlarını da içerir. Ayrı bir tasarım dosyasına ihtiyaç olmadan okunabilir.

**Hazırlanma tarihi:** 21 Ekim 2026. Gün numaraları takvim tarihi değildir; başladığın tarihten itibaren çalışma oturumlarını ifade eder.

## İçindekiler

- [1. Projenin sonunda ne çalışacak?](#kapsam)
- [2. Gerçekçi süre ve çalışma yöntemi](#sure)
- [3. Kurulum ve sürüm kararları](#ortam)
- [4. Sistem, düğümler ve mesajlar](#mimari)
- [5. Klasör ve dosya düzeni](#dosyalar)
- [6. Başarı ölçütleri ve başlangıç ayarları](#olcutler)
- [7. Önce doğrulanacak riskler](#riskler)
- [Gün 1 — Ortam ve grafik kontrolü](#gun-1)
- [Gün 2 — Simüle drone ve Mission Planner](#gun-2)
- [Gün 3 — Kamera, mesajlar ve erken performans denemesi](#gun-3)
- [Gün 4 — Platform sahnesi ve veri kaydedici](#gun-4)
- [Gün 5 — Veri toplama](#gun-5)
- [Gün 6 — Etiketleme ve veri doğrulama](#gun-6)
- [Gün 7 — PyTorch temelleri ve ilk eğitim](#gun-7)
- [Gün 8 — Hataları inceleme ve ikinci deney](#gun-8)
- [Gün 9 — Canlı algılama düğümü](#gun-9)
- [Gün 10 — Modelden bağımsız kontrol ve eksen testi](#gun-10)
- [Gün 11 — Görüntüyle kapalı çevrim hizalanma](#gun-11)
- [Gün 12 — Hedef kaybı ve gecikme](#gun-12)
- [Gün 13 — Tekrarlı görev değerlendirmesi](#gun-13)
- [Gün 14 — ONNX ve hız karşılaştırması](#gun-14)
- [Gün 15 — Tekrar çalıştırma, demo ve rapor](#gun-15)
- [Ek A — Takılınca ne yapılacak?](#sorunlar)
- [Ek B — Günlük kayıt şablonu](#gunluk)
- [Ek C — İsteğe bağlı genişletmeler](#ekler)
- [Ek D — Kavram sözlüğü ve kaynaklar](#kaynaklar)

<a id="kapsam"></a>
## 1. Projenin sonunda ne çalışacak?

Demo şu sırayla ilerleyecek:

1. Gazebo sahnesi, ArduPilot SITL ve ROS 2 düğümleri açılır.
2. Windows'taki Mission Planner simüle drone'a bağlanır.
3. Drone'u Mission Planner veya MAVProxy üzerinden kaldırıp yaklaşık 5 metre yüksekliğe getirirsin.
4. Platform başlangıçta aşağı bakan kameranın görüşündedir; drone platform merkezinden yatayda yaklaşık 0,5–2 metre uzaktadır.
5. ROS 2 servisiyle yaklaşma görevini başlatırsın.
6. Eğittiğin model platformu bulur; drone görüntüdeki merkez hatasını azaltacak yönde hareket eder.
7. Platform yeterince ortalandığında drone durur ve konumunu korur.
8. Algılama, görev durumu ve ölçümler ekranda/loglarda görünür.
9. Platform kaybolduğunda veya görüntü eskidiğinde yatay hareket durdurulur; otomatik arama yapılmaz.

**Öğrenme hedefleri:** Veri ürettim ve etiketledim; önceden eğitilmiş bir modeli kendi problemime uyarladım; modeli OpenCV kullanan canlı görüntü akışına bağladım; ROS 2 düğümlerini haberleştirdim; algılamayı hareket komutuna dönüştürdüm; doğruluk, hız ve görev başarısını ölçtüm.

### Temel kapsam

- Tek drone, tek görünür platform, tek nesne sınıfı: `delivery_platform`.
- Sabit aşağı bakan kamera; yaklaşık sabit uçuş yüksekliği ve sabit yönelim.
- Başlangıçta görüş alanında bulunan platforma yatay hizalanma.
- Kendi simülasyon verinle model uyarlama; eğitim ve değerlendirme kaydı.
- Birbirinden ayrılmış algılama, yaklaşma ve uçuş arayüzü düğümleri.
- Başlat/durdur komutu, hedef kaybı davranışı, gecikme kaydı.
- PyTorch–ONNX Runtime karşılaştırması ve tekrarlanabilir demo.

### İlk 15 güne dahil olmayanlar

- Otomatik kalkış görevi, geniş alanda platform arama veya rota planlama.
- Otomatik hassas iniş, hareketli platform veya engelden kaçınma.
- SLAM, optical flow, GPS'siz tam navigasyon veya yeni bir uçuş kontrolcüsü.
- Gerçek drone'a aktarım ve gerçek dünya başarısı iddiası.
- Çoklu drone, web paneli, Docker altyapısı, TensorRT ve kapsamlı otomatik etiketleme sistemi.

Hizalanma uygulamasının mantığı, görsel olarak tanınan bir teslimat/şarj istasyonuna yaklaşmadır. Yalnızca tek renkli bir kareyi veya sabit bir kodu bulmak amaçlansaydı öğrenilmiş model gereksiz olabilirdi. Bu projede modelin işi, farklı zemin, doku, ölçek ve ışıklarda aynı nesne kategorisini ayırt etmektir. Birkaç temsilî platform görünümü ve benzer görünen olumsuz örnekler kullanacağız; sınırsız platform tasarımını tanıdığını iddia etmeyeceğiz.

<a id="sure"></a>
## 2. Gerçekçi süre ve çalışma yöntemi

Plan, günlük **yaklaşık 3–4 saat**, toplamda **45–60 saat** odaklı çalışma varsayar. Bu bir tahmindir; özellikle Gazebo/VM kurulumu ve PyTorch'a başlangıç süreyi değiştirebilir. İlk defa karşılaştığın bir kavram için ek süre ayırman normaldir. Günlük yalnızca bir saat ayırabiliyorsan aynı planı daha uzun takvime yay.

Her gün şu döngüyü uygula:

1. **15–30 dakika:** O gün gereken kavramı öğren. İlgisiz kurs bölümlerine sapma.
2. **2–2,5 saat:** Günün somut parçasını uygula.
3. **30–45 dakika:** Doğrula, hata örneklerini sakla, ölçüm al.
4. **10–15 dakika:** Günlüğü güncelle ve çalışan değişiklikleri Git'e kaydet.

**Bir sonraki güne geçiş:** Gün sonundaki kabul koşullarını sağla. Takvim yetişsin diye çalışmayan bağlantının üzerine yeni bir katman ekleme.

**İlk üç günün önemi:** İlk gün bütün sistemi bitirme hedefi koymuyoruz. İlk üç günde uçuş, kamera ve model çalıştırmanın bu ortamda uygulanabilirliğini kanıtlıyoruz. Temel altyapı üçüncü gün sonunda çalışmıyorsa veriyi ve modeli büyütmeden bu sorunu çöz.

**İlk 10 günde beklenen:** Eğitilmiş model canlı kamerayı işliyor; drone'a modelden bağımsız doğru yönde komut verilebiliyor. Tam görev, ölçüm ve ONNX teslimi için 15 günlük sürümü esas al.

<a id="ortam"></a>
## 3. Kurulum ve sürüm kararları

| Bileşen | Yer / karar | Gerekçe |
|---|---|---|
| Ubuntu 24.04 + ROS 2 Jazzy | Mevcut VMware VM | Çalışan öğrenme ortamını koru. |
| Gazebo Harmonic | Ubuntu VM | Jazzy ile önerilen eşleşme. |
| ArduPilot SITL + MAVProxy | Ubuntu VM | Simülasyon ve MAVLink yönlendirme aynı Linux ortamında kalsın. |
| Mission Planner | Windows | Mevcut yer kontrol istasyonu akışını kullan. |
| Model eğitimi | Windows, RTX 4060 | VMware içinde CUDA erişimini varsayma. |
| İlk canlı çıkarım | Ubuntu VM, CPU | Küçük modelle erkenden ölç; yeterli değilse ortam kararını değiştir. |
| Model | `yolo11n.pt` üzerinden tek sınıfa uyarlama | Küçük, belgelenmiş bir başlangıç; model ailesi araştırmasına zaman harcama. |
| Kontrol bağlantısı | ROS 2 düğümü içinde `pymavlink` | Bu kapsamda ek MAVROS/DDS kurulumu gerektirmeyen yol. |
| Modelin ikinci çalışma biçimi | ONNX Runtime, CPU | Gerçek hedef ortamında karşılaştırılabilir ölçüm. |

Ubuntu 24.04, Jazzy ve Harmonic eşleşmesi [Gazebo'nun resmî uyumluluk belgesinde](https://gazebosim.org/docs/harmonic/ros_installation/) önerilir. Bu, bütün ArduPilot eklentilerinin senin VM'inde önceden test edilmiş olduğu anlamına gelmez; ilk üç günlük doğrulama bu yüzden var. ArduPilot için güncel [Gazebo eklentisini](https://github.com/ArduPilot/ardupilot_gazebo) kullan; Gazebo Classic için yazılmış eski kurulumlarla karıştırma.

### Python ortamlarını ayır

- **Windows eğitim ortamı:** Python 3.12 sanal ortamı. CUDA destekli PyTorch kurulum komutunu [resmî seçiciden](https://pytorch.org/get-started/locally/) Windows / Pip / Python / uygun CUDA seçerek al. CUDA sürümünü tahmin ederek sabitleme.
- **Ubuntu proje ortamı:** Ubuntu'nun `/usr/bin/python3` yorumlayıcısından `--system-site-packages` ile açılan sanal ortam. Böylece apt ile kurulu `rclpy` ve `cv_bridge` görülebilir.
- ArduPilot'un kurulum betiğinin oluşturduğu ortamı proje ortamıyla karıştırma. SITL terminali kendi ortamında, ROS terminalleri proje ortamında çalışsın.
- Sistem Python'una `sudo pip` uygulama; apt'nin yönettiği paketleri topluca yükseltme.
- NumPy/OpenCV ikili uyumluluğu hatası çıkarsa önce `numpy`, `cv2` ve `cv_bridge` sürümlerini kontrol et. Rastgele sürüm düşürmek yerine çalışan bağımlılık takımını ayrı ortamda doğrula ve kaydet.
- Çalışan Windows ve Ubuntu paket listelerini ayrı dosyalara kaydet. İki ortamın `pip freeze` çıktılarının birebir aynı olması gerekmez.

### GPU ve VMware kararı

VMware'in 3B grafik hızlandırması, PyTorch'a CUDA sunmasıyla aynı şey değildir. Linux VM'e NVIDIA sürücüsü kurarak bunu çözeceğini varsayma. Modeli Windows'ta eğit, ağırlıkları VM'e kopyala. Canlı CPU çıkarımını Gazebo ile aynı anda ölç.

Gazebo grafik performansı veya CPU çıkarımı yetersizse önce kamera çözünürlüğünü ve model boyutunu azalt. Bu yeterli olmazsa **veri toplama aşamasına geçmeden** WSL 2 ya da yerel Linux seçeneğine karar ver. WSL 2 CUDA ve grafik hızlandırması sağlayabilir, ancak Gazebo performansı ayrıca doğrulanmalıdır. [Microsoft WSL GPU belgesi](https://learn.microsoft.com/en-us/windows/wsl/tutorials/gpu-compute)

<a id="mimari"></a>
## 4. Sistem, düğümler ve mesajlar

```text
Gazebo kamera ── ros_gz_bridge ── /camera/image_raw
                                      │
                               detector_node
                                      │ /platform/observation
                               approach_node
                                      │ /approach/body_velocity
                            flight_interface_node
                                      │ MAVLink
                                   MAVProxy
                                      │
                                ArduPilot SITL ↔ Gazebo fizik
                                      │
                                Mission Planner

Veri toplarken: /camera/image_raw → dataset_recorder
Değerlendirirken: Gazebo gerçek pozları → evaluation aracı → CSV/rapor
```

**Sorumluluk sınırı:** Gazebo gerçek platform/drone pozları algılama veya yaklaşma düğümüne girmeyecek. Bu bilgiler yalnızca veri etiketi üretimi ve sonuç ölçümü içindir. Drone yatay kontrol için görüntüye dayanır; ArduPilot kendi simüle sensörlerini uçuşu dengelemek için kullanmaya devam eder. Bu proje GPS'siz uçuş iddiası taşımaz.

### Düğümler

| Düğüm / araç | Girdi | Çıktı | Sorumluluk |
|---|---|---|---|
| `ros_gz_bridge` | Gazebo görüntü, kamera bilgisi, saat | `/camera/image_raw`, `/camera/camera_info`, `/clock` | Simülasyonu ROS 2'ye bağlar. |
| `detector_node` | `/camera/image_raw` | `/platform/observation`, isteğe bağlı `/platform/debug_image` | Ön işleme, model, kutu seçimi, kaynak zaman damgasının korunması. |
| `approach_node` | `/platform/observation`, `/flight/status` | `/approach/body_velocity`, `/approach/state` | Merkez hatası, durum makinesi, başlat/durdur, hedef kaybı. |
| `flight_interface_node` | `/approach/body_velocity`, MAVLink telemetri | MAVLink hız komutları, `/flight/status`, CSV | Tek MAVLink yazıcısı; uçuş modu ve komut yaşı denetimi. |
| `dataset_recorder` | `/camera/image_raw` | Görüntüler ve `manifest.csv` | Kontrollü sıklıkta, sahne kimliğiyle veri kaydeder. Uçuş demosunda gerekmez. |
| Değerlendirme araçları | Deneme kayıtları ve Gazebo gerçek pozları | Görev metrikleri ve grafikler | Kontrolden bağımsız ölçüm. |

### Mesaj sözleşmesi

İki küçük özel mesaj kullan. Mesajları `drone_alignment_interfaces` adlı `ament_cmake` paketinde oluştur. Düğümler `drone_alignment` adlı `ament_python` paketinde olsun. Mesaj paketini ayrı tutmak, Python düğümlerinde mesaj derleme karmaşasını azaltır.

`PlatformObservation.msg`:

```text
std_msgs/Header header
uint64 ingress_steady_ns
uint32 image_width
uint32 image_height
bool detected
float32 center_x_px
float32 center_y_px
float32 width_px
float32 height_px
float32 confidence
float32 inference_ms
```

- `header`, orijinal kamera görüntüsünün damgası ve kamera çerçevesidir. Algılama bittiğinde yeni damgayla değiştirilmez.
- `ingress_steady_ns`, görüntünün dedektörün ROS abonelik callback'ine geldiği anda alınır. Aynı VM'deki süreçler boyunca aynen taşınır.
- Kutular **orijinal ROS görüntüsünün piksel koordinatlarındadır**. Modelin yeniden boyutlandırılmış/letterbox görüntüsüne ait koordinatlar yayımlanmaz.
- Uygun kutu yoksa da `detected=false` mesajı yayımla. Sayısal kutu alanlarını sıfırla; önceki kutuyu yeni tespit gibi kullanma.

`BodyVelocity.msg`:

```text
std_msgs/Header header
uint64 ingress_steady_ns
uint64 command_steady_ns
bool enabled
float32 forward_mps
float32 right_mps
```

- `header.stamp` ve `ingress_steady_ns` kararı doğuran görüntüden kopyalanır; `command_steady_ns` hız isteği üretildiğinde alınır. Hızların çerçevesi kamera değildir: `header.frame_id` değeri `base_link_frd` olarak belirlenir ve ileri/sağ/aşağı gövde tanımı belgelenir.
- İleri ve sağ hızları drone gövdesine göredir. ROS'un genel `Twist` eksen varsayımını sessizce MAVLink'e aktarma.
- Dikey hız ve yaw kontrolü bu arayüzde yoktur. MAVLink mesajında `vz=0` kullanılır, yaw/yaw-rate alanları maskeyle yok sayılır.

Diğer arayüzler:

- `/approach/enable`: `std_srvs/srv/SetBool`; `true` görev başlatır, `false` görevi durdurur. Başlangıçta kapalıdır.
- `/approach/state`: `std_msgs/msg/String`; değerler `IDLE`, `WAITING_TARGET`, `ALIGNING`, `ALIGNED`, `TARGET_LOST`, `ABORTED`.
- `/flight/status`: `std_msgs/msg/String`; değerler `DISCONNECTED`, `NOT_READY`, `READY`, `MANUAL_OVERRIDE`. `READY`: güncel heartbeat, armed ve GUIDED koşulları sağlanmış.
- Görüntü aboneliğinde `qos_profile_sensor_data` ile uyumlu best-effort ve küçük kuyruk kullan. Tespit/hız topic'lerinde reliable ve depth 1 seç; eski mesajlar birikmesin. Durum yayın/aboneliğinde reliable, transient-local ve depth 1 ile son durumun yeni aboneye ulaşmasını sağla.

### Uygulama dosyalarının temel arayüzleri

| Dosya | Uygulanacak arayüz / görev |
|---|---|
| `geometry.py` | `normalized_error(cx, cy, width, height) -> tuple[float, float]`; görüntü merkezine göre boyutsuz hata. |
| `controller.py` | `compute_body_velocity(ex, ey, kp, max_speed, deadband) -> tuple[float, float]`; ileri ve sağ hızları. |
| `state_machine.py` | `update(detected, fresh, ready, enabled, centered, sim_time_s) -> str`; durum ve kesintisiz hizalanma süresi. |
| `flight_interface_node.py` | `send_body_velocity(forward_mps, right_mps)`; MAVLink paketleme, heartbeat ve komut yaşı. |
| `dataset_tools/validate_dataset.py` | Kutu aralıkları, dosya eşleşmesi, sınıf kimliği ve sekans ayrımını denetler; hata varsa sıfır dışı çıkış. |
| `evaluation/summarize_trials.py` | `trials.csv` ve zaman serilerinden başarı, süre ve son hatayı hesaplar. |
| `evaluation/benchmark_backends.py` | Aynı görüntülerde PyTorch ve ONNX Runtime'ın doğruluk ve gecikmesini ölçer. |

<a id="dosyalar"></a>
## 5. Klasör ve dosya düzeni

Bu ağaç **uygulama sırasında oluşturulacak** dosyaları gösterir; bu yol haritasını hazırlarken proje kodu oluşturulmadı. Ubuntu proje kökü `~/projects/drone_alignment`, Windows eğitim kopyası `C:\drone_alignment_train` olsun. Aşağıdaki göreli dosya adları bu köklere aittir.

```text
drone_alignment/
  README.md
  configs/
    alignment.yaml
    bridge.yaml
    simulation.env
  sim/
    worlds/platform_world.sdf
    models/delivery_platform/
    models/iris_down_camera/
  ros_ws/src/
    drone_alignment_interfaces/
      msg/PlatformObservation.msg
      msg/BodyVelocity.msg
      CMakeLists.txt
      package.xml
    drone_alignment/
      drone_alignment/
        detector_node.py
        approach_node.py
        flight_interface_node.py
        dataset_recorder.py
        geometry.py
        controller.py
        state_machine.py
      launch/alignment.launch.py
      test/
        test_geometry.py
        test_controller.py
        test_state_machine.py
        test_command_freshness.py
      setup.py
      setup.cfg
      package.xml
      resource/drone_alignment
  dataset_tools/
    validate_dataset.py
    preview_labels.py
  training/
    train.py
    export_onnx.py
    pytorch_basics.py
    dataset.yaml
    experiment_log.md
  evaluation/
    benchmark_backends.py
    summarize_trials.py
    log_ground_truth.py
    cases.csv
  datasets/platform/
    images/train/
    images/val/
    images/test/
    labels/train/
    labels/val/
    labels/test/
    manifest.csv
    split_manifest.csv
  models/
    platform_best.pt
    platform_best.onnx
  reports/
    environment.md
    requirements_windows.txt
    requirements_ubuntu.txt
    diary.md
    dataset_card.md
    test_protocol.md
    trials.csv
    latency.csv
    backend_comparison.csv
    final_report.md
  media/
  .gitignore
```

`datasets/`, sanal ortamlar, ROS `build/install/log`, eğitim `runs/` klasörü ve büyük model/video dosyalarını normal Git geçmişine koyma. Küçük yapılandırmaları, kodu, veri manifestlerini ve raporları kaydet. Paylaşılacak ağırlık ve veri için README'de indirme/üretme yolu belirt. Üçüncü taraf model ve araçların lisanslarını README'de kaynaklarıyla belirt; bu plan ticari lisans değerlendirmesi yapmaz.

<a id="olcutler"></a>
## 6. Başarı ölçütleri ve başlangıç ayarları

### Görev başarısı

Başlangıç tasarım hedefi:

- Platform yaklaşık 2 × 2 metre; yükseklik yaklaşık 5 metre.
- Başlangıç yatay uzaklığı 0,5–2 metre; platformun yeterli kısmı kamerada görünür.
- 10 önceden belirlenmiş deneme.
- En fazla 30 simülasyon saniyesinde platform merkezine yatay uzaklık **0,5 metre veya altı**.
- Bu koşul **kesintisiz 3 simülasyon saniyesi** korunursa deneme başarılı.
- İlk hedef en az **8/10** başarı; sonucu elde etmeden başarı iddiası yok.

Gerçek uzaklık, ortak Gazebo dünya çerçevesindeki drone ve platform pozlarından değerlendirme aracıyla hesaplanır:

```text
distance_m = sqrt((drone_x - platform_x)^2 + (drone_y - platform_y)^2)
```

Kamera gövde merkezinden uzaktaysa ofseti kaydet; ilk tasarımda kamerayı gövdenin yatay merkezine yerleştir. Görüntü merkezlenmesi ve metre cinsinden görev başarısı ayrı ölçümlerdir. Denetleyici `ALIGNED` dedi diye ölçüm otomatik başarılı sayılmaz.

### Başlangıç parametreleri

Bu sayılar başlangıç ayarıdır; ölçerek değiştir ve deney kaydına yaz.

| Ayar | İlk değer |
|---|---:|
| Kamera | 640 × 480, 15 Hz |
| İlk model giriş boyutu | 416 × 416 |
| Algılama hedef sıklığı | En az 5 Hz; daha hızlıysa eski görüntü biriktirme |
| Yatay komut sıklığı | 10 Hz |
| Toplam yatay hız sınırı | 0,30 m/s |
| Oransal kazanç `kp` | 0,40 m/s / normalize hata |
| Görüntü merkezlenme eşiği | Normalize hata normu ≤ 0,08 |
| Tespit güven eşiği | 0,60 |
| Bir tespitin azami gerçek yaşı | 0,50 saniye, ROS'a girişten itibaren |
| Uçuş düğümünün komut watchdog süresi | 0,30 gerçek saniye |
| Heartbeat bayatlama sınırı | 2,0 gerçek saniye |
| Hizalanma bekleme süresi | 3 simülasyon saniyesi |

Görüntü gelmiyorsa, tespit eskiyse veya güven eşiği sağlanmıyorsa ilerlemeye devam edilmez. Uçuş GUIDED ve armed durumundaysa sıfır hız istenir; operatör başka uçuş moduna geçmişse düğüm modu geri değiştirmez ve hareket komutlarını keser. Başlangıçta otomatik arm/kalkış/mod değiştirme yoktur.

### Ölçüm grupları

1. **Algılama:** Precision, recall, mAP50, mAP50–95; ayrıca kutu merkez hatası ve olumsuz sahnelerde yanlış pozitifler.
2. **Çalışma hızı:** Ön işleme, model, son işleme; p50 ve p95 süreleri, kamera ve çıkarım Hz değerleri, simülasyon gerçek zaman faktörü (RTF).
3. **Kontrol:** Hizalanma süresi, son yatay hata, başarı sayısı, hedef kaybından sonra son sıfır olmayan komuta kadar süre.
4. **Dağıtım biçimi:** PyTorch CPU ve ONNX Runtime CPU karşılaştırması. Windows GPU ölçümü ayrıca yazılır; VM CPU sonuçlarıyla doğrudan backend üstünlüğü gibi sunulmaz.

<a id="riskler"></a>
## 7. Önce doğrulanacak riskler

| Durum | Beklenen davranış | Doğrulama günü |
|---|---|---|
| Görüntü var ama platform yok | `detected=false`; drone eski kutuyla hareket etmez. | 9, 12 |
| Görüntü/komut bayat veya süreç durdu | Watchdog eski komutu sürdürmez. | 10, 12 |
| Kamera eksenlerinde işaret hatası | Sağ/sol/ileri/geri testleri model olmadan geçer. | 10 |
| Operatör uçuş modunu değiştirdi | Sistem komut göndermeyi keser; görevi kendiliğinden sürdürmez. | 10, 12 |
| Simülasyon durakladı/sıfırlandı veya sahneler veri sızdırdı | Saat alanları karışmaz; görev yeniden başlatılır; veri ayrımı sekans bazındadır. | 6, 12, 13 |

Temel kesme kuralı: Bir altyapı sorunu üzerinde aynı oturumda yaklaşık 60–90 dakika sonuçsuz kaldıysan sürüm, komut ve logu kaydet. Yeni paketler ekleyerek sorunu büyütme; Ek A'daki sırayla daralt. Ağ ve görüntü performans sorunlarını model eğitimiyle çözmeye çalışma.

---

<a id="gun-1"></a>
## Gün 1 — Ortamı kaydet, Gazebo grafiğini ve Windows GPU'yu doğrula

**Amaç:** Sonraki günlerde üzerinde çalışacağın iki ortamın temelini doğrulamak.

**Öğreneceğin:** VMware grafik hızlandırması ile CUDA farkı; ROS/Gazebo sürüm eşleşmesi; sanal Python ortamı.

### Adımlar

- [ ] VM kapalıyken VMware Display ayarındaki 3B hızlandırmayı kontrol et. Kaynak ayırırken Windows'u belleksiz bırakma; toplam RAM bilinmediği için sabit VM RAM önerisini körlemesine uygulama.
- [ ] Ubuntu'da sürüm ve kaynak bilgisini kaydet:

```bash
lsb_release -ds
python3 --version
printenv ROS_DISTRO
free -h
nproc
```

- [ ] Proje klasörünü oluştur; mevcutsa içindekileri koru:

```bash
mkdir -p ~/projects/drone_alignment/reports
cd ~/projects/drone_alignment
git init
```

- [ ] `reports/environment.md` içine VMware sürümünü, Ubuntu sürümünü, VM RAM/CPU ayarını ve Windows NVIDIA sürücüsünü yaz.
- [ ] Temel ROS/grafik araçlarını kur:

```bash
sudo apt update
sudo apt install build-essential cmake mesa-utils python3-venv python3-colcon-common-extensions python3-pytest ros-jazzy-ros-gz ros-jazzy-cv-bridge ros-jazzy-rqt-image-view ros-jazzy-rosidl-default-generators
source /opt/ros/jazzy/setup.bash
glxinfo -B
```

- [ ] `OpenGL renderer` satırını kaydet. `llvmpipe` yazıyorsa yazılımsal çizim kullanılıyor olabilir; grafik hızlandırmasını çözmeden kamera sahnesini ağırlaştırma.
- [ ] Harmonic komutu sistemde yoksa [resmî Ubuntu kurulumundaki](https://gazebosim.org/docs/harmonic/install_ubuntu/) Noble/Harmonic adımlarını uygula. Eski Gazebo Classic deposu ekleme. Ardından:

```bash
gz sim --versions
gz sim -r shapes.sdf
```

- [ ] Pencerenin açıldığını ve hareketin akıcı olduğunu gözle. Çözünürlüğü küçük tut; grafik sürücü hatasını terminalden kaydet.
- [ ] Windows PowerShell'de `nvidia-smi` ile kartı doğrula. Python 3.12 kuruluysa eğitim ortamını oluştur:

```powershell
New-Item -ItemType Directory -Force -Path C:\drone_alignment_train
Set-Location C:\drone_alignment_train
py -3.12 -m venv .venv
```

- [ ] [PyTorch resmî kurulum seçicisinden](https://pytorch.org/get-started/locally/) aldığın CUDA destekli komutu `.venv\Scripts\python.exe -m pip` kullanarak bu ortama uygula. Ardından:

```powershell
.\.venv\Scripts\python.exe -c "import torch; print(torch.__version__); print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CUDA kullanilamiyor')"
```

### Gün sonu çıktısı ve kabul

- [ ] Gazebo şekil dünyası açılıyor; çizim motoru bilgisi kaydedildi.
- [ ] Windows'taki PyTorch CUDA kontrolü `True` ve RTX 4060 adı veriyor.
- [ ] Ortam bilgileri `reports/environment.md` içinde.

**Takılırsan:** CUDA sorunu Windows eğitim ortamında çözülür; VM'e NVIDIA sürücüsü kurmaya geçme. Gazebo boş/karanlık açılıyorsa model dosyalarından önce grafik motorunu incele. Bugünün çıktısı uçan drone değil, doğrulanmış altyapıdır.

---

<a id="gun-2"></a>
## Gün 2 — ArduPilot SITL, Gazebo ve Mission Planner bağlantısı

**Amaç:** Algılama modeli olmadan, simüle drone'u kaldırıp kararlı uçurmak.

**Bağımlılık:** Gün 1'de Gazebo çalışıyor.

### Adımlar

- [ ] ArduPilot'u proje kodunun dışında bir üçüncü taraf klasörüne al:

```bash
mkdir -p ~/projects/drone_alignment_vendor
cd ~/projects/drone_alignment_vendor
git clone --recurse-submodules https://github.com/ArduPilot/ardupilot.git
cd ardupilot
Tools/environment_install/install-prereqs-ubuntu.sh -y
```

- [ ] [Resmî Linux kurulumunun](https://ardupilot.org/dev/docs/building-setup-linux.html) istediği profil/ortam adımlarını tamamla; yeni terminal aç. İlk başarılı sürümün commit kimliğini `git rev-parse HEAD` ile kaydet. Plan boyunca her gün `git pull` yapma.
- [ ] Güncel [ArduPilot Gazebo eklentisini](https://github.com/ArduPilot/ardupilot_gazebo) ayrı vendor klasörüne klonla; Harmonic bağımlılıklarını kurup derle. Belgedeki `GZ_VERSION=harmonic`, eklenti ve model arama yollarını uygula. Bu adımlar ROS paketini derlemekten ayrıdır.
- [ ] Gazebo terminalinde örnek Iris dünyasını başlat:

```bash
gz sim -v4 -r iris_runway.sdf
```

- [ ] Ayrı SITL terminalinde Windows adresini alıp bağlantıyı başlat:

```bash
read -r -p "Windows VMware VMnet8 IPv4 adresi: " ALIGN_WINDOWS_IP
cd ~/projects/drone_alignment_vendor/ardupilot
./Tools/autotest/sim_vehicle.py -v ArduCopter -f gazebo-iris --model JSON --console --map --out="udp:${ALIGN_WINDOWS_IP}:14550" --out=udp:127.0.0.1:14560
```

Windows adresini Windows'taki `ipconfig` çıktısından belirle. NAT kullanıyorsan VMware VMnet8 adaptörünün IPv4 adresi başlangıç adayıdır; NAT ağ geçidi adresinin Windows adresi olduğunu varsayma. Bridged kullanıyorsan erişilebilir Windows LAN adresini kullan. Bu komut simüle drone içindir.

- [ ] Mission Planner'da bağlantı tipini UDP, dinleme portunu `14550` seç. Mission Planner'ın Simulation ekranından ikinci bir SITL başlatma; zaten Gazebo'ya bağlı tek SITL çalışıyor.
- [ ] MAVProxy konsolunda konum/EKF hazır olana kadar bekle; sonra:

```text
mode guided
arm throttle
takeoff 5
```

- [ ] Drone'un yükselip durduğunu ve Mission Planner telemetrisinin aynı drone'u gösterdiğini doğrula.
- [ ] MAVProxy'den `mode land` ile simüle uçuşu bitir. Arming denetimlerini topluca kapatmak yerine hata mesajını çöz.
- [ ] Çalışan komutları, commit kimliklerini ve ağ adreslerini `reports/environment.md` içine kaydet.

### Portların görevi

| Port | Kullanım |
|---|---|
| Windows UDP 14550 | Mission Planner telemetrisi ve komutları |
| Ubuntu UDP 14560 | Proje uçuş düğümünün MAVLink bağlantısı |
| SITL/Gazebo iç bağlantısı | Eklentinin kendi ayarları; yukarıdaki GCS portlarıyla karıştırma |

MAVProxy'yi yönlendirici olarak kullan; iki programı aynı UDP dinleme portuna bağlama. Windows güvenlik duvarında gerekirse yalnızca ilgili uygulama/port için dar kapsamlı özel ağ izni ver; güvenlik duvarını bütünüyle kapatma. GCS yönlendirme yaklaşımı [ArduPilot SITL belgesinde](https://ardupilot.org/dev/docs/using-sitl-for-ardupilot-testing.html) açıklanır.

### Gün sonu çıktısı ve kabul

- [ ] Gazebo ve Mission Planner aynı drone'u gösteriyor.
- [ ] GUIDED kalkış, yaklaşık 5 metre havada bekleme ve LAND çalışıyor.
- [ ] Portlar ve yeniden başlatma komutları yazılı.

**Takılırsan:** Önce Gazebo–SITL, sonra SITL–Mission Planner bağlantısını ayrı ayrı doğrula. Mission Planner bağlanmıyorsa bu, Gazebo eklentisinin çalışmadığı anlamına gelmez.

---

<a id="gun-3"></a>
## Gün 3 — Aşağı bakan kamera, ROS mesajları ve erken performans denemesi

**Amaç:** Görüntü akışını ve model çalıştırma kapasitesini, veri hazırlamadan önce kanıtlamak.

**Öğreneceğin:** SDF kamera sensörü, `ros_gz_bridge`, özel mesaj, QoS, FPS ile simülasyon hızının farkı.

### Adımlar

- [ ] Iris modelinin projeye ait kopyasını `sim/models/iris_down_camera/` altında oluştur. Vendor modelini doğrudan değiştirip güncellemelerde kaybetme.
- [ ] Kamerayı gövdenin altında, yatay merkezine yakın ve aşağı bakacak biçimde yerleştir. Hareketli gimbal yerine sabit kamera kullan.
- [ ] Kamera ayarlarını 640 × 480 ve 15 Hz yap. Eksenleri doğrulamak için zemine ileri yön oku veya kareli referans yerleştir.
- [ ] Kameranın görüntü topic'ini komutla keşfet; örnek modeldeki uzun adı ezberleyerek varsayma:

```bash
gz topic -l
```

- [ ] `configs/bridge.yaml` içine keşfettiğin Gazebo görüntü ve kamera bilgisi topic'lerini ROS adlarıyla eşleştir. Görüntü `sensor_msgs/msg/Image` / `gz.msgs.Image`, kamera bilgisi `sensor_msgs/msg/CameraInfo` / `gz.msgs.CameraInfo`, saat `rosgraph_msgs/msg/Clock` / `gz.msgs.Clock` olsun. Yön `GZ_TO_ROS`.
- [ ] Köprüyü başlat ve kontrol et:

```bash
ros2 run ros_gz_bridge parameter_bridge --ros-args -p config_file:=$HOME/projects/drone_alignment/configs/bridge.yaml
```

Başka ROS terminalinde:

```bash
ros2 topic list
ros2 topic hz /camera/image_raw
ros2 run rqt_image_view rqt_image_view
```

- [ ] `rqt_image_view` içinde `/camera/image_raw` seç. Kamera gerçekten aşağı bakıyor mu kontrol et. Görüntü QoS ayarını yayıncıyla uyumlu tut.
- [ ] `~/projects/drone_alignment/ros_ws/src` klasörünü oluştur. Burada `ros2 pkg create` ile `drone_alignment_interfaces` adlı `ament_cmake` mesaj paketi ve `drone_alignment` adlı `ament_python` düğüm paketi oluştur.
- [ ] 4. bölümdeki iki mesajı tanımla. Mesaj paketinde `std_msgs`, `rosidl_default_generators`, `rosidl_default_runtime` bağımlılıklarını; `rosidl_interface_packages` grup üyeliğini ve iki `.msg` dosyasını listeleyen `rosidl_generate_interfaces` çağrısını ayarla. Python paketinin `package.xml` dosyasında `rclpy`, `sensor_msgs`, `std_msgs`, `std_srvs`, `cv_bridge` ve `drone_alignment_interfaces` bağımlılıklarını belirt.
- [ ] `ros_ws` içinde `colcon build --symlink-install` çalıştır, ardından `source install/setup.bash` yap. Mesajı doğrula:

```bash
ros2 interface show drone_alignment_interfaces/msg/PlatformObservation
ros2 interface show drone_alignment_interfaces/msg/BodyVelocity
```

- [ ] Ubuntu proje Python ortamını oluştur:

```bash
cd ~/projects/drone_alignment
/usr/bin/python3 -m venv --system-site-packages .venv
source .venv/bin/activate
source /opt/ros/jazzy/setup.bash
python -m pip install ultralytics pymavlink colcon-common-extensions
python -c "import rclpy, cv2; from cv_bridge import CvBridge; import ultralytics; print('ROS ve model importlari tamam')"
```

- [ ] Mesajların ilk derlemesinden sonra Python düğümlerini venv yorumlayıcısıyla tekrar derle. Yalnızca venv'i aktive edip sistemdeki `/usr/bin/colcon` komutunu çağırmak bazı kurulumlarda sistem Python'uyla giriş betiği üretebilir. Bu projede venv içindeki colcon'u açıkça kullan:

```bash
cd ~/projects/drone_alignment/ros_ws
~/projects/drone_alignment/.venv/bin/colcon build --symlink-install
source install/setup.bash
```

- [ ] Üretilen düğüm giriş betiğinin ilk satırındaki yorumlayıcıyı kontrol et; modelin kurulu olduğu venv'i göstermeli. Başarılı import sonrasında `pip freeze` çıktısını kaydet. ROS kurulumu ile ilgisiz toplu paket yükseltmesi yapma.
- [ ] Kameradan tek görüntü kaydet; hazır `yolo11n.pt` ile CPU'da 416 giriş boyutunda ısınma sonrası en az 100 çıkarım yap. Aynı anda Gazebo çalışsın. Hazır modelin platformu tanıması beklenmez; burada yalnızca süreyi ölçüyoruz.
- [ ] Çıkarımın p50/p95 süresini, görüntü Hz değerini ve Gazebo RTF değerini kaydet.

### Üçüncü gün kabul koşulları ve karar kapısı

- [ ] Drone uçuyor, görüntü ROS'a geliyor, model VM'de çalışıyor.
- [ ] Başlangıç hedefi: en az 5 çıkarım/s ve yaklaşık RTF ≥ 0,8. Bunlar ortamı değerlendirmek için çalışma hedefidir, garanti değil.
- [ ] Yetersizse önce GUI yükünü azalt, modeli 320 girişte dene, kamera Hz/çözünürlüğünü düşür ve yeniden ölç.
- [ ] Hâlâ yetersizse ortam değişikliğine burada karar ver. Aynı anda WSL kurulumu, Windows'ta ayrı çıkarım sunucusu ve yeni haberleşme protokolü ekleme.

**Gün sonu kanıtı:** Kamera ekran görüntüsü, model süreleri, çalışan mesaj tanımları ve `reports/environment.md` güncellemesi.

**Kontrol noktası 1:** Bu kapı geçilmeden gün 4–9 veri/model çalışmasına geçme. Gerekirse takvimi uzat; çalışan altyapı ölçülmeden 15 gün taahhüdü verme.

---

<a id="gun-4"></a>
## Gün 4 — Platform sahnesi ve veri kaydedici

**Amaç:** Modelin öğreneceği nesneyi tanımlamak ve veriyi düzenli toplamak.

**Bağımlılık:** Kamera ROS'a geliyor; ilk performans kapısı geçildi.

**Dosyalar:** `sim/worlds/platform_world.sdf`, `sim/models/delivery_platform/`, `dataset_recorder.py`, `reports/dataset_card.md`.

### Adımlar

- [ ] Basit, yaklaşık 2 × 2 metre, yere yakın bir teslimat platformu oluştur. Kutu merkezinin platformun fiziksel merkezine yaklaşık karşılık gelmesini sağlayan simetrik geometri kullan.
- [ ] Aynı nesnenin 2–3 doku/işaret varyantını hazırla. İlk sürümde rastgele onlarca model indirme; birkaç kontrollü varyant yeterli.
- [ ] Zemin için 3–4 basit malzeme, ortam için birkaç ışık/yön seçeneği hazırla. Birkaç platform olmayan kutu veya desen de ekle.
- [ ] `dataset_card.md` içine sınıfı tanımla: “Yere yerleştirilmiş teslimat platformunun dış fiziksel sınırı.” Yalnızca üzerindeki sembol etiketlenmeyecek.
- [ ] `dataset_recorder` düğümünü yaz. Parametreleri `output_dir`, `scene_id`, `session_id`, `save_interval_s` olsun. İlk kayıt aralığı 0,5–1 saniye.
- [ ] Her görüntüyle birlikte `manifest.csv` satırı üret. Alanlar:

```text
image_id,scene_id,session_id,image_path,source_stamp_ns,width,height,platform_variant,ground_variant,light_variant,nominal_height_m,notes
```

- [ ] Gerçek poz verisi henüz yoksa uydurma kesin değer yazma; `nominal_height_m` komutla hedeflenen yaklaşık yükseklik olabilir. Gerçek ölçümle farkını belgede açık tut.
- [ ] Kayıt dosya adını `scene03_session02_frame0012.png` gibi benzersiz üret. Yeni oturum eski görüntülerin üzerine yazmasın.
- [ ] Önce 30–40 görüntülük pilot kayıt al. Görüntülerin açıldığını, isimlerin benzersiz olduğunu ve manifest satır sayısını kontrol et.

### Doğrulama ve kabul

- [ ] Drone sabitken arka arkaya kaydedilen görüntülerin neredeyse aynı olduğunu gözle gör; bunları çeşitlilik sanma.
- [ ] Platform yokken de kayıt al. Negatifler gerçek simülasyon sahneleri olsun.
- [ ] Bir komutla kayıt başlıyor; görüntü ve manifest eşleşiyor; platformun etiket sınırı yazılı.

**Takılırsan:** Önce tek zemin/tek platformla kayıt aracını bitir. Dekorasyon için günün tamamını harcama.

---

<a id="gun-5"></a>
## Gün 5 — Çeşitli ve bölünebilir bir veri kümesi topla

**Amaç:** Eğitimde ezberlemeye, değerlendirmede veri sızıntısına yol açmayan küçük veri kümesi.

**Öğreneceğin:** Negatif örnek, dağılım çeşitliliği, sekans/sahne bazlı ayrım.

### Başlangıç toplama planı

Yaklaşık **12 ayrı sahne/oturum grubunda 40'ar görüntü**, toplam **480 görüntü** hedefle. Bu bir yeterlilik garantisi değil; küçük proje için başlangıç bütçesidir. Birbirine çok benzeyen kareleri ele; daha az ama daha çeşitli veri daha yararlı olabilir.

| Değişken | Toplama sırasında denenecek durum |
|---|---|
| Yükseklik | Yaklaşık 4, 5 ve 6 metre |
| Platformun görüntüdeki yeri | Merkez, sağ/sol/üst/alt ve köşeler |
| Yönelim | Başlangıç yönü ve küçük yaw değişimleri |
| Zemin / ışık | Farklı arka planlar, açık/koyu görünüm, gölge |
| Platform görünümü | 2–3 temsilî varyant |
| Negatif örnek | Platform yok; benzer kutu/desen var |
| Zor örnek | Küçük platform, görüntü kenarı, kısmi görünüm |

### Adımlar

- [ ] Çekime başlamadan 12 grubun kimliğini ve koşulunu yaz.
- [ ] Her grupta drone'u birkaç farklı konuma getir. Yalnızca kayıt frekansını artırarak görüntü sayısını doldurma.
- [ ] Veri kümesinin yaklaşık %20–25'ini platform olmayan görüntülerden oluştur.
- [ ] İlk görevde ağır kapanma çözülmeyeceği için platformun çoğunlukla görünür olduğu örnekleri ağırlıkta tut.
- [ ] Grupları baştan ayır: 8 grup eğitim, 2 grup doğrulama, 2 grup son test. Yaklaşık 320/80/80 görüntü oluşur.
- [ ] Aynı sahnenin ardışık görüntülerini farklı kümelere dağıtma. Aynı sahnenin yalnızca yeni oturum adıyla tekrarını da farklı kümeye koyma.
- [ ] `split_manifest.csv` içine `image_id,scene_id,session_id,split` yaz. Ayırma kararını eğitimden önce sabitle.
- [ ] Eğitime benzer ama aynı olmayan koşullarda doğrulama/test sahneleri hazırla. Modelin desteklemediği yepyeni nesne türünü tek test koşulu yapma.
- [ ] Bozuk görüntü, tekrarlı kare ve boş manifest alanlarını temizle. Ham verinin kopyasını koru.

**Gün sonu kabulü:** Yaklaşık 480 kullanılabilir görüntü veya daha az kullanma gerekçesi; negatif örnekler; sahne bazında sabit train/val/test ayrımı.

**Takılırsan:** 300 çeşitli görüntüyle ilk deneyi başlatabilirsin. Bunu rapora yaz; aynı görüntüyü çoğaltıp veri sayısını büyük gösterme. Yeni veri eklenirse veri kümesine sürüm ver.

---

<a id="gun-6"></a>
## Gün 6 — Etiketle, veriyi programla kontrol et ve Windows'a aktar

**Amaç:** Eğitim programına gerçekten doğru kutular vermek.

**Dosyalar:** `dataset_tools/validate_dataset.py`, `dataset_tools/preview_labels.py`, `training/dataset.yaml`, `reports/dataset_card.md`.

### Adımlar

- [ ] Tercih ettiğin etiketleme aracı YOLO detection biçiminde dışa aktarabilsin. İlk proje için etiketleme sunucusu kurmak zorunda değilsin.
- [ ] Her olumlu görüntüde platformun dış sınırını eksenlere paralel kutuyla etiketle. Sınıf kimliği `0` olsun.
- [ ] Platform kısmen görünüyorsa görünür kısmın kutusunu kullan; aynı kuralı bütün veri kümesine uygula. Kontrolün tam görünür platformla değerlendirileceğini veri kartına yaz.
- [ ] Negatif görüntüler için boş `.txt` etiketi oluştur. Olumlu görüntüyü yanlışlıkla boş etiketli bırakma.
- [ ] [YOLO etiket biçimindeki](https://docs.ultralytics.com/datasets/detect/) her satır şu alanları içerir:

```text
class_id center_x_normalized center_y_normalized width_normalized height_normalized
```

Merkez ve boyutlar görüntü genişlik/yüksekliğine bölünür; piksel değildir. Örneğin 640 × 480 görüntüde merkezi (320, 240), boyutu 128 × 96 olan kutu `0 0.5 0.5 0.2 0.2` olur. Bu yalnızca biçim örneğidir; gerçek etiketler görüntüden ölçülür.

- [ ] `validate_dataset.py` şu koşulları denetlesin: görüntü/etiket eşleşmesi, yalnızca sınıf `0`, sonlu sayılar, pozitif boyut, kutunun [0,1] sınırları içinde kalması, aynı sahnenin farklı split'lere sızmaması.
- [ ] Kasıtlı hatalı etiketle doğrulayıcının hata verdiğini göster; sonra doğru veride başarılı çalıştır. Dosya varlığı kontrolü tek başına yeterli değil.
- [ ] `preview_labels.py` ile her split'ten rastgele kutulu örnekler üret; en az 30 görüntüyü gözle kontrol et. Kutular kayıksa eğitime geçme.
- [ ] Windows eğitim klasörüne veri, manifest ve eğitim kodunu aktar. Linux `.venv`, `build` veya `install` klasörlerini kopyalama.
- [ ] Windows'taki `training/dataset.yaml` dosyasını veri konumuna göre ayarla:

```yaml
path: C:/drone_alignment_train/datasets/platform
train: images/train
val: images/val
test: images/test
names:
  0: delivery_platform
```

- [ ] Ubuntu'daki değerlendirme için `path` değerini Ubuntu veri klasörüne uyarlayan yerel kopya kullan. Windows mutlak yolunu Linux'a aynen taşıma.
- [ ] Veri kartına kaynak, sayılar, varyantlar, split kuralı, kutu kuralı ve bilinen eksikleri yaz.

**Gün sonu kabulü:** Etiket doğrulama hatasız; örnek kutular doğru; Windows'ta veri açılıyor; test kümesi eğitim/ayar seçimi için kullanılmadı.

**Kontrol noktası 2:** Ortam ve denetlenmiş veri kümesi hazır. Veri hatasını daha büyük modelle çözmeye çalışma.

---

<a id="gun-7"></a>
## Gün 7 — PyTorch mantığını öğren ve ilk modeli eğit

**Amaç:** Eğitimin ne yaptığını anlayarak ilk çalışan ağırlığı üretmek.

**Öğreneceğin:** Tensor, forward, loss, backward, optimizer, epoch, batch, train/eval ve fine-tuning.

### Önce 45–60 dakikalık küçük PyTorch çalışması

- [ ] `training/pytorch_basics.py` içinde sentetik doğrusal ilişki öğrenen küçük model kur: veri oluştur, `torch.nn.Linear` kullan, MSE kaybı hesapla, `loss.backward()` ve optimizer adımlarını çalıştır.
- [ ] Başlangıç/son kaybı karşılaştır; ağırlıkları kaydet ve yeniden yükle. Kaybın neden azaldığını kendi cümlelerinle yaz.
- [ ] Bu oyuncak çalışmayı drone modeli başarısı gibi sunma. Amaç, yüksek seviye eğitim aracı kullanırken ne olduğunu anlamak.

### Gerçek model eğitimi

- [ ] Windows eğitim ortamına Ultralytics kur. Kurulumdan sonra `torch.cuda.is_available()` hâlâ `True` olmalı.
- [ ] `training/train.py` içinde Windows çoklu süreç sorunu için `if __name__ == '__main__':` korumasını kullan. İlk çalıştırmada `workers=0` seç.
- [ ] Eğitim kodu `YOLO('yolo11n.pt')` yüklesin, `dataset.yaml` ile `model.train` metodunu aşağıdaki ayarlarla çağırsın ve sonuçları isimlendirilmiş deney klasörüne yazsın.
- [ ] Önce 2 epoch'luk kısa deneme yap. Etiketler yükleniyor mu, tek sınıf var mı, GPU kullanılıyor mu kontrol et. Bu çalışma ana deney değildir.
- [ ] İlk ana deney `E01_baseline` olsun:

| Parametre | Değer |
|---|---|
| `model` | `yolo11n.pt` |
| `imgsz` | 416 |
| `epochs` | 40 |
| `batch` | 8; bellek hatasında 4 |
| `device` | 0 |
| `workers` | 0 |
| `seed` | 7 |
| `patience` | 10 |
| `project` / `name` | `runs/platform` / `E01_baseline` |

- [ ] Veri artırmalarını bu deneyde kapat: `hsv_h=0`, `hsv_s=0`, `hsv_v=0`, `degrees=0`, `translate=0`, `scale=0`, `fliplr=0`, `flipud=0`, `mosaic=0`, `mixup=0`. Kurulu sürümde ek artırmalar varsa etkilerini deney kaydına yaz.
- [ ] Loss, precision/recall ve doğrulama mAP grafikleriyle tahmin görüntülerini incele. `best.pt` ile son epoch ağırlığının neden farklı olabileceğini öğren.
- [ ] `training/experiment_log.md` içine veri sürümü, ayarlar, süre, best epoch, doğrulama metrikleri ve 5 yanlış örnek yaz.

Bu çalışma önceden eğitilmiş modeli kendi sınıfına uyarlamadır; ağı tamamen sıfırdan eğitmek değildir. Model ailesi [YOLO11 belgesinde](https://docs.ultralytics.com/models/yolo11/), eğitim arayüzü [resmî eğitim rehberinde](https://docs.ultralytics.com/modes/train/) açıklanır.

**Gün sonu kabulü:** CUDA üzerinde tamamlanan eğitim; saklanan `best.pt`, ayarlar ve doğrulama sonuçları; temel eğitim adımlarını kendi sözlerinle açıklayabiliyorsun.

**Takılırsan:** GPU belleği yetmiyorsa önce batch'i düşür. Loss anormal ise etiketleri ve veri yollarını kontrol et.

---

<a id="gun-8"></a>
## Gün 8 — Hataları incele, tek bir iyileştirme deneyi yap

**Amaç:** “Model çalıştı” ile “modeli değerlendirdim ve geliştirdim” arasındaki farkı oluşturmak.

### Adımlar

- [ ] E01'in doğrulama kümesinde kaçırılan platform, yanlış pozitif, kayık kutu merkezi ve görüntü kenarı hatalarını ayrı topla.
- [ ] Örnekleri görüntü olarak sakla. Kontrol için kutu merkezinin kararlılığına özellikle bak.
- [ ] Etiket hatası varsa düzelt; veri sürümünü değiştir ve iki deneyi de aynı veri sürümünde tekrar çalıştır. Bir deneyin verisini sessizce değiştirerek karşılaştırma yapma.
- [ ] İkinci deney `E02_augmentation` olsun. Veri, seed, model, görüntü boyutu, batch ve epoch bütçesi aynı kalsın. Yalnızca sınırlı artırmalar aç:

```text
hsv_h=0.01
hsv_s=0.20
hsv_v=0.20
degrees=10
translate=0.10
scale=0.15
fliplr=0
flipud=0
mosaic=0
mixup=0
```

- [ ] Gerçek sahnede karşılığı olmayan agresif dönüşümler ekleme.
- [ ] E01 ve E02'yi aynı doğrulama kümesinde karşılaştır. Artırma daha iyi sonuç vermek zorunda değil; etkisini raporla.
- [ ] Birincil seçim ölçütü doğrulama **mAP50–95** olsun. Çok yakın sonuçta yanlış pozitifler, kutu merkez hatası ve çalışma hızıyla karar ver. Test kümesiyle eşik/model seçme.
- [ ] Seçilen ağırlığı `models/platform_best.pt` olarak kopyala. Hangi deneyden geldiğini ve SHA-256 özetini kaydet.
- [ ] Modeli Ubuntu'ya aktar; Windows ve Ubuntu dosyalarının hash değerlerini karşılaştır.

### Deney kaydı

Her deney için şu sütunları doldur:

```text
experiment_id,dataset_version,seed,imgsz,epochs_run,val_precision,val_recall,val_map50,val_map50_95,center_error_px,notes
```

**Gün sonu kabulü:** İki kayıtlı deney; yalnızca validation ile seçilmiş model; örnek hatalar ve aktarım doğrulaması.

**Takılırsan:** 10 ayarı aynı anda deneme. Veride olmayan koşulu artırmayla çözmeye çalışmadan önce o koşuldan simülasyon örneği topla; test ayrımını koru.

---

<a id="gun-9"></a>
## Gün 9 — Eğittiğin modeli canlı ROS 2 kamera akışına bağla

**Amaç:** Kaydedilmiş videoya bağlı olmayan, simülasyon kamerasını işleyen algılama düğümü.

**Dosyalar:** `detector_node.py`, `configs/alignment.yaml`, `launch/alignment.launch.py`.

### Adımlar

- [ ] Modeli başlangıçta bir kez yükle; her karede diskten açma.
- [ ] Kamera callback'inde `header` ve `time.monotonic_ns()` giriş damgasını kaydet. Dönüşüm/çıkarım bu meta veriyi aynen taşısın.
- [ ] Callback yalnızca en yeni görüntüyü saklasın. Model meşgulse bütün kareleri kuyruğa ekleme; iş bitince en yeni kareyi al.
- [ ] `cv_bridge` ile OpenCV görüntüsüne çevir. BGR/RGB dönüşümünü model arayüzüne göre bir kez yap; iki kez çevirmediğini renkli referansla kontrol et.
- [ ] Çıkarım için `eval`/inference çalışma biçimi kullan; eğitim gradient hesaplarını açık bırakma. Kutuların orijinal görüntüye geri ölçeklendiğini doğrula.
- [ ] Tek platform varsayımı altında güven eşiğini geçen uygun kutuyu seç. Kadraj kenarına temas eden veya aşırı küçük kutuları ilk kontrol sürümünde uygun sayma; filtre eşiklerini `alignment.yaml` içinde tut ve raporla.
- [ ] Her işlenen görüntüde `PlatformObservation` yayımla. Platform yokken de `detected=false` üret.
- [ ] Hatalı görüntü/model exception'ında eski kutuyu tekrar yayımlama. Hata logla; kontrol zaman aşımı devreye girebilsin.
- [ ] Debug görüntüsünde kutu, merkez noktası, güven skoru, model süresi ve kaynak damgasını göster. Debug yayınını yaklaşık 5 Hz ile sınırla.
- [ ] İlk launch dosyası köprüyü ve dedektörü açsın. Uçuş kontrolü henüz kapalı kalsın.

### Doğrulama

```bash
ros2 topic echo /platform/observation --once
ros2 topic hz /platform/observation
ros2 run rqt_image_view rqt_image_view
```

- [ ] Platform sağa/sola gidince piksel merkezi doğru değişiyor.
- [ ] Platform kalkınca `detected=false` geliyor.
- [ ] 640 × 480 görüntü merkezi (320, 240); modelin 416 giriş merkeziyle karışmıyor.
- [ ] İki dakikalık akışta gecikme sürekli büyümüyor ve bellek kontrolsüz artmıyor.

**Gün sonu kabulü:** Eğitilmiş model canlı Gazebo kamerasını işliyor; tespitler görünür; kaynak zaman damgaları korunuyor.

**Kontrol noktası 3:** Veri → eğitim → simülasyon kamerasına entegrasyon tamam. Ara demo kaydet; henüz otonom hizalanma iddiası yapma.

---

<a id="gun-10"></a>
## Gün 10 — Model olmadan hareket komutunu ve eksenleri doğrula

**Amaç:** Algılama hatasıyla kontrol/eksen hatasını birbirine karıştırmamak.

**Dosyalar:** `geometry.py`, `controller.py`, `flight_interface_node.py`, `test_geometry.py`, `test_controller.py`, `test_command_freshness.py`.

### Önce yönleri tanımla

- Görüntüde `u`: sağa doğru artar; `v`: aşağı doğru artar.
- Gövde hızında `forward`: ileri, `right`: sağ yön pozitiftir.
- Bu planın kamera yerleşimi: görüntünün üst tarafı drone'un ilerisi, sağ tarafı drone'un sağıdır. Kamera montajı farklıysa aşağıdaki dönüşüm değişir; gözlemle doğrulamadan kullanma.

Normalize hata:

```text
ex = (center_x_px - image_width / 2) / (image_width / 2)
ey = (center_y_px - image_height / 2) / (image_height / 2)

forward_mps = -kp * ey
right_mps   =  kp * ex
```

Hata normu merkezlenme eşiğinin altındaysa iki hız da sıfır. Diğer durumda hız vektörünün **toplam büyüklüğünü** 0,30 m/s ile sınırla; yalnızca her ekseni 0,30 ile kesip çaprazda daha yüksek hıza izin verme. Bu ilk sürüm görsel oransal kontroldür; piksel hatasının metre cinsinden mesafe olduğunu iddia etmez.

### Adımlar

- [ ] Önce merkez, dört yön, çapraz ve geçersiz sayı durumlarını doğrulayan testleri yaz. `kp=0.40` için `(ex,ey)=(0.4,0)` → `(ileri,sağ)=(0,0.16)`; `(0,-0.5)` → `(0.20,0)` bekle. `(1,1)` durumunda toplam hız 0,30'u aşmasın; merkezde iki hız da sıfır olsun.
- [ ] Testlerin henüz işlevler yokken başarısız olduğunu gör; sonra `geometry.py` ve `controller.py` işlevlerini uygula. `NaN`, sonsuz sayı ve sıfır görüntü boyutunda hareket üretme.
- [ ] Uçuş düğümü `udpin:0.0.0.0:14560` üzerinden MAVProxy'ye bağlansın. Seçilen autopilot'un heartbeat'ini ve hedef sistem/bileşen kimliklerini doğrulasın; bir GCS heartbeat'ini uçuş kontrolcüsü sanmasın. Ayrı bir companion kaynak kimliği kullan; Mission Planner kimliğini gelişigüzel kopyalama.
- [ ] MAVLink almak için bloklayan sonsuz beklemeyi ROS callback'ine koyma. Telemetriyi düzenli ve bloklamadan işle; bağlantı durumunu güncelle.
- [ ] Uçuş komutu yalnızca güncel heartbeat, armed, GUIDED ve yeni komut koşullarında gönderilsin. Başlangıçta otomatik arm veya mod geçişi yapılmasın.
- [ ] `SET_POSITION_TARGET_LOCAL_NED` mesajını **gövdeye göre hız** için `MAV_FRAME_BODY_NED` ile kullan. Hız alanları etkin, konum/ivme/yaw alanları yok sayılan maske `3527` (hex `0x0DC7`) olsun. `vx=forward`, `vy=right`, `vz=0`. Bu ayrıntıları [ArduPilot Guided komut belgesiyle](https://ardupilot.org/dev/docs/copter-commands-in-guided-mode.html) kontrol et.
- [ ] 10 Hz komut akışı, sıfır hız isteği ve komut watchdog'u uygula. Hız isteği 0,30 gerçek saniyeden eskiyse ve drone hâlâ GUIDED/armed ise sıfır hız iste; bir önceki hızı sürdürme.
- [ ] Açılışta veya hiç görev başlatılmamışken otomatik sıfır hız akışı da gönderme. Açık durdurma veya etkin görevde watchdog tetiklenmesi sonrasında, eski hareketi kesmek için kısa sıfır hız geçişi uygula; ardından yazıcının pasif duruma geçtiğini belgeleyip dene. Operatör mod değiştirmişse sıfır komutuyla bile müdahale etme. Yeniden hareket için yeni başlatma gerekir. `ALIGNED` durumunda ise görev açık kaldığı sürece sıfır hızla bekleme sürer.
- [ ] Platform tespiti yerine sahte merkez hataları ver. Önce uçuş arayüzünün yalnızca göndereceği komutu logladığı `dry_run` biçiminde çalıştır; sonra simülasyonda dene.
- [ ] Drone havadayken 0,10 m/s hızla yaklaşık 1 saniyelik ileri/geri/sağ/sol denemeleri yap; her birinin ardından sıfır hız gönder. Aynı anda başka yazılım hız komutu vermesin.

### Eksen doğrulama tablosu

| Sahte hedef | Beklenen komut | Drone hareket edince beklenen görüntü değişimi |
|---|---|---|
| Merkez | Sıfır | Hata büyümemeli |
| Sağ | Sağa | Platform merkeze yaklaşmalı |
| Sol | Sola | Platform merkeze yaklaşmalı |
| Üst | İleri | Platform merkeze yaklaşmalı |
| Alt | Geri | Platform merkeze yaklaşmalı |

Son sütun önemlidir: Drone doğru gövde yönünde gidiyor gibi görünse bile kameradaki hata artıyorsa kapalı çevrim yönü yanlıştır. Kamera pozunu ve dönüşümü kontrol et; rastgele kontrol kazancı değiştirerek çözmeye çalışma.

### Doğrulama ve kabul

- [ ] `python -m pytest ros_ws/src/drone_alignment/test -q` ile o güne kadar yazılan ilgili testler geçiyor.
- [ ] Komut kesilince watchdog devreye giriyor; eski hız tekrar tekrar gönderilmiyor.
- [ ] Mission Planner'dan uçuş modu değişince düğüm GUIDED'e geri almıyor ve komut göndermeyi kesiyor.
- [ ] Dört yönün hem simülasyon hareketi hem görüntü etkisi yazılı olarak doğrulandı.

**Takılırsan:** Modeli bu teste katma. Tüm eksenler yanlışsa MAVLink çerçevesi; yalnızca görüntü eşlemesi yanlışsa kamera montajı/dönüşümü üzerinde dur.

---

<a id="gun-11"></a>
## Gün 11 — Canlı görüntüyle kapalı çevrim hizalanma

**Amaç:** Eğitilmiş modelin çıktısı drone'un hareketini yönetsin.

**Dosyalar:** `approach_node.py`, `state_machine.py`, `test_state_machine.py`, `alignment.launch.py`, `configs/alignment.yaml`.

### Durum makinesi

| Durum | Giriş / davranış |
|---|---|
| `IDLE` | Görev kapalı. Kendiliğinden uçuş başlatılmaz. |
| `WAITING_TARGET` | Görev açıldı; uçuş hazır ve uygun tespit bekleniyor. Yatay hız sıfır. |
| `ALIGNING` | Uygun, yeni tespit var; merkez hatasından hız üretiliyor. |
| `ALIGNED` | Görüntü hatası eşik içinde kesintisiz 3 simülasyon saniyesi kaldı. Sıfır hızla bekleniyor. |
| `TARGET_LOST` | Hedef kayboldu/eskidi. Sıfır hız; yeniden hareket için açık yeniden başlatma gerekir. |
| `ABORTED` | Operatör durdurdu, uçuş hazır değil veya saat sıfırlandı. Görev kapatılır. |

Görevi açma komutu kalkış komutu değildir. Drone zaten havada ve GUIDED olmalıdır. `ALIGNED` sonrasında kendiliğinden iniş yapılmaz. Platform sonradan hafifçe kayarsa bu sürümde yeni yaklaşma komutuyla yeniden hizalanır; hareketli platform takibi eklenmez.

### Adımlar

- [ ] Önce durum makinesinin testlerini yaz: başlangıç kapalı; tespit yokken sıfır; merkezlenme kesintisiz olmalı; kayıp/hedef eskimesinde durmalı; yeniden başlatılmadan otomatik hareket olmamalı.
- [ ] `/approach/enable` servisini uygula. Uçuş hazır değilse başlatmayı reddet ve anlaşılır yanıt dön.
- [ ] Her yeni tespitte kaynak damgasını ve gerçek giriş yaşını kontrol et. Sırası geçmiş görüntü veya önceki göreve ait gözlemi reddet.
- [ ] Kontrolü yaklaşık 10 Hz çalıştır; son gözlem 0,50 gerçek saniyeden eskiyse yeni komut üretme, durma durumuna geç. Yeni timer çağrısı eski görüntüyü yeniymiş gibi damgalamasın.
- [ ] Kontrol zamanı ve hizalanma beklemesi için ROS simülasyon saatini kullan. `/clock` geriye sıçrarsa geçmiş gözlem ve bekleme sayacını temizle; tekrar başlatılmayı bekle.
- [ ] Başlangıçta platform neredeyse merkezde olsun; ardından 0,5 metre ve 1 metre başlangıç ofsetlerini dene.
- [ ] Hız sınırı ve kazancı düşük tut. Hedef çevresinde salınım varsa önce eksenleri ve gecikmeyi kontrol et; sonra kazancı azalt.
- [ ] Launch dosyasına uçuş ve yaklaşma düğümlerini ekle. Varsayılan görev durumu kapalı kalsın.

Başlatma/durdurma komutları:

```bash
ros2 service call /approach/enable std_srvs/srv/SetBool '{data: true}'
ros2 service call /approach/enable std_srvs/srv/SetBool '{data: false}'
```

Durumu izle:

```bash
ros2 topic echo /approach/state
```

### Gün sonu kabulü

- [ ] Basit sahnede en az üç farklı başlangıç noktasından modelle hizalanma gözlendi.
- [ ] Başlat/durdur çalışıyor; açılışta drone kendiliğinden hareket etmiyor.
- [ ] `ALIGNED` durumu ve görüntüdeki merkezlenme birbiriyle tutarlı.
- [ ] 3 saniyelik bekleme tespit kaybında sıfırlanıyor; parçalı süreler toplanmıyor.

**Kontrol noktası 4:** Projenin ana davranışı çalışıyor. Bundan sonra yeni özellik eklemek yerine başarısızlıkları ve ölçümleri tamamla.

---

<a id="gun-12"></a>
## Gün 12 — Hedef kaybını, eski veriyi ve gecikmeyi ölç

**Amaç:** Sistem yalnızca ideal koşulda çalışmasın; ne zaman duracağını bilsin ve nedenlerini kaydetsin.

### Saatleri doğru ayır

İki farklı zaman alanı tut:

1. **ROS simülasyon zamanı:** Kamera `header.stamp`, `/clock`, görev süresi ve Gazebo gerçek pozları. Kamera oluşumundan komut gönderimine kadar geçen **simülasyon zamanı** bu alan içinde hesaplanabilir. RTF'yi yanında raporla.
2. **Monoton gerçek zaman:** Aynı Ubuntu VM'inde `time.monotonic_ns()` ile callback girişi, çıkarım, kontrol ve komut gönderimi. İşlem gecikmesi, watchdog ve performans için kullanılır.

Görüntü kaynak damgası simülasyon zamanıyken ondan Windows saatini veya monoton zamanı çıkarma. VM'deki monoton zamanı Windows'a taşıyıp iki bilgisayar arasında doğrudan fark alma.

Gerçek süre metriğinin adı açık olsun:

```text
pipeline_wall_ms = (mavlink_send_steady_ns - ingress_steady_ns) / 1_000_000
```

Bu, **görüntünün ROS callback'ine girişinden MAVLink gönderimine** kadar süredir. Kamera sensörünün gerçek duvar saatiyle görüntü üretme anını ayrıca ölçmediğin için bunu tam sensörden motor tepkisine gecikme diye sunma. MAVLink gönderimi, ArduPilot'un komutu aldığı/uyguladığı an değildir.

### Adımlar

- [ ] `flight_interface_node` gönderim anında `latency.csv` satırı üretsin. Alanlar:

```text
trial_id,frame_stamp_ns,ingress_steady_ns,command_steady_ns,send_steady_ns,inference_ms,pipeline_wall_ms,observation_age_sim_ms,state,forward_mps,right_mps
```

- [ ] Aynı görüntüden birden fazla komut üretilirse ilk gönderim ve tekrarları ayırt et. Model hızını komut tekrar sayısından hesaplama.
- [ ] Ön işleme/son işleme sürelerini mümkünse ayrı kaydet. CSV yazmayı her karede diski zorlayacak senkron işlemlerle yapma; küçük tampon ve düzenli flush yeterli.
- [ ] Gerçek zaman watchdog'unu simülasyon duraklasa da çalışabilecek monoton saatli timer/denetimle kur. Simülasyon saatiyle durmuş timer'ın gerçek süre güvence verdiğini varsayma.
- [ ] Aşağıdaki hata denemelerini ayrı çalıştır:

| Deneme | Beklenen |
|---|---|
| Platform görünmez oldu | `TARGET_LOST`, sıfır yatay hız isteği |
| Kamera köprüsü kapandı | Son gözlem yaşlanır; eski hız sürdürülmez |
| Dedektör durdu | Aynı tespit sonsuza kadar kullanılmaz |
| Yaklaşma düğümü durdu | Uçuş arayüzünün komut watchdog'u durdurur |
| Mission Planner'da mod değişti | `MANUAL_OVERRIDE`, yeni hareket komutu yok |
| Simülasyon duraklatıldı/sıfırlandı | Zaman ölçümü bozulmaz; reset sonrası açık yeniden başlatma gerekir |

- [ ] Gecikme etkisi için normal durum ile **ek 100 ms ve 200 ms** gecikmeli iki koşul dene. Bu yapay gecikme yalnızca test parametresiyle, kaynak damgasını değiştirmeden eklensin. Normal çalışmada kapalı olsun.
- [ ] Gecikme enjekte ederken bütün ROS executor'ını `sleep` ile kilitleme; gözlem teslimini planla veya ayrı worker kullan. Watchdog çalışmaya devam etsin.
- [ ] Daha yüksek gecikmede salınım, daha uzun süre veya zaman aşımı olursa bunu raporla. Her gecikmeyi gizlemek için kazancı değiştirip aynı deney diye sunma.

### Gün sonu kabulü

- [ ] Kayıp/eski veri ve süreç kesilmesi durumları kayıtlarla doğrulandı.
- [ ] Komut yaşı 0,30 saniyeyi aşan aralıkta eski sıfır olmayan komutlar tekrarlanmıyor; gözlem yaşı sınırı da ayrıca kontrol ediliyor.
- [ ] p50/p95 gerçek işlem süreleri ve simülasyon zamanı ölçümü birbirinden ayrı.
- [ ] İki ek gecikmenin etkisi için küçük karşılaştırma var.

**Takılırsan:** Önce tek bir `frame_stamp_ns` değerini düğümler arasında takip et. Damgaları her aşamada yenilemek sorunu çözüyor gibi gösterir ama ölçümü bozar.

---

<a id="gun-13"></a>
## Gün 13 — Önceden belirlenmiş görev denemelerini çalıştır

**Amaç:** Başarılı bir videodan daha güçlü, tekrarlanabilir sonuç üretmek.

**Dosyalar:** `evaluation/cases.csv`, `evaluation/log_ground_truth.py`, `evaluation/summarize_trials.py`, `reports/test_protocol.md`, `reports/trials.csv`.

### Adımlar

- [ ] Modeli ve kontrol parametrelerini bugünün başında dondur. Başarısız final testten sonra ayar değiştirirsen yeni sürüm olarak tüm protokolü tekrar et; ilk sonucu gizleme.
- [ ] Modelin ayrılmış görüntü test kümesindeki son metriklerini bir kez raporla. Test sonuçlarını hiperparametre seçimine geri besleme.
- [ ] Görev için 10 başlangıç koşulunu baştan yaz. Önerilen dağılım: dört ana yönde dört deneme, dört çapraz yönde dört deneme, iki farklı zemin/ışıkta iki deneme. Ofsetleri 0,5–2 metre aralığında tut; platformun görünür olduğunu kontrol et.
- [ ] `cases.csv` alanları: `case_id,scene_id,offset_x_m,offset_y_m,height_m,yaw_deg,model_id,config_id`.
- [ ] Gazebo'nun gerçek poz topic'ini `gz topic -l` ile keşfet. Denetleyiciye bağlamadan, ayrı `log_ground_truth.py` aracında drone ve platform dünya pozlarını isimleriyle ayıkla. Kamera/gimbal bağlantı pozunu drone kök pozu sanma.
- [ ] Gazebo poz akışını gerekirse köprüle; veri tipini gerçek topic'ten doğrula. Ortak dünya çerçevesi ve aynı simülasyon damgasıyla kaydet. Telemetri NED ile Gazebo ENU pozlarını dönüşümsüz birbirinden çıkarma.
- [ ] Her denemeyi aynı hazırlık sırasıyla başlat: sahne hazır, drone havada, GUIDED hazır, log açık, yaklaşma servisi açılır.
- [ ] Başarıyı 6. bölümdeki metre/süre koşuluyla bağımsız hesapla. Kamera kadrajından çıkan veya zaman aşan denemeyi sessizce listeden çıkarma; başarısız say ve nedenini yaz.
- [ ] Deneme bittikten sonra görevi durdur. Başlangıç konumuna dönüşü ayrı, manuel hazırlık adımı olarak yap.

### Sonuç dosyası

```text
trial_id,case_id,success,alignment_time_sim_s,final_error_m,hold_duration_sim_s,pipeline_p50_ms,pipeline_p95_ms,rtf_mean,failure_reason
```

Ek olarak hata–zaman ve komut–zaman grafiği üret. Basit bir CSV ve Matplotlib grafiği yeterli; panel geliştirme.

### Gün sonu kabulü

- [ ] 10 denemenin tamamı kayıtlı; başarı ve başarısızlıklar birlikte raporlandı.
- [ ] Gerçek merkez uzaklığı kontrol düğümünden bağımsız ölçüldü.
- [ ] 8/10 hedefi sağlandıysa kanıtı var; sağlanmadıysa gerçek sayı ve hata sınıfları yazılı.

**Takılırsan:** Gazebo gerçek pozunu alamadıysan piksel merkez hatasını metre diye yazma. Eksik metriği açıkça belirt ve ölçüm aracını tamamla. Çok başarısız görevde önce tespit, eksen, gecikme ve kazancı ayrı ayrı incele.

---

<a id="gun-14"></a>
## Gün 14 — ONNX'e aktar ve PyTorch ile adil hız karşılaştırması yap

**Amaç:** Aynı eğitilmiş modeli farklı çalıştırma biçimlerinde kullanabilmek ve etkisini ölçmek.

**Dosyalar:** `training/export_onnx.py`, `models/platform_best.onnx`, `evaluation/benchmark_backends.py`, `reports/backend_comparison.csv`.

### Adımlar

- [ ] Seçilen `platform_best.pt` modelinden ONNX üret. İlk aktarım sabit 416 giriş, batch 1, FP32 ve dinamik şekil kapalı olsun. [Ultralytics ONNX aktarım belgesindeki](https://docs.ultralytics.com/integrations/onnx/) API'yi kullan; checkpoint'in YOLO11 olduğunu kaydet.
- [ ] NMS'nin modelin içine gömülüp gömülmediğini açık seç. İlk sürümde her iki backend için aynı Ultralytics son işleme yolunu kullanmak işleri azaltır. Ham ONNX çıktısını `.pt` kutularıyla doğrudan karşılaştırma.
- [ ] Ubuntu proje ortamında `onnxruntime` CPU paketini kur; aktif execution provider'ın `CPUExecutionProvider` olduğunu kontrol et. GPU paketi kurulu diye GPU'nun kullanıldığını varsayma.
- [ ] `detector_node` için `backend=pytorch` ve `backend=onnx` seçeneği ekle. ROS mesajları, kutu koordinatları, eşikler ve kontrol davranışı değişmesin.
- [ ] Aynı sabit görüntü listesini kullan; eğitimden bağımsız seçilmiş bu listede en az 30–50 ısınma çıkarımı sonrası 200 ölçümlü çıkarım yap. Disk okuma ve model yükleme ilk çıkarım maliyeti olarak ayrı raporlansın.
- [ ] Önce çıktıları karşılaştır: sınıf, kutu merkez/boyut farkı ve test metrikleri. Küçük sayısal fark olabilir; belirgin farkta renk, normalizasyon, letterbox ve NMS'yi incele.
- [ ] Her iki backend'i aynı Ubuntu VM'de CPU, FP32, batch 1 ve aynı girişte ölç. Thread ayarını, Gazebo'nun açık/kapalı oluşunu ve VM kaynaklarını kaydet. Ana tablo Gazebo açıkken olsun; modelin tek başına ölçümünü ayrıca verebilirsin.
- [ ] p50, p95, toplam geçen süreden hesaplanan throughput ve doğruluk farkını kaydet. Tek görüntü gecikmesinden bütün sistem FPS'ini çıkardığını iddia etme.
- [ ] Windows CUDA ölçümü eklemek istersen ayrı tablo yap. GPU ölçümünde ısınma ve uygun senkronizasyon kullan. [PyTorch benchmark rehberi](https://docs.pytorch.org/tutorials/recipes/recipes/benchmark.html) bu farkı açıklar.

### Karşılaştırma tablosu

| Ortam | Backend | Cihaz | Girdi | Model p50/p95 | Ön+model+son işlem p50/p95 | Throughput | Doğruluk |
|---|---|---|---|---|---|---|---|
| Ubuntu VM | PyTorch | CPU | 416, FP32, batch 1 | Ölçülecek | Ölçülecek | Ölçülecek | Ölçülecek |
| Aynı Ubuntu VM | ONNX Runtime | CPU | 416, FP32, batch 1 | Ölçülecek | Ölçülecek | Ölçülecek | Ölçülecek |

Tabloda “Ölçülecek” bırakmak final teslimde kabul edilmez; bu belge uygulama planı olduğu için henüz sayı uydurulmuyor. ONNX daha hızlı çıkmak zorunda değildir. Değer, sonucu doğru yöntemle ölçmendir.

### Gün sonu kabulü

- [ ] ONNX modeli yükleniyor ve tespitler `.pt` ile tutarlı.
- [ ] Adil CPU karşılaştırması ve yapılandırması kaydedildi.
- [ ] ONNX backend'inde en az üç canlı hizalanma denemesi yapıldı.
- [ ] Final demoda kullanılacak backend seçildi; değiştirdiysen gün 13'ün 10 görev denemesini final backend ile tekrar et.

**Takılırsan:** Export uyumluluğu sorununda checkpoint, Ultralytics, ONNX, opset ve Runtime sürümlerini kaydet; desteklenen kombinasyonu kullan. TensorRT, FP16 ve INT8'i aynı gün ekleme.

---

<a id="gun-15"></a>
## Gün 15 — Sistemi yeniden aç, demo kaydet ve portföy teslimini tamamla

**Amaç:** Kendi bilgisayarında yalnızca bir kez çalışmış deneyden, açıklanabilir ve yeniden çalıştırılabilir projeye geçmek.

### Yeniden başlatma provası

- [ ] Tüm proje süreçlerini normal biçimde kapat ve yeni terminallerle yeniden aç. Çalışması için gizli kalan elle verilmiş komut varsa README'ye ekle.
- [ ] Kurulum bir defalık, çalıştırma günlük adım olarak ayrı yazılsın.
- [ ] Simülasyonu tek yerden başlat. İkinci SITL veya ikinci komut yazıcısı açılmadığını kontrol et.
- [ ] Launch dosyası kamera köprüsü, dedektör, yaklaşma ve uçuş arayüzünü başlatsın. ArduPilot/Gazebo ayrı başlatılıyorsa bunu açıkça yaz; tek komut iddiası yapma.
- [ ] Bütün ROS terminallerinde gereken kaynaklama sırasını belgeye koy:

```bash
source /opt/ros/jazzy/setup.bash
source ~/projects/drone_alignment/.venv/bin/activate
source ~/projects/drone_alignment/ros_ws/install/setup.bash
```

- [ ] İlgili testleri çalıştır; ROS derlemesini doğrula. README'deki komutlarla bir tam görev ve bir hedef kaybı denemesi yap.

### README içeriği

- [ ] Problem ve tek paragrafta çözüm.
- [ ] Mimari şeması; hangi parçayı senin yazdığın ve hangisinin hazır araç olduğu.
- [ ] Windows/Ubuntu görev dağılımı ve sürümler.
- [ ] Kurulum, çalıştırma, kalkış, görevi başlatma/durdurma sırası.
- [ ] Veri üretimi, etiket kuralı, eğitim komutu ve modelin kaynağı.
- [ ] Model/ONNX dosyalarının edinilmesi; gerekli veri örnekleri.
- [ ] Algılama, gecikme, backend ve görev başarı tabloları.
- [ ] Bilinen sınırlar: simülasyon, başlangıçta görünür hedef, sabit kamera, yaklaşık sabit yükseklik/yaw, iniş yok.
- [ ] Başarısız örnekler ve sonraki tek geliştirme fikri.

### Demo videosu: 2–3 dakika

1. 15–20 saniye: Görevi ve kullanılan parçaları göster.
2. 30–45 saniye: Mission Planner kalkışı, canlı kamera ve model tespitini göster.
3. 30–45 saniye: Hizalanma komutunu ver; durum ve hata azalışı görünür olsun.
4. 20–30 saniye: Platform kaybında durma davranışını göster.
5. 20–30 saniye: Ölçülmüş sonuç tablosunu göster; en iyi denemeyi bütün sonuçmuş gibi sunma.

### Son teslim ve kabul kontrol listesi

- [ ] Kod ve yapılandırmalar Git'te; büyük/geçici dosyalar hariç.
- [ ] Veri kartı ve eğitim deney kaydı var.
- [ ] Seçilen `.pt` ve `.onnx` modelinin sürümü/hash'i belli.
- [ ] 10 görev denemesinin tamamı ve hedef kaybı testleri kayıtlı.
- [ ] Gecikme tanımları ve gerçek/simülasyon zamanı ayrımı yazılı.
- [ ] PyTorch–ONNX Runtime karşılaştırması gerçek ölçümler içeriyor.
- [ ] Yeni terminallerle baştan çalıştırma başarılı.
- [ ] Demo ve son rapor hazır; simülasyon başarısı gerçek drone başarısı diye sunulmuyor.

**CV/portföy anlatımı için sonuçtan sonra doldurulacak cümle:** “Gazebo ve ArduPilot SITL üzerinde, kendi oluşturduğum simülasyon verileriyle uyarladığım nesne tespit modelini ROS 2 düğümlerine entegre ederek görsel platform hizalanması geliştirdim; görev başarısını, uçtan uca tanımlanmış işlem gecikmesini ve PyTorch/ONNX Runtime performansını ölçtüm.” Sayısal sonuçları yalnızca elde ettikten sonra ekle.

---

<a id="sorunlar"></a>
## Ek A — Takılınca ne yapılacak?

### 1. Gazebo yavaş veya kamera açılınca çöküyor

1. `glxinfo -B` ile çizim motorunu, terminalde OpenGL/Ogre hatasını kontrol et.
2. Kamera kapalı basit dünyayı dene. Bu da yavaşsa model eğitimiyle ilgisi yoktur.
3. Kamera çözünürlüğünü/Hz değerini azalt; gölge, fazla model ve yüksek GUI çözünürlüğünü azalt.
4. VM kaynaklarını Windows'u da rahat bırakacak biçimde ayarla.
5. RTF ve çıkarım hızını yeniden ölç. Hâlâ uygulanabilir değilse WSL 2/yerel Linux kararını erken ver; iki haftanın sonuna erteleme.

### 2. Mission Planner bağlanmıyor

1. MAVProxy'de telemetri var mı? Yoksa önce SITL'yi düzelt.
2. NAT/Bridged ağ modunu ve Windows adaptör IP'sini kontrol et.
3. UDP 14550'yi Mission Planner'ın dinlediğini, MAVProxy'nin doğru Windows IP'sine gönderdiğini doğrula.
4. Aynı portu başka bir programın kullanmadığını kontrol et. Linux'ta `ss -lunp`, Windows'ta ilgili bağlantı/uygulama bilgisinden yararlan.
5. Uygulamaya özel ağ iznini kontrol et; güvenlik duvarını kapatmayı çözüm kabul etme.

### 3. ROS görüntü topic'i var ama görüntü gelmiyor

1. Gazebo sensörü veri üretiyor mu ve simülasyon pause durumunda mı?
2. Köprüde Gazebo topic adı, mesaj tipi ve `GZ_TO_ROS` yönü doğru mu?
3. Abonenin QoS'u sensör yayınıyla uyumlu mu?
4. Ham görüntüyü `rqt_image_view` ile aç. Görüntü yokken dedektör kodunu değiştirme.

### 4. `rclpy`, `cv_bridge`, NumPy veya OpenCV import hatası

1. `which python`, `python --version`, `python -m pip --version` ve `printenv ROS_DISTRO` çıktısını kaydet.
2. Ubuntu 24.04'ün Python 3.12 tabanıyla uyumlu sistem yorumlayıcısından açılmış `--system-site-packages` ortamı kullandığını doğrula.
3. ROS kurulumu source edilmiş mi kontrol et. Sistem Python'u ile venv Python'unu ayrı ayrı dene; hangi paketin hangi ortamda bozulduğunu bul.
4. Binary NumPy hatası varsa kurulu paket sürümlerini incele; apt `cv_bridge` ile uyumsuz pip NumPy/OpenCV birleşimini izole ortamda düzelt.
5. Sorunu `sudo pip`, `--break-system-packages` veya tüm ROS'u yeniden kurarak büyütme.

### 5. Model iyi görünüyor ama drone platformdan uzaklaşıyor

1. Görevi durdur; görüntü merkezi, yayımlanan piksel koordinatları ve seçilen kutuyu kontrol et.
2. Modeli devreden çıkarıp gün 10'un sahte hata testini tekrar yap.
3. Kamera görüntüsünün üstü gerçekten gövde ilerisi mi? Görüntü aynalanmış/döndürülmüş mü?
4. MAVLink gövde hız çerçevesi ve işaretleri doğru mu?
5. Bunlar doğruysa veri yaşı ve kuyruğa bak; sonra kontrol kazancını değiştir.

### 6. Drone merkez etrafında salınıyor

1. Tespit merkezi titreşiyor mu; kutu başka nesneye atlıyor mu?
2. Gecikme/kuyruk büyüyor mu? Yeni yerine eski görüntü mü işleniyor?
3. Maksimum hızı ve kazancı azalt; aynı başlangıç koşulunda tekrar dene.
4. Gerekirse küçük bir merkez ölü bölgesi kullan; filtre eklersen getirdiği ek gecikmeyi kaydet.
5. PID, Kalman veya optical flow'u ilk tepki olarak ekleme. Sorunun nedenini önce ayır.

### 7. Eğitim başarılı ama yeni sahnede tespit yok

1. Görüntü boyutu, renk dönüşümü, kutu geri ölçeklemesi ve doğru model dosyasını kontrol et.
2. Eğitim örnekleri yeni zemini/ölçeği/ışığı temsil ediyor mu?
3. Hata örneklerini yalnızca eğitim verisine ekle; ayrılmış test setini eğitim verisine katma.
4. Modeli büyütmeden önce çeşitlilik ve etiket doğruluğunu iyileştir.

### 8. Takvim sarktı

Korunacak sıra:

1. Model olmadan uçuş ve kamera.
2. Küçük doğru veri, tek eğitim ve canlı algılama.
3. Basit hizalanma ve hedef kaybında durma.
4. Ölçüm, görev denemeleri ve anlaşılır demo.
5. İkinci eğitim deneyi ve ONNX karşılaştırması.
6. Otomatik etiketleme/dekorasyon gibi ekler.

Bu belgede ikinci deney ve ONNX planlanan teslimdir. Gerçek süre yetmezse bunları sessizce tamamlanmış sayma; eksik kalanları raporda işaretleyip kalan işi sonraki oturuma taşı. Tekrar edilebilir çekirdek görev, çalışmayan ek özelliklerden önce gelir.

---

<a id="gunluk"></a>
## Ek B — Her gün doldurulacak kısa kayıt

Aşağıdaki şablonu `reports/diary.md` içinde her gün kopyala. Bu kayıt, sonraki gün aynı hatayı tekrar araştırmamanı sağlar.

```markdown
## Gün numarası / tarih

### Bugünkü amaç

### Tamamladığım işler
- [ ] Günün ana adımı
- [ ] Doğrulama

### Çalışan komutlar ve ortam

### Ölçtüğüm sonuçlar

### Başarısız olan deneme

### Hata mesajı ve çözümün nedeni

### Öğrendiğim üç şey

### Bir sonraki oturumun ilk işi

### İlgili commit / model / veri sürümü
```

Her çalışan aşamada küçük, anlamlı bir commit oluştur. Örneğin kamera entegrasyonu, veri kaydedici ve kontrol dönüşümü ayrı değişiklikler olabilir. Kontrol hatasını düzeltirken aynı commit'te model ailesini de değiştirme.

### Öğrenmeyi kontrol etmek için günlük sorular

| Gün | Kendi cümlelerinle açıklayabilmen gereken soru |
|---|---|
| 1 | VM grafik hızlandırmasıyla CUDA neden ayrı? |
| 2 | Gazebo, SITL ve Mission Planner'ın görevleri ne? |
| 3 | Topic adı, mesaj tipi ve QoS neden birlikte önemli? |
| 4 | Bir veri kaydının hangi sahneden geldiğini neden saklıyorum? |
| 5 | Aynı videonun komşu karelerini train/test'e bölmek neden yanıltır? |
| 6 | YOLO kutusu piksel koordinatından nasıl farklı? |
| 7 | Loss, backward ve optimizer ne yapıyor; benim çalışmam neden fine-tuning? |
| 8 | Validation ile model seçip test'i ayırmanın amacı ne? |
| 9 | Model giriş boyutuyla yayınlanan görüntü koordinatları neden farklı olabilir? |
| 10 | Görüntüde sağdaki hedef için hangi gövde hızını üretiyorum? |
| 11 | Açık çevrim komutla kapalı çevrim yaklaşma arasındaki fark ne? |
| 12 | Neden simülasyon damgasından gerçek bilgisayar saatini çıkarmıyorum? |
| 13 | Kutunun ortalanmasıyla gerçek platform merkezine uzaklık neden aynı ölçüm değil? |
| 14 | ONNX formatı ile ONNX Runtime arasındaki fark ne? |
| 15 | Başka biri projeyi açtığında hangi adımları izleyerek aynı sonucu görebilir? |

---

<a id="ekler"></a>
## Ek C — Temel sürüm bittikten sonra seçilebilecek genişletmeler

Bu bölümü ilk 15 günün zorunlu işi gibi uygulama. Çekirdek görevi ve raporu bitirdikten sonra **tek birini** seç.

### C1. Otomatik etiketleme

Kazanım: Simülasyonun bilinen geometrisini eğitim verisine dönüştürmek.

1. Kameranın iç parametrelerini ve optik çerçevesini doğrula.
2. Platformun köşe noktalarını aynı görüntü zamanındaki kamera optik çerçevesine dönüştür.
3. Kamera önündeki noktaları görüntüye yansıt; kutuyu görüntü sınırlarına kırp.
4. Kamera arkasında kalan, tamamen kadraj dışında olan veya aşırı kesilen platformları işaretle.
5. İzdüşüm kutusunun nesnenin gerçekten görünür olduğunu garanti etmediğini unutma; örtülme ayrıca ele alınmalı.
6. En az 30 otomatik etiketi elle denetle; hatayı ölçmeden veri kümesini büyütme.

Ground-truth bilgisi yalnızca etiketleyicide kullanılacak. Kontrol düğümüne bu bilgiyi vermek görsel algılamanın yerine geçer ve projenin iddiasını değiştirir.

### C2. Hassas iniş

Kazanım: Merkezlenmeden kontrollü alçalmaya geçiş.

Önce hedef konumu/açısı, kamera kalibrasyonu, yükseklik bilgisi ve ArduPilot iniş davranışını çalış. Sadece `LAND` moduna geçmenin görsel hassas iniş sistemi kurmakla aynı olmadığını ayır. ArduPilot'un [precision landing arayüzü](https://ardupilot.org/dev/docs/mavlink-precision-landing.html) ayrı bir entegrasyon konusudur. Bunu mevcut hizalanma projesine bir akşamlık zorunlu ek gibi değerlendirme.

### C3. Gerçek kamera ile algılama doğrulaması

Kazanım: Simülasyon–gerçek görüntü farkını görmek.

Gerçek drone uçurmadan, basılı/üretilmiş platform örneğini elde tutulan kamera veya masa düzeninde algıla. Simülasyonda iyi sonuç veren modelin gerçek görüntüde başarısını ayrıca ölç. Bu aşama uçuş aktarımı değil, algılama aktarımı denemesidir.

---

<a id="kaynaklar"></a>
## Ek D — Kavram sözlüğü ve resmî kaynaklar

### Kısa sözlük

| Kavram | Bu projedeki anlamı |
|---|---|
| SITL | Gerçek uçuş kontrol yazılımının bilgisayarda çalışan simülasyon sürümü. |
| Gazebo | Fizik, sensör ve sahne simülasyonu. |
| Mission Planner | Uçuş durumu, mod ve görev kontrolü için yer istasyonu. |
| MAVProxy | MAVLink bağlantılarını yönlendiren araç/konsol. |
| MAVLink | Uçuş yazılımıyla telemetri ve komut haberleşme protokolü. |
| Node / düğüm | Belirli sorumluluğu olan ROS 2 süreci. |
| Topic | Düğümler arasında sürekli mesaj akışı. |
| Service | Başlat/durdur gibi istek–yanıt işlemi. |
| QoS | Mesaj teslimi, güvenilirlik ve kuyruk davranışı ayarları. |
| Ground truth | Değerlendirmede karşılaştırma için kullanılan simülatörün gerçek poz/etiket bilgisi. |
| Fine-tuning | Önceden eğitilmiş modeli kendi verine uyarlama. |
| Augmentation | Eğitim örneğinin görünümünü kontrollü değiştirme. |
| Precision | Pozitif tespitlerin ne kadarının doğru olduğu. |
| Recall | Gerçek hedeflerin ne kadarının bulunduğu. |
| IoU | Tahmin ve gerçek kutunun kesişim alanının birleşim alanına oranı. |
| mAP | Farklı eşiklerde nesne tespit başarısını özetleyen ölçüm ailesi. |
| Letterbox | En-boy oranını koruyarak yeniden boyutlandırma ve kenar doldurma. |
| Closed-loop / kapalı çevrim | Yeni görüntüye göre bir sonraki hareket komutunu düzeltmek. |
| Watchdog | Yeni veri/komut gelmeyince eski davranışı durduran süre denetimi. |
| RTF | Simülasyon zamanının gerçek zamana oranı; 1, yaklaşık gerçek zamanlı çalışma. |
| p95 | Ölçümlerin %95'inin altında kaldığı değer. |
| ONNX | Modeli farklı çalıştırıcılara taşıyan dosya/hesap grafiği biçimi. |
| ONNX Runtime | ONNX modelini çalıştıran yazılım. |

### Gerektiği gün okunacak kaynaklar

| Konu | Birincil kaynak | Ne için kullanacaksın? |
|---|---|---|
| Sürüm eşleşmesi | [Gazebo ve ROS kurulumu](https://gazebosim.org/docs/harmonic/ros_installation/) | Jazzy–Harmonic eşleşmesini korumak. |
| Gazebo kurulum | [Harmonic Ubuntu paketleri](https://gazebosim.org/docs/harmonic/install_ubuntu/) | Noble/Ubuntu 24.04 kurulumu. |
| ROS köprüsü | [Gazebo ROS 2 etkileşim öğreticisi](https://gazebosim.org/docs/harmonic/ros2_integration/) | Görüntü/saat köprüsü, topic ve mesaj tipi. |
| ArduPilot kurulum | [Linux geliştirme ortamı](https://ardupilot.org/dev/docs/building-setup-linux.html) | SITL bağımlılıkları. |
| Gazebo–SITL | [Resmî ArduPilot Gazebo eklentisi](https://github.com/ArduPilot/ardupilot_gazebo) | Eklenti, model, örnek dünya. |
| GCS bağlantısı | [SITL kullanımı](https://ardupilot.org/dev/docs/using-sitl-for-ardupilot-testing.html) | Mission Planner/MAVProxy yönlendirme. |
| Hız komutları | [Copter Guided komutları](https://ardupilot.org/dev/docs/copter-commands-in-guided-mode.html) | Gövde hız çerçevesi ve maske. |
| Python MAVLink | [Pymavlink kullanımı](https://mavlink.io/en/mavgen_python/) | Heartbeat, bağlantı ve mesaj gönderimi. |
| Windows GPU eğitimi | [PyTorch yerel kurulum](https://pytorch.org/get-started/locally/) | Doğru CUDA destekli paket. |
| PyTorch mantığı | [PyTorch temel konular](https://docs.pytorch.org/tutorials/beginner/basics/intro.html) | Tensor, gradient ve eğitim döngüsü. |
| Model | [YOLO11](https://docs.ultralytics.com/models/yolo11/) | Seçilen nano dedektör ailesi. |
| Eğitim | [Ultralytics train](https://docs.ultralytics.com/modes/train/) | Fine-tuning parametreleri. |
| Veri biçimi | [Detection veri kümesi](https://docs.ultralytics.com/datasets/detect/) | Etiket ve YAML düzeni. |
| ONNX | [ONNX aktarımı](https://docs.ultralytics.com/integrations/onnx/) | Export ve model çalıştırma. |
| Ölçüm | [PyTorch benchmark](https://docs.pytorch.org/tutorials/recipes/recipes/benchmark.html) | Isınma, senkronizasyon ve ölçüm hataları. |
| Ortam alternatifi | [WSL GPU](https://learn.microsoft.com/en-us/windows/wsl/tutorials/gpu-compute) | Yalnızca VM yeterli olmazsa GPU erişimi alternatifi. |

Kurulum belgelerindeki sürümler zamanla değişebilir. Bir aşama çalıştıktan sonra kullanılan commit ve paket sürümlerini kaydet; proje ortasında sırf daha yeni sürüm çıktı diye ortamı değiştirme.
