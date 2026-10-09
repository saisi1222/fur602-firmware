# HONOR FUR-602 完整固件云编译（GitHub Actions）

基于 **padavanonly/immortalwrt-mt798x-6.6 @ `openwrt-24.10-6.6`** 编译包含以下特性的 FUR-602 固件：

- **闭源 mtwifi 驱动**（`kmod-mt_wifi`，与现固件一致，含 HNAT/WARP）
- **CPU 频率**：MT7981 硬件**不支持 DVFS**（联发科移除动态节能，定频 1.3GHz、电压不动态升降，无 OPP 节点），因此"CPU 降频"在 FUR-602 上**物理不可实现**；编译产物**不含** `cpufreq` / `luci-app-cpufreq`。需要温度/散热管理请改用 `pwm-fan`（现固件 DTS 已带，`status=disabled`，可按需开启）。
- **全锥形 NAT（nft fullcone）**：用户态补丁 padavanonly 已自带（libnftnl / nftables / firewall4）；内核模块 `kmod-nft-fullcone` 以**本地 vendor 包**形式放入 `package/kernel/nft-fullcone/`（上游仓库是单包目录、不能直接当 feed 用，故改为 vendor）
- **FUR-602 设备支持**：DTS + device 段来自 Yuzhii0718 fork，已把 `kmod-mt7915e` 改为 `kmod-mt_wifi`

> 设计依据（已在线核实）：padavanonly `feeds.conf.default` 只挂标准 feed，**不含**全锥；其 `nft.mk` 里没有 `kmod-nft-fullcone`（官方 immortalwrt 24.10 同样不含模块），所以必须靠外部 feed 补内核模块，而用户态补丁已在主源 `package/*/patches/` 就位。

## 目录结构

```
fur602-build/
├── .github/workflows/build-fur602.yml   # 完整固件编译 workflow
├── fur602-patches/
│   ├── dts/mt7981b-honor-fur-602.dts     # FUR-602 设备树（从路由器运行期 DTB 反编译，最贴近真实硬件；含闭源 mtwifi 的 wifi@18000000 节点）
│   ├── apply-device.py                   # 把设备定义注入 filogic.mk
│   └── fur602.config                     # .config 种子（target/device/功能开关）
├── kernel.config                         # 路由器现跑内核配置（参考/对照用）
└── README.md
```

## 一键推仓 + 触发编译

需要你的 GitHub PAT（scope 勾 `repo` + `workflow`）：

```bash
GH_PAT=ghp_xxx bash push-and-build.sh
```

脚本会：① 用 PAT 在你的账号下建公开库 `fur602-firmware`；② 推 `main`；③
推上去即触发 `Build FUR-602 firmware` workflow（也可在仓库 Actions 页手动 Run）。

## 产物

`bin/targets/mediatek/filogic/` 下的 `*-sysupgrade.bin` 与 `*-factory.bin`（约 1.5–2.5 小时构建）。

## 路由器侧刷写与验证

```sh
# 刷 sysupgrade（保留配置可加 -n 去掉以不保留）
sysupgrade -v openwrt-mediatek-filogic-honor_fur-602-squashfs-sysupgrade.bin

# 验证全锥
lsmod | grep nft_fullcone
uci set firewall.@defaults[0].fullcone='1'; uci commit firewall; fw4 reload
nft list ruleset | grep -i fullcone

# 验证 CPU 频率（MT7981 定频，无 scaling 可用；确认当前主频即可）
cat /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_cur_freq 2>/dev/null || grep -i bogo /proc/cpuinfo
```

## 注意

- 不要 `rmmod` 任何 fullcone 模块（`xt_FULLCONENAT` 的 rmmod 曾导致内核 panic 重启）。
- 闭源 mtwifi 与现固件同源同分支，驱动版本匹配，刷后 Wi-Fi 行为与现固件一致。
- 若构建报 `kmod-nft-fullcone` 依赖缺失，多半是 `NF_CONNTRACK_EVENTS` / `NF_CONNTRACK_CHAIN_EVENTS`
  未开；workflow 已强制 `-e` 这两项为 y。
