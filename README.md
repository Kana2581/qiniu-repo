明白 👍 下面是更新后的最终版 **项目启动说明（README.md）**，已补充前端 `.env.development` / `.env.production` 文件修改说明，同时保留 `.env.example` 的提示。

---

# 🚀 项目启动说明

## 一、环境准备

### 1. 启动基础服务（使用 Docker Compose）

确保已安装 **Docker** 和 **Docker Compose**，然后在项目根目录下执行：

```bash
docker compose up -d
```

该命令会自动拉取并启动所需的镜像和服务（例如 MySQL、Redis 等）。

---

### 2. 创建 Python 虚拟环境并安装依赖

建议使用 **Python 3.9+**。

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖包
pip install -r requirements.txt
```

---

### 3. 配置后端环境变量

项目根目录下提供了 `.env.example` 文件。
请复制一份并重命名为 `.env`：

```bash
cp .env.example .env
```

然后根据实际环境修改其中内容（数据库、Redis、密钥等配置）。
`.env` 示例内容如下：

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

#七牛云 TTS/SSR API Keys
TTS_AND_ASR_API_KEY=your_api_key

#七牛云 Object Storage (KODO)
KOBO_ACCESS_KEY="your_access_key"
KOBO_SECRET_KEY="your_secret_key"
KOBO_BUCKET_NAME="your_bucket_name"
KOBO_BUCKET_DOMAIN="your_bucket_domain"
```

> ⚠️ 提示：生产环境建议将密钥放入服务器环境变量，而不是直接提交到仓库。

---

## 二、后端启动

激活虚拟环境后运行以下命令启动后端：

```bash
uvicorn backend.app.main:app --reload
```

默认访问地址：
👉 [http://127.0.0.1:8000](http://127.0.0.1:8000)

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

前端的 API 地址配置通常位于以下两个文件中：

* `.env.development` — 开发环境使用
* `.env.production` — 部署生产环境使用

请根据实际后端启动地址修改其中的 **接口 URL**（例如 `VITE_API_BASE_URL`）：

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000
```

修改完成后即可启动前端：

```bash
npm run dev
```

默认访问地址：
👉 [http://localhost:5173](http://localhost:5173)

---

## 四、项目演示

## 四、项目演示

演示视频可直接播放（建议 2 倍速观看）：

<video controls width="800" src="./演示视频建议2倍速观看.mp4">
您的浏览器不支持视频播放，请下载观看。
</video>

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
├── 项目演示.mp4
└── README.md
```

---

## 六、常见问题

| 问题               | 解决方案                                                     |
| ---------------- | -------------------------------------------------------- |
| **后端端口被占用**      | 修改命令：`uvicorn backend.app.main:app --reload --port 8080` |
| **前端访问后端接口失败**   | 检查 `.env.development` 或 `.env.production` 的接口地址是否与后端一致   |
| **数据库无法连接**      | 确认 Docker Compose 已启动并 `.env` 中数据库配置正确                   |
| **Redis 报错连接失败** | 若使用 Docker 内部网络，将 `REDIS_HOST` 改为 `redis`                |

---

是否希望我帮你把这个 README 格式化成带有目录和徽章的「GitHub 美化版」？（如自动生成目录、运行徽章、环境徽章等）
