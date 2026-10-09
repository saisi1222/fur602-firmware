# 给 HONOR FUR-602 编译 nft_fullcone.ko（GitHub Actions 云编译）

路由器：ImmortalWrt 24.10-SNAPSHOT（第三方 padavanonly 分支），内核 **6.6.133**，aarch64。
目标：编译出与该内核 ABI 一致的 `nft_fullcone.ko`，装上后开启 fw4 原生全锥 NAT（`fullcone='1'`），不刷机、不写脚本。

## 为什么必须这样编

直接装官方 24.10.6 的 `kmod-nft-fullcone` 会失败：

```
module nft_fullcone: .gnu.linkonce.this_module section size must match
the kernel's built struct module size at run time
```

vermagic 一样（都是 `6.6.133 SMP mod_unload aarch64`）但 `struct module` 布局不同 ——
因为**内核 .config 不同**。解决办法：把路由器上正在跑的那份真实内核配置
（`/proc/config.gz`，已导出为 `kernel.config`）覆盖编译时的 target kernel config，
这样编出来的模块 ABI 与运行内核一致。

## 用法

```bash
git init fur602-fullcone && cd fur602-fullcone
# 放入 kernel.config 和 .github/workflows/build-nft-fullcone.yml
git add -A && git commit -m "build nft_fullcone for FUR-602 6.6.133"
gh repo create fur602-fullcone --public --source=. --push      # 或用网页建库后 push
# 然后：仓库页面 → Actions → "Build nft_fullcone.ko..." → Run workflow
```

跑完约 60~120 分钟（工具链 + 内核）。产物在 Artifacts：`nft_fullcone-6.6.133`
（含 `nft_fullcone.ko` 和 `kmod-nft-fullcone_*.ipk`）。

## 装到路由器

```sh
# 1) 先试加载（干净失败也不会崩，最坏是 insmod 报错）
insmod /tmp/nft_fullcone.ko && echo "LOAD OK"
lsmod | grep fullcone
dmesg | tail -5

# 2) 确认 OK 再固化
cp /tmp/nft_fullcone.ko /lib/modules/6.6.133/
echo nft_fullcone > /etc/modules.d/nft-fullcone
uci set firewall.@defaults[0].fullcone='1'
uci commit firewall
fw4 reload

# 3) 验证
nft list ruleset | grep -i fullcone
```

注意：**别对任何 fullcone 相关模块执行 rmmod**（`xt_FULLCONENAT` 的 rmmod 曾导致内核 panic 重启）。
若 `insmod` 仍报 struct module size 不匹配，说明 config 仍未对齐，直接放弃，不要强加载。
