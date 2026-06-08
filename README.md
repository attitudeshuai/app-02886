# Git Doc Fetcher

Git 仓库文档抓取工具 - 快速浏览、搜索和导出任意公开 Git 仓库的文档内容。

## 1. How to Run

```bash
docker compose up --build -d
```

## 2. Services

| 服务 | 地址 |
|------|------|
| **Frontend** | http://localhost:8081 |
| **Backend API** | http://localhost:8000 |
| **API Docs** | http://localhost:8000/docs |

## 3. 测试账号

本项目无需登录认证，直接访问即可使用所有功能。

## 4. 题目内容

> 使用 Python 开发项目：抓取 Git 仓库文档

---

## 项目介绍

Git Doc Fetcher 是一款简洁高效的 Git 仓库文档抓取工具，帮助用户快速浏览、搜索和导出任意公开仓库的文档内容。

### 核心功能

- **仓库管理**: 支持添加多个 Git 仓库，自动扫描并索引文档文件
- **文档浏览**: 精美的 Markdown 渲染，支持代码高亮和目录导航（双向联动）
- **全文搜索**: 快速搜索所有文档内容，关键词高亮显示
- **文档导出**: 支持单文档下载或批量打包 ZIP 下载

### 支持的文档格式

- Markdown (.md)
- 纯文本 (.txt)
- reStructuredText (.rst)
- AsciiDoc (.adoc)

---

## 技术栈

### 后端
- Python 3.11
- FastAPI
- SQLAlchemy + SQLite
- GitPython

### 前端
- React 18 + TypeScript
- Vite
- Tailwind CSS
- react-markdown + rehype

### 部署
- Docker + Docker Compose
- Nginx (反向代理)

---

## 项目结构

```
git-doc-fetcher/
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── main.py         # FastAPI 入口
│   │   ├── config.py       # 配置
│   │   ├── database.py     # 数据库
│   │   ├── models/         # 数据模型
│   │   ├── schemas/        # Pydantic 模式
│   │   ├── services/       # 业务服务
│   │   └── routers/        # API 路由
│   ├── requirements.txt
│   └── Dockerfile
├── frontend-user/           # 前端服务
│   ├── src/
│   │   ├── components/     # 组件
│   │   ├── pages/          # 页面
│   │   ├── api/            # API 调用
│   │   └── types/          # 类型定义
│   ├── package.json
│   └── Dockerfile
├── docs/                    # 文档
│   ├── Requirements.md     # 需求文档
│   ├── Roadmap.md          # 开发路线图
│   ├── DesignSpec.md       # 设计规范
│   └── SelfTestReport.md   # 自测报告
└── docker-compose.yml       # Docker 编排
```

---

## API 接口

### 仓库管理
- `GET /repositories` - 获取仓库列表
- `POST /repositories` - 添加仓库
- `DELETE /repositories/{id}` - 删除仓库
- `POST /repositories/{id}/refresh` - 刷新仓库

### 文档操作
- `GET /repositories/{id}/tree` - 获取文档树
- `GET /repositories/{id}/documents?filepath=xxx` - 获取文档内容

### 搜索
- `GET /search?q=xxx` - 全文搜索

### 导出
- `GET /repositories/{id}/export?filepath=xxx` - 导出单文档
- `GET /repositories/{id}/export-all` - 导出全部文档 (ZIP)

---

## 冲突解决日志

| 冲突点 | AI 分析 | 用户决策 |
|--------|---------|----------|
| PDF导出功能 | 依赖库兼容性问题复杂 | 用户决定移除 PDF 导出，仅保留 Markdown 导出 |

---

## License

MIT License
