# Gün 1 — Mevcut ortamı doğrula

## Bugünkü hedef

Repo oluşturmak, Windows eğitim ortamında GPU ile gerçek işlem yapmak ve Ubuntu'daki Gazebo jitter sorununu daraltmak. ROS 2 veya Gazebo'yu yeniden kurmak bugünün adımı değildir.

## Nerede çalışıyoruz?

| İş | Yer |
|---|---|
| PyTorch/Ultralytics ve eğitim | Windows'ta ayrı Python 3.12 sanal ortamı |
| ROS 2, Gazebo, ileride SITL | Ubuntu 24.04 / VMware |
| Linux terminal komutları | Kullanıcı Ubuntu terminalinde çalıştırır |
| Kaynak ve belgeler | Bu Git reposu |

## Ubuntu'dan alınan bilgiler

- Gazebo: 8.15.0, Harmonic.
- Bellek: yaklaşık 3.8 GiB; paylaşılan çıktıda kullanılabilir bellek 2.5 GiB, swap kullanımı 0.
- Renderer: `SVGA3D; build: RELEASE; LLVM;`, OpenGL 4.3, Mesa 25.2.8.
- `glxinfo -B`: `Accelerated: no`, `Video memory: 1MB` bildiriyor.
- VMware yapılandırması: 4 vCPU, 4096 MiB RAM, 3B hızlandırma açık, NAT.
- Windows VMware renderer logu RTX 4060 üzerinde DX12 renderer başlattığını bildiriyor.

Bu bilgiler grafik katmanının araştırılmasını gerektiriyor. Guest çıktısındaki 1 MB değerini doğrudan fiziksel GPU belleği saymıyoruz; host loguyla birlikte değerlendiriyoruz. RAM eksikliği veya GPU'nun tamamen kullanılmadığı henüz kanıtlanmış değil.

## Windows eğitim ortamı — doğrulandı

Python 3.12.13, PyTorch 2.14.1+cu126, torchvision 0.29.1+cu126, Ultralytics 8.4.183 ve OpenCV 5.0.0 kuruldu. CUDA 12.6 çalışma zamanı, GPU üzerinde matris işlemi/backward ve 416 girişli YOLO11n mimarisinin forward adımı doğrulandı. Bu, eğitilmiş bir platform modelinin testi değildir; rastgele ağırlıklı mimariyle ortam denemesidir.

Kanıt: [GPU kontrolü](../reports/windows_gpu_check.json), [paket sürümleri](../reports/requirements_windows.txt).

Aynı ortamı yeni Windows repo kopyasında oluşturma sırası:

```powershell
uv python install 3.12
uv venv --python 3.12 .venv
uv pip install --python .venv\Scripts\python.exe torch==2.14.1 torchvision==0.29.1 --index-url https://download.pytorch.org/whl/cu126
uv pip install --python .venv\Scripts\python.exe -r reports/requirements_windows.txt
.\.venv\Scripts\python.exe -c "import torch; print(torch.__version__); print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0))"
```

Mevcut bilgisayarda ortam zaten oluşturuldu; bu komutları yeniden çalıştırmak gerekmiyor. Gerçek yerel ortam yolu Git'e girmeyen `reports/paths.local.md` dosyasında tutulur. Sistem Python 3.14 varsayılanı değiştirilmedi.

## Jitter'ı ayıran deneme

Önce açık Gazebo'yu normal biçimde kapat. Ubuntu terminalinde:

```bash
printenv XDG_SESSION_TYPE
gz sim -v 4 shapes.sdf
```

Bu açılışta `-r` yok: simülasyon başlangıçta duraklatılmış olmalı. Kamera sabitken ve kamerayı döndürürken titreme var mı kaydet. Sonra Play/Pause farkını gözle. Terminaldeki ilk renderer hatalarını sakla.

Basit ve duraklatılmış sahnede de sorun varsa fizik modelinden önce görüntü/UI katmanı incelenir. Tek değişkenli ikinci test için ilk pencereyi kapatıp:

```bash
gz sim -v 4 shapes.sdf --render-engine ogre
```

Bu deneme yalnızca renderer karşılaştırmasıdır; proje renderer'ının kalıcı seçimi değildir. Sonuçları görmeden başka ortam değişkeni veya sürücü değişikliği ekleme.

| Durum | Varsayılan renderer | Ogre renderer |
|---|---|---|
| Pause, kamera sabit | Henüz ölçülmedi | Henüz ölçülmedi |
| Pause, kamera hareketli | Henüz ölçülmedi | Henüz ölçülmedi |
| Play | Henüz ölçülmedi | Henüz ölçülmedi |

Kaynak: [Gazebo Harmonic troubleshooting](https://gazebosim.org/docs/harmonic/troubleshooting/).

## Bugünün kabul koşulları

- [ ] GitHub reposu oluşturuldu, yerel commit remote ile eşleşiyor.
- [x] Windows'ta CUDA destekli PyTorch ve Ultralytics import ediliyor.
- [x] GPU üzerinde matris işlemi ve backward adımı başarıyla yapıldı.
- [x] Paket sürümleri kaydedildi.
- [ ] Gazebo jitter'ının hangi koşulda oluştuğu tekrarlanabilir biçimde yazıldı.
- [ ] Sonraki kurulum adımı, teşhis sonucuna göre belirlendi.

Jitter doğrulanmadan ArduPilot, kamera ve kontrol katmanlarını aynı anda eklemeyeceğiz.
