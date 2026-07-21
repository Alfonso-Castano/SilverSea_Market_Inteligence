# Silversea 市场情报系统 — 部署文档（中文）

## 目录

- [系统概述](#系统概述)
- [环境要求](#环境要求)
- [快速开始：仅查看仪表盘](#快速开始仅查看仪表盘)
- [运行完整流水线](#运行完整流水线)
- [生产环境部署](#生产环境部署)
- [环境变量参考](#环境变量参考)
- [故障排除](#故障排除)
- [项目结构](#项目结构)

---

## 系统概述

Silversea 市场情报系统是一个有状态的 AI 市场情报平台，为 Silversea Media 的业务拓展/销售团队构建。它抓取三个国家（新加坡、越南、马来西亚）的行业和业务领域标记的信息源，通过多轮 LLM 流水线进行过滤和综合分析，并将结果以每日内部 Web 仪表盘的形式呈现，同时包含反馈闭环机制，可量化地影响未来报告。

**技术栈：** Python 3.12.3、Flask + Jinja2、Tailwind CSS（CDN，无构建步骤）、Groq API（Llama 4 Scout 17B）、ChromaDB（通过 `sentence-transformers` 嵌入）、Scrapling + Playwright（动态网页抓取）。

**认证方式：** 两个共享密码（查看者、管理员），非个人用户账户体系。

---

## 环境要求

| 组件 | 版本/说明 |
|------|----------|
| 操作系统 | **Ubuntu 24.04 LTS**（本文档以此为目标系统；macOS / Windows 也可运行） |
| Python | **3.12.3**（精确版本，见 `.python-version`，最低 3.11+） |
| pip | 最新版本（随 Python 3.12.3 附带） |
| 网络 | 出站 HTTPS 访问（抓取信息源 + Groq API 调用） |
| 磁盘空间 | ~2 GB（Python 包 + ChromaDB + Playwright 浏览器） |

> **Ubuntu 24.04 用户注意：** Ubuntu 24.04 默认 `python3` 即为 **3.12.3**，与项目要求的版本完全一致，无需额外安装 Python。

### 安装系统依赖（Ubuntu 24.04）

在开始之前，先安装必需的 Ubuntu 系统包：

```bash
sudo apt update
sudo apt install -y python3.12-venv python3-pip python3-dev
```

| 包名 | 用途 |
|------|------|
| `python3.12-venv` | 创建 Python 虚拟环境（Ubuntu 24.04 需指定版本号） |
| `python3-pip` | Python 包管理器 |
| `python3-dev` | Python C 扩展编译头文件（`chromadb` 依赖需要） |
| `nginx` | 生产环境反向代理（仅仪表盘模式可跳过） |
| `git` | 克隆仓库 |

---

## 快速开始：仅查看仪表盘

此模式**不需要任何 API 密钥**，直接读取仓库中已提交的预生成报告数据。

### 1. 克隆仓库

```bash
git clone https://git.silversea-media.net/silversea-media/marketintelligent/ai-mi.git
cd ai-mi
```

### 2. 创建虚拟环境并安装依赖

```bash
python3 -m venv im-env
source im-env/bin/activate          # Windows: im-env\Scripts\activate
pip install -r requirements.txt
```

### 3. 配置环境变量（可选）

```bash
cp .env.example .env
```

**仪表盘模式无需填写任何 `.env` 值** — 将所有内容留空即可正常运行。

### 4. 启动仪表盘

```bash
python3 app.py
```

打开浏览器访问 **http://localhost:5000**。

### 5. 登录

首次访问会被重定向到登录页面，使用默认密码 **`Silversea`** 登录。

- 这是内置的共享默认密码，无需 `.env` 配置。
- 如果管理员通过 `/admin` 页面修改了密码，或 `VIEWER_PASSWORD` 环境变量已设置，请使用对应的值。

---

## 运行完整流水线

完整流水线会抓取真实信息源，进行实际的 LLM 调用，并覆盖 `data/latest_report_{COUNTRY}_{DOMAIN}.json` 文件。

### 前提条件

完成上述「快速开始」中的所有步骤后，继续以下操作：

### 1. 安装 Scrapling 浏览器二进制文件

```bash
scrapling install
```

> ⚠️ **这是一个容易遗漏的步骤。** `pip install` 仅安装 Scrapling 和 Playwright 的 Python 包，但某些信息源绕过反爬虫页面或渲染 JS 密集型网站所需的实际浏览器二进制文件需要通过 `scrapling install` 单独下载。跳过此步骤，流水线首次处理标记为 `"fetcher": "stealth"` 或 `"fetcher": "dynamic"` 的信息源时会报错：`Executable doesn't exist at ...\chrome-win64\chrome.exe`。

### 2. 设置 Groq API 密钥

在 `.env` 文件中设置 `GROQ_API_KEY`：

```bash
GROQ_API_KEY=gsk_your_actual_key_here
```

在 [console.groq.com](https://console.groq.com) 免费注册 — 免费套餐无需支付信息。

### 3. 运行流水线

**按国家和业务领域范围运行：**

```bash
python3 main.py --country=SG --domain=BER --no-email
```

**参数说明：**

| 参数 | 说明 | 可选值 |
|------|------|--------|
| `--country` | 运行哪个国家的信息源列表 | `SG`（新加坡）、`VN`（越南）、`MY`（马来西亚） |
| `--domain` | 该国信息源中哪个业务领域的子集 | `BER`（建筑环境）、`GENERAL`、`EDU`、`RCC`、`HLS`、`MFG`、`CTE`、`PSS` |
| `--no-email` | 跳过邮件摘要发送步骤 | 推荐使用，除非已配置 `GMAIL_*` 变量 |

> ⚠️ **注意配额：** Groq 免费套餐每天限额 100,000 tokens。单次范围运行的消耗约为 15,000-30,000 tokens。请勿循环遍历所有组合。

省略 `--country`/`--domain` 参数将运行所有活跃组合 — 这会非常慢且消耗大量配额，不建议仅用于测试目的。

### 4. 查看结果

输出覆盖 `data/latest_report_{COUNTRY}_{DOMAIN}.json`，仪表盘每次请求时都会重新读取 — **无需重启**即可看到新结果。

---

## 生产环境部署（Ubuntu 24.04）

以下为生产环境部署的推荐方案。开发服务器 (`app.py` 内置的 Flask 开发服务器) **不适合生产环境使用**。

### 1. 部署代码到 `/www/wwwroot/ai-mi`

```bash
mkdir -p /www/wwwroot
git clone https://git.silversea-media.net/silversea-media/marketintelligent/ai-mi.git /www/wwwroot/ai-mi
```

### 2. 创建虚拟环境并安装依赖

```bash
cd /www/wwwroot/ai-mi
python3 -m venv im-env
source im-env/bin/activate
pip install -r requirements.txt
pip install gunicorn
scrapling install
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入实际值（至少设置 GROQ_API_KEY 和 ADMIN_PASSWORD）
```

### 4. 启动/重启 Gunicorn

项目提供了 `deploy/start.sh` 脚本，自动处理「已运行则先停止再启动」的逻辑：

```bash
bash /www/wwwroot/ai-mi/deploy/start.sh
```

脚本行为：
- 如果已有 Gunicorn 进程在运行，先发送 `SIGTERM` 优雅停止（2 秒超时后 `SIGKILL` 强制终止）
- 然后以 `--daemon` 模式启动新进程，PID 写入 `gunicorn.pid`
- 启动后验证进程是否存活

> 手动停止：`kill $(cat /www/wwwroot/ai-mi/gunicorn.pid)`

### 5. 配置 Nginx 反向代理

`/etc/nginx/sites-available/silversea-mi`：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 超时配置（LLM 调用可能较慢）
        proxy_read_timeout 180s;
        proxy_connect_timeout 10s;
    }

    location /static {
        alias /www/wwwroot/ai-mi/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

### 6. 启用站点并重载 Nginx

```bash
# 先移除默认站点（避免端口冲突）
sudo rm -f /etc/nginx/sites-enabled/default

# 启用 Silversea MI 站点
sudo ln -s /etc/nginx/sites-available/silversea-mi /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 7. 配置防火墙（UFW）

Ubuntu 24.04 默认使用 `ufw`：

```bash
sudo ufw allow 80/tcp       # HTTP
sudo ufw allow 443/tcp      # HTTPS（如使用 SSL）
sudo ufw allow 22/tcp       # SSH（确保不把自己锁在外面！）
sudo ufw enable
sudo ufw status             # 确认规则生效
```

### 8. 配置 SSL/HTTPS（推荐）

使用 Certbot 获取免费的 Let's Encrypt 证书：

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
sudo certbot renew --dry-run   # 验证自动续期
```

Certbot 会自动修改 Nginx 配置添加 SSL 并设置 HTTP→HTTPS 重定向。

---

### 定时运行流水线（Cron）

生产环境中，你可能希望每日自动运行流水线：

```bash
crontab -e
```

```bash
# 每天早上 7:00 运行新加坡 BER 领域流水线
0 7 * * * cd /www/wwwroot/ai-mi && /www/wwwroot/ai-mi/im-env/bin/python main.py --country=SG --domain=BER --no-email >> /www/wwwroot/ai-mi/cron.log 2>&1

# 每天早上 7:30 运行越南 BER 领域流水线
30 7 * * * cd /www/wwwroot/ai-mi && /www/wwwroot/ai-mi/im-env/bin/python main.py --country=VN --domain=BER --no-email >> /www/wwwroot/ai-mi/cron.log 2>&1

# 每周日凌晨 3:00 运行周度摘要（main.py 在周日运行时自动触发）
0 3 * * 0 cd /www/wwwroot/ai-mi && /www/wwwroot/ai-mi/im-env/bin/python main.py --country=SG --domain=GENERAL --no-email >> /www/wwwroot/ai-mi/cron.log 2>&1
```

---

## 环境变量参考

| 变量名 | 必需 | 说明 |
|--------|------|------|
| `GROQ_API_KEY` | 仅流水线 | Groq API 密钥，用于 LLM 调用。在 [console.groq.com](https://console.groq.com) 免费注册 |
| `VIEWER_PASSWORD` | 否 | 仪表盘查看密码。不设置时默认为 `Silversea`，首次运行时自动写入 `data/viewer_password.txt` |
| `ADMIN_PASSWORD` | 仅管理功能 | `/admin` 页面密码。**无默认值** — 不设置则管理员登录被拒绝 |
| `GMAIL_USER` | 仅邮件功能 | 发送邮件摘要的 Gmail 地址 |
| `GMAIL_APP_PASSWORD` | 仅邮件功能 | Gmail 应用专用密码（非普通密码，在 [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) 生成） |
| `RECIPIENT_EMAILS` | 仅邮件功能 | 接收摘要的邮箱地址，逗号分隔 |

> ⚠️ **安全提醒：** `.env` 文件是每台机器独立的，已加入 `.gitignore` — 切勿提交到仓库。`ADMIN_PASSWORD` 没有内置默认值，请从 Silversea 共享密钥管理员处获取真实值。

---

## 故障排除

| 症状 | 解决方案 |
|------|---------|
| 立即重定向到 `/login`，不知道密码 | 使用 `Silversea` 登录（内置共享默认密码） |
| 流水线报错 `Executable doesn't exist at ...chrome-win64\chrome.exe` | 运行 `scrapling install`（`pip install -r requirements.txt` 之后的一次性步骤） |
| `pip install -r requirements.txt` 失败或行为异常 | 检查 `python3 --version` 是否匹配 `.python-version`（3.12.3）。此仓库的依赖项（`numpy`/`onnxruntime` 通过 `chromadb`）要求 Python 3.11+ |
| 即使登录后 `/admin` 仍被重定向 | `.env` 中未设置 `ADMIN_PASSWORD` — 管理员密码没有默认值，需要从团队获取 |
| 流水线运行但仪表盘不显示新数据 | 检查 `data/` 目录下是否生成了 `latest_report_{COUNTRY}_{DOMAIN}.json` 文件。仪表盘每次请求都会重新读取，但确保你的 URL 参数 `?country=` 和 `?domain=` 与流水线运行参数匹配 |
| ChromaDB 错误 | 确保 `data/` 目录可写。ChromaDB 数据存储在 `data/` 下的持久化目录中 |

---

## 项目结构

```
ai-mi/
├── app.py                  # Flask 仪表盘入口（查看者/管理员认证）
├── main.py                 # 流水线入口（抓取 → 过滤 → 分析 → 报告）
├── requirements.txt        # Python 依赖（精确版本锁定）
├── .python-version         # Python 版本约束（3.12.3）
├── .env.example            # 环境变量模板
├── config/
│   ├── sources.json        # 按国家分类的信息源列表（177 个，152 个活跃）
│   ├── sources.py          # 信息源加载/保存工具
│   └── models.py           # 数据模型
├── pipeline/
│   ├── scraper.py          # 分层抓取器（普通请求 / Scrapling stealth / dynamic-JS）
│   ├── filter.py           # 关键词过滤（优先级 + 通用分层权重）
│   ├── analyst.py          # LLM 分析（提取 → 综合 → 摘要，三次调用）
│   ├── report.py           # 报告 JSON 持久化
│   ├── emailer.py          # Gmail 邮件摘要（可选）
│   ├── feedback.py         # 反馈聚合 + ChromaDB RAG 闭环
│   ├── vectorstore.py      # ChromaDB 向量存储封装
│   ├── weekly.py           # 周度摘要压缩
│   └── source_suggestions.py # 信息源建议审批流程
├── data/
│   ├── latest_report*.json # 预生成报告文件 + 按国家/领域划分的报告
│   ├── company_context.md  # 公司背景知识文档
│   ├── viewer_password.txt # 查看者密码持久化文件
│   └── feedback/           # 用户反馈 JSON 文件
├── static/
│   ├── style.css           # 自定义样式
│   └── animations.js       # 前端动画
├── templates/
│   ├── base.html           # Jinja2 基础模板（导航、布局）
│   ├── report.html         # 仪表盘主页（信号、机会、风险）
│   ├── login.html          # 登录页面
│   ├── admin.html          # 管理页面（信息源审批、密码轮换）
│   └── internals.html      # 系统内部信息页面
├── deploy/                 # 部署文档
│   ├── deployment-zh.md    # 中文部署文档（本文件）
│   └── deployment-en.md    # 英文部署文档
├── docs/                   # 参考资料（PDF、Excel 模板等）
├── tests/                  # 测试
├── scripts/                # 辅助脚本
└── output/                 # 输出目录
```

---

## 架构概览

```
config/sources.json (按国家分类的信息源列表，含行业 + 领域标签)
  → 抓取器 (分层：plain requests / Scrapling stealth / Scrapling dynamic-JS)
  → 关键词过滤 (优先级 + 通用分层权重，按国家分列关键词列表)
  → 按行业提取 (每个行业一次 LLM 调用 — 列出每个具体信号，不做解读)
  → 按行业综合 (提取文本 → 结构化 JSON: 实体/信号/来源)
  → 摘要调用 (执行摘要 + 评分机会，一次调用)
  → data/latest_report_{COUNTRY}_{DOMAIN}.json
  → Flask 仪表盘 (查看者/管理员认证保护)
```

**关键设计决策：** 「提取-综合」分两步而非一步，因为将过多原始内容一次性输入大型综合调用会导致模型静默丢弃大部分信号 — 在测试中，拆分后信号数量从个位数提升到 65+。

**反馈闭环：** 仪表盘的反馈表单聚合提交内容，通过 LLM 总结为摘要，并存入 ChromaDB — 后续流水线运行会检索这些内容作为上下文，使团队反馈可量化地改变后续报告内容。

**机会评分：** 每个发现的机会按 5 个维度评分（战略匹配度、收入潜力、赢单概率、紧迫性、情报质量；各 1-5 分，满分 25 分）。评分区间：20-25 = 立即上报 BD，13-19 = 监控，0-12 = 仅记录。
