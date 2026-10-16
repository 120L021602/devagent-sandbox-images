# kylin-swe-sandbox:v2 镜像恢复指南

镜像 `kylin-swe-sandbox:v2`（aarch64 架构，`docker save` 导出，gzip 压缩）因 GitHub 单文件 2GB 限制，切分为 **7 个分块**存放在本仓库的 Release 中。

- Release：`kylin-swe-sandbox-v2`
- 合并后文件：`kylin-swe-sandbox-v2.tar.gz`（13,623,292,188 字节 ≈ 12.7 GiB）
- 分块清单：`kylin-swe-sandbox-v2.tar.gz.part-00` ~ `part-06`
- 校验清单：`sha256sums.txt`（含每个分块和合并后整包的 SHA256）

> ⚠️ 镜像是 **aarch64/ARM64** 架构，只能在 ARM 主机（如 Apple Silicon、ARM 服务器）或配置了 QEMU/Rosetta 跨架构支持的环境运行；x86_64 机器可以 `docker load` 但无法直接运行容器。

---

## 1. 下载全部分块

仓库是私有的，下载需要 GitHub 身份认证。

### 方式 A：浏览器（最简单）

登录 GitHub 后打开：

```
https://github.com/120L021602/devagent-sandbox-images/releases/tag/kylin-swe-sandbox-v2
```

下载全部 7 个 `part-*` 文件和 `sha256sums.txt`，放到同一目录。

### 方式 B：gh CLI

```bash
gh release download kylin-swe-sandbox-v2 \
  --repo 120L021602/devagent-sandbox-images \
  --pattern "kylin-swe-sandbox-v2.tar.gz.part-*" \
  --pattern "sha256sums.txt" \
  --dir ./images
```

### 方式 C：curl + Personal Access Token

```bash
TOKEN=<你的PAT>   # 需要 repo 权限
REPO=120L021602/devagent-sandbox-images
for i in 00 01 02 03 04 05 06; do
  NAME="kylin-swe-sandbox-v2.tar.gz.part-$i"
  ASSET_ID=$(curl -sf -H "Authorization: Bearer $TOKEN" \
    "https://api.github.com/repos/$REPO/releases/tags/kylin-swe-sandbox-v2" \
    | python -c "import json,sys; print([a['id'] for a in json.load(sys.stdin)['assets'] if a['name']=='$NAME'][0])")
  curl -fL -H "Authorization: Bearer $TOKEN" -H "Accept: application/octet-stream" \
    -o "$NAME" "https://api.github.com/repos/$REPO/releases/assets/$ASSET_ID"
done
# 同样方法下载 sha256sums.txt
```

## 2. 合并分块

### Linux / macOS / Git Bash

```bash
cat kylin-swe-sandbox-v2.tar.gz.part-* > kylin-swe-sandbox-v2.tar.gz
```

### Windows PowerShell / CMD

```powershell
cmd /c copy /b kylin-swe-sandbox-v2.tar.gz.part-00+kylin-swe-sandbox-v2.tar.gz.part-01+kylin-swe-sandbox-v2.tar.gz.part-02+kylin-swe-sandbox-v2.tar.gz.part-03+kylin-swe-sandbox-v2.tar.gz.part-04+kylin-swe-sandbox-v2.tar.gz.part-05+kylin-swe-sandbox-v2.tar.gz.part-06 kylin-swe-sandbox-v2.tar.gz
```

> 合并后整包大小必须是 **13,623,292,188** 字节，不对则说明分块缺失或损坏。

## 3. 校验完整性

```bash
# Linux / macOS / Git Bash
sha256sum -c sha256sums.txt
```

合并后整包的 SHA256 应为：

```
a8039c6f5e3cb83191bea106e956352e1d64840bd0e6ee5d67a28fb2f19e54f6  kylin-swe-sandbox-v2.tar.gz
```

Windows 无 sha256sum 时可用：

```powershell
certutil -hashfile kylin-swe-sandbox-v2.tar.gz SHA256
```

## 4. 导入镜像

```bash
docker load -i kylin-swe-sandbox-v2.tar.gz
```

导入成功后验证：

```bash
docker image inspect kylin-swe-sandbox:v2 --format '{{.Id}} {{.Architecture}}'
# 期望输出：sha256:6b7d775eb6d2... aarch64
```

之后即可按 `SANDBOX.md` 的说明启动容器（code-server `:9000`、sandbox server `:8080`、VNC `:5900`）。

---

## 常见问题

| 问题 | 处理 |
|---|---|
| 某个分块下载中断/损坏 | 用 `sha256sum -c sha256sums.txt` 定位坏块，只需重下该分块 |
| 合并后大小不一致 | 检查是否漏下分块；`copy /b` 的 `+` 顺序必须与 part 编号一致 |
| x86 机器 `docker load` 后无法运行 | 镜像为 aarch64，需 `docker run --platform linux/arm64` 且主机已装 QEMU binfmt（仍会很慢），建议直接在 ARM 机器使用 |
| Release 下载返回 404 | 私有仓库需先登录 / 使用带 repo 权限的 token |
