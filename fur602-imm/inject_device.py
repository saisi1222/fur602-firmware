#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 HONOR FUR-602 设备支持注入 padavanonly/immortalwrt-mt798x-6.6 源码树。

用法: python3 inject_device.py <openwrt-source-root>

做三件事（均幂等）：
  1. 复制 mt7981b-honor-fur-602.dts 到 target/linux/mediatek/dts/
  2. 在 target/linux/mediatek/image/filogic.mk 的 'define Device/h3c_magic-nx30-pro' 前插入 FUR-602 设备块
  3. 在 filogic/base-files/etc/board.d/02_network 的 'jcg,q30-pro|\' 前插入 honor,fur-602 网口条目
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    root = os.path.abspath(root)

    # 1) DTS
    dts_dst = os.path.join(root, "target/linux/mediatek/dts/mt7981b-honor-fur-602.dts")
    shutil.copy(os.path.join(HERE, "mt7981b-honor-fur-602.dts"), dts_dst)
    print("[ok] DTS ->", dts_dst)

    # 2) device profile
    mk = os.path.join(root, "target/linux/mediatek/image/filogic.mk")
    text = open(mk, encoding="utf-8").read()
    if "define Device/honor_fur-602" in text:
        print("[skip] device block already present")
    else:
        block = open(os.path.join(HERE, "device-fur602.mk"), encoding="utf-8").read()
        marker = "define Device/h3c_magic-nx30-pro"
        if marker not in text:
            raise SystemExit("FATAL: marker %r not found in filogic.mk" % marker)
        text = text.replace(marker, block + "\n" + marker, 1)
        open(mk, "w", encoding="utf-8").write(text)
        print("[ok] device block injected into filogic.mk")

    # 3) 02_network
    net = os.path.join(root, "target/linux/mediatek/filogic/base-files/etc/board.d/02_network")
    n = open(net, encoding="utf-8").read()
    if "honor,fur-602" in n:
        print("[skip] network entry already present")
    else:
        marker = "jcg,q30-pro|\\"
        if marker not in n:
            raise SystemExit("FATAL: marker %r not found in 02_network" % marker)
        n = n.replace(marker, "\thonor,fur-602|\\\n" + marker, 1)
        open(net, "w", encoding="utf-8").write(n)
        print("[ok] honor,fur-602 injected into 02_network")


if __name__ == "__main__":
    main()
