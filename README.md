# WorldOS · 万界纵横

[English](#english) · [中文](#中文)

## English

The code currently available in this repository is for the WorldOS project progress site.

Project progress: [English site](https://hymxo.github.io/worldos/)

WorldOS is a research project on interactive narrative and virtual world modeling. Set in Tang-dynasty Chang’an, the first prototype explores how AI characters remember events and how player choices shape the story that follows.

The first MVP has been built and is undergoing internal testing. We will publish the full MVP source code in this repository as soon as possible.

### Current Release

The repository contains the project site, a prebuilt frontend, and the Python backend source code for reading and updating milestones.

- `serve.py` serves the static pages and the progress API.
- `current/standalone/progress_server.py` reads and writes milestones and progress records.
- `current/standalone-dist/` contains the prebuilt frontend, ready to serve. The archive includes the entry point `current/standalone/main.tsx`. Rebuilding the frontend requires the page source files and build configuration.

### Run Locally

This example uses PowerShell and Python 3. On Linux or macOS, set the same environment variables with `export`, then start the server with `python3 serve.py`.

```powershell
$env:WANJIE_HOST = '127.0.0.1'
$env:WANJIE_PORT = '58001'
$env:WANJIE_ADMIN_USERNAME = 'admin'
$env:WANJIE_ADMIN_PASSWORD = '<choose a local admin password>'
python serve.py
```

Open <http://127.0.0.1:58001/> to view the site and <http://127.0.0.1:58001/admin> to manage progress. The server creates the local `data/progress.json` file when you first save changes.

## 中文

当前开源的是项目进度展示网站。

项目进度：[中文展示站](https://hymxo.github.io/worldos/zh/)

万界纵横是一个交互叙事与虚拟世界建模研究项目，以唐代长安为首个原型场景，探索 AI 角色的事件记忆和玩家选择对后续剧情的影响。

第一个MVP原型已经开发出来，目前还在紧张内测，我们会尽快在这里公布MVP全套源码。

### 当前版本

仓库提供项目展示站、预构建前端，以及用于读取和更新里程碑的 Python 后端源码。

- `serve.py` 提供静态页面和进度接口。
- `current/standalone/progress_server.py` 实现里程碑和进度记录的读写。
- `current/standalone-dist/` 是可直接运行的前端构建产物。归档提供了入口文件 `current/standalone/main.tsx`，缺少它引用的前端页面源码与构建配置。

### 在本机运行

以下示例使用 PowerShell 和 Python 3。在 Linux 或 macOS 中，可以用 `export` 设置相同的环境变量，再用 `python3 serve.py` 启动。

```powershell
$env:WANJIE_HOST = '127.0.0.1'
$env:WANJIE_PORT = '58001'
$env:WANJIE_ADMIN_USERNAME = 'admin'
$env:WANJIE_ADMIN_PASSWORD = '<自行设置本地管理密码>'
python serve.py
```

访问 <http://127.0.0.1:58001/> 查看站点，访问 <http://127.0.0.1:58001/admin> 管理进度。首次保存时，服务会创建本地的 `data/progress.json`。
