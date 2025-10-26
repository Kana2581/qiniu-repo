
# 秋招项目：语音助手项目演示 🚀

🎬 **演示视频**：[Bilibili 播放链接](https://www.bilibili.com/video/BV12VxNzuEhs/?share_source=copy_web&vd_source=f74e0c665f4fb75caa2057a3e0d75600)（建议 2 倍速观看）

---

## 一、环境准备

### 1. 启动基础服务（Docker Compose）

确保已安装 **Docker** 和 **Docker Compose**，然后在项目根目录下执行：

```bash
docker compose up -d
```

> 该命令会自动拉取并启动所需服务，如 MySQL、Redis 等。

---

### 2. 创建 Python 虚拟环境并安装依赖

建议使用 **Python 3.12**：

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装依赖包
pip install -r requirements.txt
```

---

### 3. 配置后端环境变量

项目根目录提供了 `.env.example` 文件，请复制一份并重命名为 `.env`：

```bash
cp .env.example .env
```

根据实际环境修改其中内容（数据库、Redis、密钥等配置）。

#### .env 示例内容：

```bash
# Database
DATABASE_URL=mysql+aiomysql://root:password@127.0.0.1:3306/ai_agent

# Redis
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password
REDIS_DECODE_RESPONSES=True

# Proxy (optional)
# HTTP_PROXY=http://127.0.0.1:7890
# HTTPS_PROXY=http://127.0.0.1:7890

HISTORY_MAX_TOKENS=5000
DEV=True

# 七牛云 TTS/ASR API Keys
TTS_AND_ASR_API_KEY=your_api_key

# 七牛云 Object Storage (KODO)
KOBO_ACCESS_KEY="your_access_key"
KOBO_SECRET_KEY="your_secret_key"
KOBO_BUCKET_NAME="your_bucket_name"
KOBO_BUCKET_DOMAIN="your_bucket_domain"
```

> ⚠️ **提示**：生产环境建议将密钥放入服务器环境变量，而不是直接提交到仓库。

---

## 二、后端启动

激活虚拟环境后运行：

```bash
uvicorn backend.app.main:app --reload
```

默认访问地址： 👉 [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 三、前端启动

进入前端目录：

```bash
cd frontend
```

安装依赖：

```bash
npm install
```

### 修改前端环境变量

前端 API 地址配置通常位于：

* `.env.development` — 开发环境
* `.env.production` — 生产环境

请根据后端启动地址修改 **接口 URL**：

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000
```

启动前端：

```bash
npm run dev
```

默认访问地址： 👉 [http://localhost:5173](http://localhost:5173)

---

## 四、项目演示

演示视频可直接在 B 站观看（建议 2 倍速）：
[Bilibili 播放链接](https://www.bilibili.com/video/BV12VxNzuEhs/?share_source=copy_web&vd_source=f74e0c665f4fb75caa2057a3e0d75600)

---

## 五、目录结构示例

```
project-root/
├── backend/
│   ├── app/
│   │   └── main.py
│   └── requirements.txt
├── frontend/
│   ├── .env.development
│   ├── .env.production
│   ├── package.json
│   └── src/
├── docker-compose.yml
├── .env.example
├── README.md
```

---


