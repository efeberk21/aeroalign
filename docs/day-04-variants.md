# Gün 4 — Sahne çeşitleri ve otomatik çekim

Bu belge Gün 4'ün kalan işlerini kapatır: ikinci platform görünümü, zemin/ışık çeşitleri, platform olmayan dikkat dağıtıcılar ve gerçek simülasyon negatifleri.

## Modeller

| Model | Varyant adı | Not |
|---|---|---|
| `delivery_platform` | `orange_h_v1` | Mevcut: koyu çerçeve, turuncu yüzey, beyaz H |
| `delivery_platform_blue` | `blue_ring_v1` | Aynı 2 × 2 m gövde; mavi yüzey, beyaz halka ve merkez nokta |
| `distractor_crate` | — | 1,2 × 0,8 × 0,6 m kahverengi sandık |
| `distractor_dark_mat` | — | 2 × 2 m düz koyu paspas; platformla aynı ayak izi, zor negatif |
| `distractor_hazard_stripes` | — | 3 × 1 m sarı/siyah şerit deseni |
| `distractor_orange_barrel` | — | Turuncu varil, beyaz bant; renk karıştırıcı |

Platform boyutu her iki görünümde de 2 × 2 m'dir. Etiket sınırı değişmez: koyu çerçeve dahil dış fiziksel sınır.

Bütün yeni modeller her dünyada **park yerinde** durur: `y = 40 m`, kameranın en geniş görüşünün (10 m'de yaklaşık ±15,6 m) çok dışında. Uçuşlu akışta drone'un gördüğü sahne eskisiyle aynıdır; bir nesneyi kadraja almak için:

```bash
gz service -s /world/iris_runway/set_pose --reqtype gz.msgs.Pose --reptype gz.msgs.Boolean \
  --timeout 2000 --req 'name: "distractor_crate", position: {x: 4, y: 2, z: 0}'
```

## Dünyalar

Zemin ve ışık değerleri [`sim/worlds/scene_variants.json`](../sim/worlds/scene_variants.json) içindedir. `scripts/make_scene_worlds.py` bu dosyadan, temel `platform_world.sdf`'i kopyalayarak 11 dünya üretir. Temel dünya gri zemin + varsayılan güneştir; toplam 4 zemin × 3 ışık = 12 dünya.

| Anahtar | Varyant adı | Değer |
|---|---|---|
| `gray` | `matte_gray_v1` | 0.38 0.40 0.39 |
| `sand` | `sand_v1` | 0.76 0.66 0.48 |
| `asphalt` | `asphalt_dark_v1` | 0.12 0.12 0.13 |
| `grass` | `grass_v1` | 0.24 0.40 0.18 |
| `default` | `sun_default_v1` | Mevcut güneş; ortam ışığı 1.0 |
| `low` | `sun_low_v1` | Alçak, sıcak renkli güneş; uzun gölge |
| `dim` | `overcast_dim_v1` | Loş, gölgesiz |

Dünya adı her dosyada `iris_runway`, drone `iris_with_gimbal` olarak kalır; köprü değişmez. Uçuşlu çalışmada:

```bash
ALIGN_WORLD=platform_world_sand_low bash ~/projects/aeroalign/scripts/start_sim.sh
```

Bir değeri değiştirmek için JSON'u düzenleyip `python3 scripts/make_scene_worlds.py` çalıştır; üretilen `.sdf` dosyalarını elle düzenleme. Bilinen not: `default` ışık kum ve çim zeminde oldukça parlak, kum neredeyse açık sarı görünür. Bu bir koşul olarak bırakıldı.

## Otomatik çekim

`scene_capture.py` drone uçurmadan veri toplar:

1. Dünyayı drone olmadan ayrı bir `GZ_PARTITION` içinde başsız açar. Çalışan bir uçuş simülasyonunu etkilemez.
2. Iris gimbal kamerasıyla aynı görüntü ayarlarına (640 × 480, yatay görüş 2,0 rad) sahip, aşağı bakan, yerçekimsiz bir kamera ekler.
3. Her kare için kamera konumu/yaw, platform konumu/yaw ve 0–3 dikkat dağıtıcıyı tek `set_pose_vector` çağrısıyla dizer; birkaç kare bekleyip görüntüyü alır.
4. PNG ve `manifest.csv` satırını kaydedicinin `write_record` işleviyle yazar. Sütunlar aynıdır.

Kullanım (Gazebo/SITL açık olması gerekmez):

```bash
source /opt/ros/jazzy/setup.bash
cd ~/projects/aeroalign
source .venv/bin/activate

python ros_ws/src/drone_alignment/drone_alignment/scene_capture.py \
  --world platform_world_grass_low --scene-id scene05 --platform blue --seed 5
```

Varsayılanlar: yükseklikler 5, 8, 10 m; her yükseklikte 12 pozitif + 3 negatif (veri planındaki bütçe). Her yükseklik ayrı bir oturumdur (`rig_h05_...`). Aynı `--seed` aynı yerleşimi üretir.

Manifestte:

- `platform_variant=none` → negatif kare.
- `nominal_height_m` → kameranın zeminden yüksekliği. Bu çekimde tam bilinir; uçuş telemetrisi değildir.
- `camera_profile=rig_nadir_640x480_hfov2` → uçuş kamerasından (`iris_wide_640x480_hfov2_zoom1`) ayırt etmek için.

Ayrıca her oturumda `capture_poses.csv` bulunur: kamera ve platform konumu/yaw, kadraja alınan dikkat dağıtıcılar. Gün 6'da etiket kutularını bu pozlardan hesaplamak mümkündür; bu henüz yapılmadı ve doğrulanmadı.

Yerleşim kuralları:

- Pozitiflerin yaklaşık %85'inde platform tamamen kadrajdadır. Kalanında platform merkezi görüntü içinde kalır ama kenardan taşabilir (kısmi/zor örnek).
- Dikkat dağıtıcılar platformla ve birbiriyle çakışmaz.
- Negatiflerde platform park yerindedir. Oturum başına en fazla bir negatif tamamen boş zemindir, çünkü düz renkli zeminde boş kareler pikseli pikseline aynıdır.

## Sınırlar

- Kamera tam aşağı bakar ve sallanmaz. Uçuşta gimbal küçük eğimler, drone parçaları ve hareket bulanıklığı içerebilir. Uçuşla alınan 141 görüntülük pilot bu farkı görmek için saklanır. Uçuş görüntüleri test kümesinde ayrıca değerlendirilmelidir.
- Zeminler düz renktir, doku yoktur.
