# Personal Agent

一个基于 LangGraph 和 React 的智能个人助理项目，提供聊天、任务管理和代码审查功能。

## 技术栈

### 后端
- **Python**: 3.12
- **FastAPI**: 0.115.6
- **Uvicorn**: 0.34.0
- **LangGraph**: latest
- **LangChain**: latest
- **LangChain-OpenAI**: latest
- **SQLAlchemy**: latest (with asyncio support)
- **asyncpg**: latest
- **python-dotenv**: 1.0.1
- **PostgreSQL**: 14+ (推荐 16.6)

### 前端
- **Node.js**: 22.12.0 LTS (最低要求: 20.19+ 或 22.12+)
- **npm**: 10.x
- **React**: 19.2.6
- **React DOM**: 19.2.6
- **Vite**: 8.0.12
- **Ant Design**: 6.4.2
- **Ant Design Icons**: 6.2.3
- **ESLint**: 10.3.0

## 环境要求

1. **Python 3.12**
2. **Node.js 22.12.0 LTS** (或 20.19+)
3. **PostgreSQL 14+** (推荐使用 Docker)
4. **DeepSeek API Key**

## 快速开始

### 1. 安装 PostgreSQL (使用 Docker)

在 Linux 服务器上运行以下命令：

```bash
# 拉取 PostgreSQL 镜像
docker pull postgres:16

# 运行 PostgreSQL 容器
docker run -d \
  --name postgres-llmchat \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=llmchat123 \
  -e POSTGRES_DB=llmchat \
  -p 5432:5432 \
  -v postgres-data:/var/lib/postgresql/data \
  --restart unless-stopped \
  postgres:16

# 验证容器运行状态
docker ps | grep postgres-llmchat

# 查看日志
docker logs postgres-llmchat
```

**常用 Docker 命令：**
```bash
# 停止容器
docker stop postgres-llmchat

# 启动容器
docker start postgres-llmchat

# 重启容器
docker restart postgres-llmchat

# 进入 PostgreSQL 命令行
docker exec -it postgres-llmchat psql -U postgres -d llmchat
```

**初始化数据库表结构：**

项目使用 SQLAlchemy ORM，表结构会在首次运行时自动创建。如果需要手动创建或查看表结构，可以使用提供的 SQL 文件：

```bash
# 方法一：使用 Docker 执行 SQL 文件
docker exec -i postgres-llmchat psql -U postgres -d llmchat < backend/schema.sql

# 方法二：进入容器后执行
docker exec -it postgres-llmchat psql -U postgres -d llmchat
\i /path/to/schema.sql
```

**数据库表说明：**
- `threads`: 会话线程表，存储聊天会话信息
- `messages`: 消息表，存储会话中的所有消息（关联到 threads）

### 2. 配置环境变量

编辑 `backend/.env` 文件，配置数据库连接和 API Key：

```env
DATABASE_URL=postgresql+asyncpg://postgres:llmchat123@127.0.0.1:5432/llmchat
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

### 3. 安装依赖

**后端依赖：**
```bash
cd backend
pip install -r requirements.txt
```

**前端依赖：**
```bash
cd frontend
npm install
```

### 4. 启动服务

#### 方法一：使用启动脚本（推荐）

在项目根目录运行：
```bash
bash start.sh
```

这个脚本会自动：
- 安装后端和前端依赖
- 启动后端服务 (http://localhost:8000)
- 启动前端服务 (http://localhost:5173)
- 按 `Ctrl+C` 可同时停止两个服务

#### 方法二：手动分别启动

**启动后端：**
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**启动前端（新开终端）：**
```bash
cd frontend
npm run dev
```

## 访问地址

- **前端**: http://localhost:5173
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

## 项目结构

```
personal-agent/
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── agents/         # LangGraph 智能体
│   │   ├── api/            # API 路由
│   │   ├── core/           # 核心功能（图、LLM）
│   │   ├── db/             # 数据库模型和 CRUD
│   │   ├── models/         # Pydantic 模型
│   │   ├── services/       # 业务逻辑
│   │   └── main.py         # FastAPI 应用入口
│   ├── .env                # 环境变量配置
│   └── requirements.txt    # Python 依赖
├── frontend/               # 前端应用
│   ├── src/
│   │   ├── App.jsx         # 主应用组件
│   │   ├── KanbanPanel.jsx # 看板面板
│   │   └── CodeReviewCard.jsx # 代码审查卡片
│   ├── package.json        # npm 依赖
│   └── vite.config.js      # Vite 配置
└── start.sh                # 一键启动脚本
```

## 开发命令

### 后端

```bash
# 启动开发服务器（热重载）
uvicorn app.main:app --reload --port 8000

# 运行测试
pytest

# 代码格式化
black app/

# 类型检查
mypy app/
```

### 前端

```bash
# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview

# 代码检查
npm run lint
```

## 常见问题

### 1. Node.js 版本过低

如果遇到 `Vite requires Node.js version 20.19+ or 22.12+` 错误：

**使用 nvm 升级 Node.js：**
```bash
# 安装 nvm-windows (Windows)
# 下载: https://github.com/coreybutler/nvm-windows/releases

# 安装 Node.js 22.12.0
nvm install 22.12.0
nvm use 22.12.0

# 验证版本
node --version
```

### 2. PostgreSQL 连接失败

确保：
- PostgreSQL 容器正在运行：`docker ps`
- 端口 5432 未被占用
- `.env` 文件中的连接信息正确

### 3. 前端依赖安装失败

尝试清理缓存并重新安装：
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## License

MIT
