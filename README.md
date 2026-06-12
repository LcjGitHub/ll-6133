# 家庭发酵实验日志

轻量级全栈 MVP：记录家庭发酵批次与观察笔记。

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Svelte 5 + Vite + TypeScript + Flowbite-Svelte |
| 数据请求 | @tanstack/svelte-query + axios |
| 路由 | svelte-routing |
| 后端 | FastAPI + SQLAlchemy |
| 数据库 | SQLite（`data/ferment.db`） |

## 功能

- **批次列表**：Flowbite 表格展示全部批次，支持新建与删除
- **批次详情**：查看/编辑批次信息，同页追加观察笔记
- **字段**：类型、开始日期、温度、状态、pH（可选）、笔记
- **种子数据**：首次启动自动写入 3 条示例批次

## 目录结构

```
├── backend/          # FastAPI 后端（端口 5000）
├── frontend/         # Svelte 前端（端口 5101）
├── data/             # SQLite 数据库（自动生成）
└── README.md
```

## 快速启动

### 1. 后端

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
# source .venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload --port 5000
```

后端 API 文档：http://localhost:5000/docs

### 2. 前端

另开终端：

```bash
cd frontend
npm install
npm run dev
```

前端地址：http://localhost:5101

## API 概览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/batches` | 批次列表 |
| POST | `/api/batches` | 创建批次 |
| GET | `/api/batches/{id}` | 批次详情（含笔记） |
| PUT | `/api/batches/{id}` | 更新批次 |
| DELETE | `/api/batches/{id}` | 删除批次 |
| POST | `/api/batches/{id}/notes` | 追加笔记 |
| DELETE | `/api/notes/{id}` | 删除笔记 |

## 说明

- 依赖均在项目目录内安装，无需全局 pnpm/yarn
- MVP 范围：无登录、JWT、Redis、Docker 及外部数据库
