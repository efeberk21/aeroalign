# Gun 4 - Hazir platform sahnesi

Platform: 2 x 2 metre, 12 cm kalinliginda koyu govde, turuncu yuzey ve merkezde beyaz H. Isaret iki eksene gore simetriktir. Platformun merkezi baslangicta dunya koordinatlarinda `(1, 0, 0)` metredir; drone'un kalkis noktasinin uzerinde degildir.

## Gazebo'yu baslat

Ubuntu'da bir terminalde:

```bash
bash ~/projects/aeroalign/scripts/start_sim.sh
```

Betik ROS Jazzy'yi yukler, model/eklenti yollarini o terminal icin ayarlar ve hem GUI hem sensorler icin Ogre kullanan proje dunyasini acar. Baska klasorden veya yeni terminalden de calisir. Ayni dunyanin ikinci kopyasini acmadan once mevcut Gazebo oturumunu kapat.

Vendor depo farkli yerdeyse:

```bash
ALIGN_GZ_ROOT=/tam/yol/ardupilot_gazebo bash ~/projects/aeroalign/scripts/start_sim.sh
```

## SITL ve kamera

SITL ayri terminalde [Gun 2'deki komutla](day-02.md#terminal-2-ardupilot-sitl) baslatilir. Gazebo betigi SITL, kalkis, kamera koprusu veya viewer baslatmaz. Bu islemler aciksa ikinci kopyalarini acma.

Dunya adi `iris_runway` ve drone adi `iris_with_gimbal` korundu; mevcut `configs/bridge.yaml` ve `camera_viewer` ayni topic'lerle calisir. Gimbal icin oturumda dogrulanan ayarlar `MNT1_TYPE=1` ve `SERVO10_FUNCTION=7` idi. Kamera yonunu Mission Planner'da Point Down ile ayarla.

## Veri icin goruntu

- Kamera goruntulerini `/camera/image_raw` topic'inden al. Gazebo editorunun ekran goruntusu veri kumesi goruntusu degildir.
- Editor izgarasi ve secim tutamaklari GUI katmanidir. Dunyanin gorunen renkli eksen geometrileri kaldirildi; mevcut sabit NavSat sensoru korundu.
- Zemin proje icinde tanimlanan mat gri duzlemdir; platform modeli doku, mesh veya internetten indirilen kaynak gerektirmez.
- Etiketlenecek sinir, H isareti degil platformun koyu cercevesini de iceren fiziksel dis sinirdir. Ayrintilar [veri kartinda](../reports/dataset_card.md).

Bu teslim ilk platform/sahne modelidir. Diger varyantlar, `dataset_recorder`, pilot kayit ve ucus kabul deneyleri ayri adimlardir.
