# Kylin SWE 沙箱说明

## 镜像与容器

| 项 | 值 |
|---|---|
| 镜像 | `kylin-swe-sandbox:v2` |
| 架构 | aarch64 |

## 服务与端口

| 服务 | 地址 | 说明 |
|---|---|---|
| code-server | `http://localhost:9000` | 免认证，工作区 `/home/ai-user/dataset` |
| sandbox server | `http://localhost:8080` | uvicorn `/home/ai-user/verl/recipe.dev_agent.sandbox.sandbox_server:app` |
| VNC | `localhost:5900` | 密码 `kimi-sandbox`，1920×1080 openbox |

code-server 和 sandbox server 由 `/entrypoint.sh` 自启；**VNC 需手动启动**。

## 启动 VNC + 图形化 code-server

```bash
docker exec 1014arm-sandbox vncserver :0 -geometry 1920x1080 -depth 24 -localhost no
docker cp playwright-test/test0.py 1014arm-sandbox:/home/ai-user/
docker exec 1014arm-sandbox sh -c 'cd /home/ai-user && DISPLAY=:0 XAUTHORITY=/home/ai-user/.Xauthority \
  nohup /home/ai-user/runtime-venv/bin/python3 /home/ai-user/test0.py > /tmp/test0.log 2>&1 &'
```

test0.py 会在 VNC 桌面打开 Chrome 并加载 code-server（5 分钟后自动关闭，改 `time.sleep(300)` 可延长）。

如果想要修改 DevAgent 的配置，先在容器内启动 VNC 服务，然后在物理机上通过 VNC 软件连接容器的 5900 端口，接着在容器内运行 test0.py，它启动的 Chrome 浏览器窗口会显示在 VNC 桌面中并自动打开 code-server 界面（http://localhost:9000），即可在界面里修改 DevAgent 插件的配置；需要注意的是，test0.py 默认 5 分钟后自动关闭浏览器，若修改时间较长需先调大脚本中的 sleep 时长。或者在playwright-test/auto-modify-configurations.py里面填好需要修改的配置（如后端代理地址），然后运行改脚本即可。

## 关键路径（容器内）

| 路径 | 内容 | 权限 |
|---|---|---|
| `/repos` | 20 个训练仓库（带 `.git`） | ai-user，777 |
| `/opt/envs` | 37 个固化环境 | - |
| `/home/ai-user/solidify-worklist.json` | 环境规格清单 | - |
| `/home/ai-user/verl` | 训练框架 + sandbox server 代码 | ai-user |
| `/usr/chrome-persistent-data` | Chrome 持久化数据 | ai-user，777 |
| `/data/configs` | ❌ 不存在（可选，缺失时回落 worklist 的 version_patterns） | - |

