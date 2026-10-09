#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 HONOR FUR-602 设备支持注入 padavanonly/immortalwrt-mt798x-6.6 源码树。

用法: python3 inject_device.py <openwrt-source-root>

三步（均幂等、多锚点 + 兜底，打 MTK 补丁后仍可用）：
  1. 复制 mt7981b-honor-fur-602.dts 到 target/linux/mediatek/dts/
  2. 在 target/linux/mediatek/image/filogic.mk 注入 FUR-602 设备块
  3. 在 filogic/base-files/etc/board.d/02_network 注入 honor,fur-602 网口条目
     （lan1 lan2 lan3 + wan，与 jcg,q30-pro 同组）
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def inject_dts(root):
    dst = os.path.join(root, "target/linux/mediatek/dts/mt7981b-honor-fur-602.dts")
    shutil.copy(os.path.join(HERE, "mt7981b-honor-fur-602.dts"), dst)
    print("[ok] DTS ->", dst)


def inject_device(root):
    mk = os.path.join(root, "target/linux/mediatek/image/filogic.mk")
    text = open(mk, encoding="utf-8").read()
    if "define Device/honor_fur-602" in text:
        print("[skip] device block already present")
        return
    block = open(os.path.join(HERE, "device-fur602.mk"), encoding="utf-8").read().rstrip() + "\n"
    for marker in [
        "define Device/h3c_magic-nx30-pro",
        "define Device/cetron_ct3003",
        "define Device/jcg_q30",
        "define Device/xiaomi_mi-router-ax3000t",
    ]:
        if marker in text:
            text = text.replace(marker, block + "\n" + marker, 1)
            open(mk, "w", encoding="utf-8").write(text)
            print("[ok] device block injected before:", marker)
            return
    # 兜底：追加到文件末尾（define + TARGET_DEVICES 同处，make 解析无顺序问题）
    text = text.rstrip() + "\n\n" + block
    open(mk, "w", encoding="utf-8").write(text)
    print("[ok] device block appended to end of filogic.mk")


def inject_network(root):
    net = os.path.join(root, "target/linux/mediatek/filogic/base-files/etc/board.d/02_network")
    n = open(net, encoding="utf-8").read()
    if "honor,fur-602" in n:
        print("[skip] network entry already present")
        return
    for anchor in ["\tjcg,q30-pro|\\\n", "\tcetron,ct3003|\\\n", "\tqihoo,360t7|\\\n"]:
        if anchor in n:
            n = n.replace(anchor, "\thonor,fur-602|\\\n" + anchor, 1)
            open(net, "w", encoding="utf-8").write(n)
            print("[ok] network entry injected before:", anchor.strip())
            return
    # 兜底：在 case "$(board_name)" in 后插入独立分支
    marker = 'case "$(board_name)" in\n'
    if marker in n:
        branch = '\thonor,fur-602)\n\t\tucidef_set_interfaces_lan_wan "lan1 lan2 lan3" wan\n\t\t;;\n'
        n = n.replace(marker, marker + branch, 1)
        open(net, "w", encoding="utf-8").write(n)
        print("[ok] network entry injected as standalone case branch")
        return
    print("[warn] 02_network: no anchor found, network mapping NOT injected")


def main():
    root = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
    inject_dts(root)
    inject_device(root)
    inject_network(root)


if __name__ == "__main__":
    main()
