define Device/honor_fur-602
  DEVICE_VENDOR := HONOR
  DEVICE_MODEL := FUR-602
  DEVICE_DTS := mt7981b-honor-fur-602
  DEVICE_DTS_DIR := ../dts
  SUPPORTED_DEVICES += honor,fur-602
  DEVICE_PACKAGES := kmod-mt_wifi kmod-conninfra kmod-warp mtwifi-cfg luci-app-mtwifi-cfg wifi-dats
  UBINIZE_OPTS := -E 5
  BLOCKSIZE := 128k
  PAGESIZE := 2048
  IMAGE_SIZE := 116736k
  KERNEL_IN_UBI := 1
  IMAGES += factory.bin
  IMAGE/factory.bin := append-ubi | check-size $$$$(IMAGE_SIZE)
  IMAGE/sysupgrade.bin := sysupgrade-tar | append-metadata
endef
TARGET_DEVICES += honor_fur-602

