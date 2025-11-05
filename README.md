# 相机数据库管理系统

一个基于 FastAPI 和 SQLModel 的相机设备、镜头和品牌数据库管理系统。

## 项目简介

本系统提供完整的相机设备管理功能，包括品牌、相机、镜头和卡口的CRUD操作，支持多对多关系管理和用户权限控制。

## 技术栈

- **后端框架**: FastAPI
- **ORM**: SQLModel
- **数据库**: SQLite (支持 PostgreSQL/MySQL)
- **迁移工具**: Alembic
- **包管理**: uv
- **认证**: JWT Token

## 项目结构

```
camera_db/
├── model/           # 数据模型定义
├── api/            # API接口路由
├── services/       # 业务逻辑服务
├── database/       # 数据库配置
├── alembic/        # 数据库迁移脚本
├── static/         # 静态文件
├── main.py         # 应用入口
└── create_superuser.py  # 超级用户创建脚本
```

## 快速开始

### 1. 安装依赖

```bash
uv sync
```

### 2. 初始化数据库

```bash
# 检查当前迁移状态
alembic current

# 执行数据库迁移
alembic upgrade head
```

### 3. 创建管理员用户

系统提供类似Django的超级用户创建功能：

```bash
# 交互式创建管理员用户
python create_superuser.py

# 创建测试数据（开发环境）
python create_superuser.py testdata

# 查看帮助信息
python create_superuser.py help
```

交互式创建过程会提示输入用户名、邮箱和密码，支持密码安全验证和自动截断处理。

### 4. 启动应用

```bash
python main.py
```

应用将在 `http://localhost:8000` 启动，自动提供交互式 API 文档。

## 环境配置

自行创建 `.env` 并配置：

```env
DATABASE_URL=sqlite:///camera.db
SECRET_KEY=your-secret-key
```

## 文档索引

- [数据模型文档](./model_docs.md) - 详细的数据模型说明和关系图
- [API接口文档](./api_docs.md) - 完整的API接口列表和使用示例

## 开发说明

- 使用 SQLModel 进行类型安全的数据库操作
- 支持数据库迁移和版本控制
- 包含完整的用户认证和权限管理
- 提供 Swagger UI 交互式文档

## 许可证

MIT License