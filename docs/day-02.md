# Gün 2 — ArduPilot, Gazebo ve Mission Planner

## Sonuç ve kanıt

Kullanıcı, Gazebo'daki Iris drone'unu önce MAVProxy, ardından Windows Mission Planner üzerinden kaldırıp indirdiğini doğruladı. Mission Planner'da normal arm işlemi ayrıca doğrudan gözlendi. Görsel hizalanma uygulaması henüz yazılmadı; kodları birlikte, öğrenerek yazacağız.

Bu, temel uçuş bağlantısı testidir. Konum hatası, hover kararlılığı, gerçek zaman faktörü veya gecikme için sayısal ölçüm henüz yok. Kamera görüntüsünün ROS'a aktarımı da henüz doğrulanmadı.

## Yazılımlar nerede ve ne yapıyor?

```text
~/projects/
├── aeroalign/                   # Bize ait proje ve belgeler
└── drone_alignment_vendor/      # Üçüncü taraf kaynak depoları
    ├── ardupilot/               # Uçuş kontrolcüsü ve SITL
    └── ardupilot_gazebo/        # Gazebo eklentisi, örnek model ve dünyalar
```

Gazebo'nun kendisi ROS Jazzy vendor paketleriyle `/opt/ros/jazzy/` altında kurulu. Vendor klasöründeki eklenti, Gazebo'dan sensör verilerini ArduPilot'a; ArduPilot'tan motor komutlarını Gazebo'ya taşır. MAVProxy ise MAVLink bağlantısını Mission Planner'a yönlendirir.

## Bir kez yapılan kurulum

ArduPilot, alt modülleriyle indirildi ve [resmî Ubuntu bağımlılık betiği](https://ardupilot.org/dev/docs/building-setup-linux.html) çalıştırıldı. Betik `~/venv-ardupilot` Python ortamını oluşturdu. Bu ortam uçuş simülatörüne aittir; Windows eğitim ortamından ve ileride oluşturulacak ROS/algılama ortamından ayrıdır.

Gazebo kurulumu şu kontrollerle belirlendi:

```bash
command -v gz
apt-cache policy libgz-sim8-dev ros-jazzy-gz-sim-vendor
```

`gz` yolu `/opt/ros/jazzy/opt/gz_tools_vendor/bin/gz`; kurulu vendor sürümü `0.0.13-1noble.20260905.073557`. Bağımsız Gazebo paket deposundaki `libgz-sim8-dev` bulunamadı. Mevcut ROS vendor kurulumu korunarak şu diğer bağımlılıklar kuruldu:

```bash
sudo apt install rapidjson-dev libopencv-dev pkg-config \
  libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev \
  gstreamer1.0-plugins-bad gstreamer1.0-libav gstreamer1.0-gl
```

Eklenti `~/projects/drone_alignment_vendor/ardupilot_gazebo` içine klonlandı. Derleme:

```bash
source /opt/ros/jazzy/setup.bash
export GZ_VERSION=harmonic
cd ~/projects/drone_alignment_vendor/ardupilot_gazebo
cmake -S . -B build -DCMAKE_BUILD_TYPE=RelWithDebInfo
cmake --build build --parallel 2
```

Dört hedef de tamamlandı: `ArduPilotPlugin`, `ParachutePlugin`, `CameraZoomPlugin`, `GstCameraPlugin`. Her açılışta bu kurulum ve derleme adımlarını yeniden yapmak gerekmez. [Vendor paketleri](https://gazebosim.org/docs/harmonic/ros2_gz_vendor_pkgs/) ve [eklenti belgesi](https://github.com/ArduPilot/ardupilot_gazebo).

## Yeniden çalıştırma — Terminal 1: Gazebo

Ubuntu'da aşağıdaki blok aynı terminalde çalışır. Export ayarları bu terminale aittir; `.bashrc` içine kalıcı ekleme yapılmadı.

```bash
source /opt/ros/jazzy/setup.bash
export ALIGN_GZ_ROOT="$HOME/projects/drone_alignment_vendor/ardupilot_gazebo"
export GZ_SIM_SYSTEM_PLUGIN_PATH="$ALIGN_GZ_ROOT/build:$GZ_SIM_SYSTEM_PLUGIN_PATH"
export GZ_SIM_RESOURCE_PATH="$ALIGN_GZ_ROOT/models:$ALIGN_GZ_ROOT/worlds:$GZ_SIM_RESOURCE_PATH"
cd "$ALIGN_GZ_ROOT"
gz sim -v 4 -r iris_runway_ogre.sdf --render-engine ogre
```

`iris_runway_ogre.sdf` henüz oluşturulmamış bir bilgisayarda, Gazebo komutundan önce şu bir defalık adım gerekir:

```bash
sed 's#<render_engine>ogre2</render_engine>#<render_engine>ogre</render_engine>#g' \
  worlds/iris_runway.sdf > worlds/iris_runway_ogre.sdf
```

Hem GUI hem de dünyadaki Sensors sistemi Ogre kullanır. Yalnızca GUI bayrağını değiştirmek, dünya dosyasının sensör motoru ayarını değiştirmez. Bu kopya vendor deposunda yerel bir kurulum uyarlamasıdır; Gün 3'te bize ait kamera/model dosyaları AeroAlign reposuna eklenecek.

Gazebo açık ve simülasyon çalışır durumda kalsın. [Örnek dünya](https://github.com/ArduPilot/ardupilot_gazebo/blob/main/worlds/iris_runway.sdf).

## Terminal 2: ArduPilot SITL

Yeni Ubuntu terminali:

```bash
source ~/venv-ardupilot/bin/activate
cd ~/projects/drone_alignment_vendor/ardupilot/ArduCopter
python3 ../Tools/autotest/sim_vehicle.py -v ArduCopter -f gazebo-iris --model JSON -j 2 --console --map
```

Başlatıcının açık dosya yolu, yeni terminalde görülen `sim_vehicle.py: command not found` sorununu önler. `-j 2`, 4 GB RAM'li VM'de paralel derleme işini sınırlar; değişmeyen dosyalar yeniden derlenmez.

Normal yeniden başlatmada **`-w` ekleme**: sanal aracın kaydettiğimiz parametrelerini sıfırlar. İlk quad ve Iris kurulum denemelerinde kullanılmıştı.

Harita açılınca MAVProxy isteminde `status` ile araç verileri görülebilir. İlk kalkıştan önce konum kestiriminin hazır olmasını bekle. Kullanıcının çıktısında `EKF3 IMU1 is using GPS` ve simülasyon/konum verileri görüldü.

## Mission Planner bağlantısı

Windows'ta `ipconfig` ile **VMware Network Adapter VMnet8** IPv4 adresini bul. NAT ağ geçidini veya VM'nin kendi IP adresini bunun yerine kullanma. Makineye özgü adresi Git'e girmeyen `reports/paths.local.md` içine kaydet.

Çalışan MAVProxy isteminde aşağıdaki yer tutucuyu gerçek Windows adresiyle değiştir:

```text
output add WINDOWS_VMNET8_IPV4:14550
output list
```

Aynı hedef listede zaten varsa tekrar ekleme. Testte yerel `127.0.0.1:14550` çıkışına ek olarak Windows çıkışı görüldü. Bu ekleme çalışan MAVProxy oturumuna aittir; SITL yeniden başlatılınca gerekirse tekrar yapılır.

Windows Mission Planner'da bağlantı türünü **UDP**, dinleme portunu **14550** seç ve bağlan. Parametrelerin yüklenmesini, araç modu ve konumunun görünmesini bekle. Mission Planner'ın Simulation ekranından ikinci SITL başlatılmaz; bağlantı mevcut Gazebo aracınadır. [MAVProxy yönlendirme](https://ardupilot.org/mavproxy/docs/getting_started/forwarding.html).

| Bağlantı | Durum |
|---|---|
| Windows UDP 14550 | Mission Planner için doğrulandı |
| Ubuntu UDP 14560 | Gelecekteki uçuş node'u için planlandı; henüz eklenmedi/test edilmedi |
| Gazebo–SITL JSON | Eklentinin kendi sensör/motor bağlantısı; GCS portlarından ayrı |

## Uçuş denemesi

Aşağıdakiler **MAVProxy komutlarıdır**, Ubuntu shell komutları değildir. Satırları tek tek uygula:

```text
mode guided
arm throttle
takeoff 5
```

Guided modunu doğrula. Arm onayı geldikten sonra birkaç saniye içinde `takeoff 5` ver; arada sohbet yanıtı bekleme. Kalkış yapılmadan beklenirse araç otomatik disarm olabilir. Hedef yükseklikte kısa süre gözlemle, sonra:

```text
mode land
```

Yere inişi ve DISARMED durumunu bekle. Mission Planner'da da mod seçimi **Set Mode** ile uygulanır; yalnızca listede Guided seçili olması aracın Guided'a geçtiğini göstermez. [Resmî SITL uçuş akışı](https://ardupilot.org/dev/docs/copter-sitl-mavproxy-tutorial.html).

## Çözülen arm hataları

### `PreArm: Motors: Check frame class and type`

MAVProxy'den mevcut değerler okundu:

```text
param show FRAME_CLASS
param show FRAME_TYPE
```

Sonuç `0` ve `1` idi. Iris için resmî değerler `FRAME_CLASS=1`, `FRAME_TYPE=1`: Quad/X. Yalnızca yanlış sınıf düzeltildi:

```text
param set FRAME_CLASS 1
param show FRAME_CLASS
```

Değer doğrulandıktan sonra SITL Ctrl+C ile durduruldu ve **`-w` olmadan** yeniden başlatıldı. Yeniden okunan sınıf `1` idi. [Iris parametre dosyası](https://github.com/ArduPilot/ardupilot/blob/master/Tools/autotest/default_params/gazebo-iris.parm). FRAME_CLASS değişimi yeniden başlatma gerektirir.

### `Arm: Land mode not armable`

Mission Planner Messages sekmesinde doğrudan görüldü. Araç önceki inişten sonra LAND modunda kalmıştı. Actions bölümündeki Guided seçimine **Set Mode** ile geçildi; HUD Guided gösterdi. Normal Arm düğmesiyle ARMED görüldü. Bu doğrulamada Force Arm kullanılmadı ve arming kontrolleri topluca kapatılmadı.

Yeni bir ret olursa gerçek nedeni oku:

```text
watch STATUSTEXT
arm throttle
```

Canlı izlemeyi bitirmek için `watch` yaz. Son durum ve komut yanıtı ayrıca şöyle okunabilir:

```text
status STATUSTEXT
status COMMAND_ACK
```

`Taking off to 5.0 meters` satırı tek başına kalkış kanıtı değildir; araç disarmed ise hareket etmeyebilir. Drone'un hareketi ve telemetri birlikte gözlenir.

## Sürüm kaydı — tamamlandı

Mission Planner başlığında ArduCopter `V4.8.0-dev (5aa07216)` gözlendi. Kullanıcı, başarılı uçuşların ardından Ubuntu terminalinde aşağıdaki komutlarla tam kaynak kimliklerini paylaştı:

```bash
git -C ~/projects/drone_alignment_vendor/ardupilot rev-parse HEAD
git -C ~/projects/drone_alignment_vendor/ardupilot_gazebo rev-parse HEAD
```

| Kaynak deposu | Doğrulanan HEAD |
|---|---|
| ArduPilot | `5aa0721611bdd66ded2285873c091b5ef7ac69e7` |
| ardupilot_gazebo | `082a0fe231f6e63bc8d1598f1cba461d9e2ea7f5` |

Kimlikler [ortam raporuna](../reports/environment.md) da kaydedildi. Gün 2'nin kurulum, uçuş ve sürüm kaydı adımları tamamlandı. Bu çalışan kaynak sürümlerini bilinçli bir neden olmadan güncelleme. Gün 3'ün ilk işlevsel hedefi aşağı bakan kameradan ROS 2'ye görüntü aktarmaktır.
