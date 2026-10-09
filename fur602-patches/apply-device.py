#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将 HONOR FUR-602 设备定义注入 padavanonly 的 filogic.mk。
- 闭源 mtwifi 驱动：DEVICE_PACKAGES 用 kmod-mt_wifi（保留与现固件一致的特性）
- DTS 文件请另行复制到 target/linux/mediatek/dts/mt7981b-honor-fur-602.dts
用法: python3 apply-device.py <path-to-filogic.mk>
"""
import sys
import os

BLOCK = '''define Device/honor_fur-602
  DEVICE_VENDOR := HONOR
  DEVICE_MODEL := A10
  DEVICE_DTS := mt7981b-honor-fur-602
  DEVICE_DTS_DIR := ../dts
  SUPPORTED_DEVICES += mediatek,mt7981-spim-snand-rfb
  DEVICE_PACKAGES := kmod-mt_wifi kmod-mt7981-firmware mt7981-wo-firmware
  UBINIZE_OPTS := -E 5
  BLOCKSIZE := 128k
  PAGESIZE := 2048
  IMAGE_SIZE := 116736k
  KERNEL_IN_UBI := 1
  IMAGES += factory.bin
  IMAGE/factory.bin := append-ubi | check-size $$$$(IMAGE_SIZE)
  IMAGE/sysupgrade.bin := sysupgrade-tar | append-metadata
  KERNEL = kernel-bin | lzma | \\
	fit lzma $$(KDIR)/image-$$(firstword $$(DEVICE_DTS)).dtb
  KERNEL_INITRAMFS = kernel-bin | lzma | \\
	fit lzma $$(KDIR)/image-$$(firstword $$(DEVICE_DTS)).dtb with-initrd
endef
TARGET_DEVICES += honor_fur-602

'''

ANCHOR = "define Device/huasifei_wh3000-pro"


def main():
    if len(sys.argv) < 2:
        print("usage: apply-device.py <filogic.mk>")
        sys.exit(1)
    path = sys.argv[1]
    if not os.path.isfile(path):
        print("ERROR: file not found:", path)
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # 已注入则跳过
    if any("honor_fur-602" in ln for ln in lines):
        print("FUR-602 已存在于 filogic.mk，跳过注入。")
        return

    out = []
    inserted = False
    for ln in lines:
        if not inserted and ln.strip() == ANCHOR:
            out.append(BLOCK)
            inserted = True
        out.append(ln)
    if not inserted:
        # 兜底：直接追加到末尾
        out.append("\n")
        out.append(BLOCK)

    with open(path, "w", encoding="utf-8") as f:
        f.writelines(out)
    print("已注入 FUR-602 设备定义到", path)


if __name__ == "__main__":
    main()
