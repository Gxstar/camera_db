# 相机镜头数据库 API 接口文档

本文档描述了相机镜头数据库系统的 RESTful API 接口规范，为前端开发者提供完整的接口调用指南。系统采用 FastAPI 框架构建，使用 JWT 进行身份验证，支持品牌、卡口、相机、镜头等核心业务实体的 CRUD 操作。

## 目录

- [1. 快速开始](#1-快速开始)
- [2. 认证与授权](#2-认证与授权)
- [3. 品牌接口](#3-品牌接口)
- [4. 卡口接口](#4-卡口接口)
- [5. 相机接口](#5-相机接口)
- [6. 镜头接口](#6-镜头接口)
- [7. 用户接口](#7-用户接口)
- [8. 认证接口](#8-认证接口)
- [9. 通用错误码](#9-通用错误码)

## 1. 快速开始

### 1.1 基础信息

所有 API 接口均以 `/api/v1` 为基础路径前缀。系统采用 JSON 格式进行数据交换，编码为 UTF-8。数据库使用 SQLite，存储在 `camera.db` 文件中。

- API 基础路径：`http://{host}:{port}/api/v1`
- Swagger 文档：`http://{host}:{port}/docs`
- ReDoc 文档：`http://{host}:{port}/redoc`
- 默认服务地址：`http://localhost:8000`

### 1.2 请求头要求

所有接口的请求头需要包含 `Content-Type: application/json`。需要身份验证的接口还需添加 `Authorization: Bearer {token}`。

```http
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

令牌有效期为 30 分钟，过期后需要刷新。建议前端在检测到 401 错误时自动引导用户重新登录。

### 1.3 响应格式

成功响应的数据格式如下：

```json
{
  "id": 1,
  "name": "Canon",
  "country": "日本",
  "website": "https://www.canon.com",
  "is_active": true,
  "create_time": "2024-01-15T10:30:00",
  "update_time": "2024-01-15T10:30:00"
}
```

批量查询返回数组格式：

```json
[
  {
    "id": 1,
    "name": "Canon",
    "country": "日本",
    "website": "https://www.canon.com",
    "is_active": true,
    "create_time": "2024-01-15T10:30:00",
    "update_time": "2024-01-15T10:30:00"
  }
]
```

## 2. 认证与授权

### 2.1 权限体系

系统采用 RBAC 模型，分为两种角色：

| 角色 | 说明 |
|------|------|
| ADMIN | 管理员，拥有所有权限 |
| USER | 普通用户，仅可查看 |

管理员账户需要通过 `create_superuser.py` 脚本创建，普通用户无法自助注册。

### 2.2 登录流程

```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=admin&password=your_password
```

成功响应：

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "role": "ADMIN",
    "is_active": true
  }
}
```

### 2.3 令牌刷新

```http
POST /api/v1/auth/refresh
Authorization: Bearer {current_token}
```

## 3. 品牌接口

品牌接口用于管理相机品牌信息。

### 3.1 获取品牌列表

**请求方式：** GET

**路径：** `/api/v1/brands/`

**查询参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| skip | integer | 否 | 0 | 跳过的记录数 |
| limit | integer | 否 | 100 | 返回数量，最大1000 |
| is_active | boolean | 否 | - | 按激活状态筛选 |
| brand_type | string | 否 | - | 按品牌类型筛选 |

**响应示例：**

```json
[
  {
    "id": 1,
    "name": "Canon",
    "country": "日本",
    "website": "https://www.canon.com",
    "brand_type": "相机厂商",
    "is_active": true,
    "create_time": "2024-01-15T10:30:00",
    "update_time": "2024-01-15T10:30:00"
  }
]
```

### 3.2 获取单个品牌

**请求方式：** GET

**路径：** `/api/v1/brands/{brand_id}`

**路径参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| brand_id | integer | 是 | 品牌 ID |

### 3.3 根据名称获取品牌

**请求方式：** GET

**路径：** `/api/v1/brands/name/{brand_name}`

### 3.4 创建品牌

**请求方式：** POST

**路径：** `/api/v1/brands/`

**请求头：** `Authorization: Bearer {token}`

**请求体：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 品牌名称，最大100字符 |
| country | string | 否 | 国家/地区 |
| website | string | 否 | 官方网站URL |
| brand_type | string | 否 | 品牌类型 |
| logo_url | string | 否 | Logo URL |
| description | string | 否 | 品牌描述 |

### 3.5 更新品牌

**请求方式：** PUT

**路径：** `/api/v1/brands/{brand_id}`

### 3.6 删除品牌

**请求方式：** DELETE

**路径：** `/api/v1/brands/{brand_id}`

**错误响应：** 存在关联相机时无法删除

```json
{
  "detail": "该品牌下有5个相机，无法删除"
}
```

### 3.7 激活/停用品牌

**请求方式：** PATCH

**路径：** `/api/v1/brands/{brand_id}/activate` 或 `/api/v1/brands/{brand_id}/deactivate`

### 3.8 获取品牌类型列表

**请求方式：** GET

**路径：** `/api/v1/brands/types/`

**响应示例：**

```json
["相机厂商", "镜头厂商", "传统光学厂商", "数码相机厂商", "无反相机厂商"]
```

## 4. 卡口接口

卡口接口用于管理相机卡口信息，如索尼 E 卡口、佳能 RF 卡口等。

### 4.1 获取卡口列表

**请求方式：** GET

**路径：** `/api/v1/mounts/`

**查询参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| skip | integer | 否 | 0 | 跳过的记录数 |
| limit | integer | 否 | 100 | 返回数量，1-1000 |
| is_active | boolean | 否 | - | 按激活状态筛选 |

**响应示例：**

```json
[
  {
    "id": 1,
    "name": "Sony E",
    "flange_distance": 18.0,
    "release_year": 2010,
    "description": "索尼无反相机卡口",
    "is_active": true,
    "create_time": "2024-01-15T10:30:00",
    "update_time": "2024-01-15T10:30:00"
  }
]
```

### 4.2 获取单个卡口

**请求方式：** GET

**路径：** `/api/v1/mounts/{mount_id}`

### 4.3 根据名称获取卡口

**请求方式：** GET

**路径：** `/api/v1/mounts/name/{name}`

### 4.4 创建卡口

**请求方式：** POST

**路径：** `/api/v1/mounts/`

**请求体：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 卡口名称 |
| flange_distance | number | 否 | 法兰距（mm） |
| release_year | integer | 否 | 发布年份 |
| description | string | 否 | 卡口描述 |
| is_active | boolean | 否 | 是否激活，默认 true |

### 4.5 更新卡口

**请求方式：** PUT

**路径：** `/api/v1/mounts/{mount_id}`

### 4.6 删除卡口

**请求方式：** DELETE

**路径：** `/api/v1/mounts/{mount_id}`

**错误响应：**

```json
{
  "detail": "无法删除卡口，有 10 台相机使用该卡口"
}
```

### 4.7 搜索卡口

**请求方式：** GET

**路径：** `/api/v1/mounts/search/`

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| query | string | 是 | 搜索关键词，最少1字符 |
| skip | integer | 否 | 跳过的记录数 |
| limit | integer | 否 | 返回数量 |

## 5. 相机接口

相机接口用于管理相机产品信息。

### 5.1 获取相机列表

**请求方式：** GET

**路径：** `/api/v1/cameras/`

**查询参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| skip | integer | 否 | 0 | 跳过的记录数 |
| limit | integer | 否 | 100 | 返回数量 |
| is_active | boolean | 否 | - | 按激活状态筛选 |
| brand_id | integer | 否 | - | 按品牌筛选 |
| mount_id | integer | 否 | - | 按卡口筛选 |
| sensor_size | string | 否 | - | 按传感器尺寸筛选 |

**传感器尺寸可选值：**

| 值 | 说明 |
|----|------|
| medium_format | 中画幅 |
| full_frame | 全画幅 |
| aps_c | 半画幅 |
| m43 | M43 |
| one_inch | 一英寸 |
| other | 其他 |

**响应示例：**

```json
[
  {
    "id": 1,
    "brand_id": 1,
    "mount_id": 2,
    "sensor_size": "full_frame",
    "series": "EOS R",
    "model": "EOS R5",
    "megapixels": 45.0,
    "ibis_level": "5级",
    "has_hot_shoe": true,
    "has_built_in_flash": false,
    "has_wifi": true,
    "has_bluetooth": true,
    "release_date": "2020-07-09",
    "release_price": 25999.0,
    "weight": 738.0,
    "is_active": true,
    "description": "佳能EOS R5全画幅微单相机",
    "create_time": "2024-01-15T10:30:00",
    "update_time": "2024-01-15T10:30:00"
  }
]
```

### 5.2 获取单个相机

**请求方式：** GET

**路径：** `/api/v1/cameras/{camera_id}`

### 5.3 创建相机

**请求方式：** POST

**路径：** `/api/v1/cameras/`

**请求体：**

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| brand_id | integer | 是 | - | 品牌 ID |
| mount_id | integer | 是 | - | 卡口 ID |
| sensor_size | string | 否 | - | 传感器尺寸 |
| series | string | 否 | - | 产品系列 |
| model | string | 是 | - | 相机型号 |
| megapixels | number | 否 | - | 有效像素（百万） |
| ibis_level | string | 否 | - | 机身防抖级别 |
| has_hot_shoe | boolean | 否 | true | 是否有热靴 |
| has_built_in_flash | boolean | 否 | false | 是否有内置闪光灯 |
| has_wifi | boolean | 否 | true | 是否有WiFi |
| has_bluetooth | boolean | 否 | true | 是否有蓝牙 |
| release_date | string | 否 | - | 发布日期 |
| release_price | number | 否 | - | 发布价格（元） |
| weight | number | 否 | - | 重量（克） |
| description | string | 否 | - | 备注说明 |

### 5.4 更新相机

**请求方式：** PUT

**路径：** `/api/v1/cameras/{camera_id}`

### 5.5 删除相机

**请求方式：** DELETE

**路径：** `/api/v1/cameras/{camera_id}`

### 5.6 激活/停用相机

**请求方式：** PATCH

**路径：** `/api/v1/cameras/{camera_id}/activate` 或 `/api/v1/cameras/{camera_id}/deactivate`

## 6. 镜头接口

镜头接口用于管理镜头产品信息。

### 6.1 获取镜头列表

**请求方式：** GET

**路径：** `/api/v1/lenses/`

**查询参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| skip | integer | 否 | 0 | 跳过的记录数 |
| limit | integer | 否 | 100 | 返回数量 |
| is_active | boolean | 否 | - | 按激活状态筛选 |
| brand_id | integer | 否 | - | 按品牌筛选 |
| mount_id | integer | 否 | - | 按卡口筛选 |
| lens_type | string | 否 | - | 按镜头类型筛选 |
| focus_type | string | 否 | - | 按对焦方式筛选 |
| has_stabilization | boolean | 否 | - | 按防抖功能筛选 |

**镜头类型可选值：**

| 值 | 说明 |
|----|------|
| prime | 定焦镜头 |
| zoom | 变焦镜头 |
| macro | 微距镜头 |
| fisheye | 鱼眼镜头 |
| tilt_shift | 移轴镜头 |
| teleconverter | 增距镜 |

**对焦方式可选值：**

| 值 | 说明 |
|----|------|
| autofocus | 自动对焦 |
| manual | 手动对焦 |
| autofocus_manual | 自动+手动 |

**响应示例：**

```json
[
  {
    "id": 1,
    "brand_id": 1,
    "mount_id": 2,
    "model": "RF 24-105mm F4 L IS USM",
    "lens_type": "zoom",
    "focus_type": "autofocus_manual",
    "min_focal_length": 24.0,
    "max_focal_length": 105.0,
    "min_aperture": 4.0,
    "max_aperture": 22.0,
    "has_stabilization": true,
    "min_focus_distance": 0.45,
    "filter_thread": 77.0,
    "weight": 700.0,
    "length": 107.3,
    "release_date": "2018-11-01",
    "release_price": 2899.0,
    "is_active": true,
    "description": "佳能RF 24-105mm F4 L IS USM标准变焦镜头",
    "create_time": "2024-01-15T10:30:00",
    "update_time": "2024-01-15T10:30:00"
  }
]
```

### 6.2 获取单个镜头

**请求方式：** GET

**路径：** `/api/v1/lenses/{lens_id}`

### 6.3 根据型号获取镜头

**请求方式：** GET

**路径：** `/api/v1/lenses/model/{model}`

### 6.4 创建镜头

**请求方式：** POST

**路径：** `/api/v1/lenses/`

**请求体：**

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| brand_id | integer | 是 | - | 品牌 ID |
| mount_id | integer | 是 | - | 卡口 ID |
| model | string | 是 | - | 镜头型号 |
| lens_type | string | 否 | - | 镜头类型 |
| focus_type | string | 否 | - | 对焦方式 |
| min_focal_length | number | 否 | - | 最小焦距（mm） |
| max_focal_length | number | 否 | - | 最大焦距（mm） |
| min_aperture | number | 否 | - | 最大光圈 |
| max_aperture | number | 否 | - | 最小光圈 |
| has_stabilization | boolean | 否 | - | 是否有防抖 |
| min_focus_distance | number | 否 | - | 最近对焦距离（m） |
| filter_thread | number | 否 | - | 滤镜口径（mm） |
| weight | number | 否 | - | 重量（克） |
| length | number | 否 | - | 长度（mm） |
| release_date | string | 否 | - | 发布日期 |
| release_price | number | 否 | - | 发布价格（元） |
| description | string | 否 | - | 备注说明 |

### 6.5 更新镜头

**请求方式：** PUT

**路径：** `/api/v1/lenses/{lens_id}`

### 6.6 删除镜头

**请求方式：** DELETE

**路径：** `/api/v1/lenses/{lens_id}`

### 6.7 激活/停用镜头

**请求方式：** PATCH

**路径：** `/api/v1/lenses/{lens_id}/activate` 或 `/api/v1/lenses/{lens_id}/deactivate`

### 6.8 辅助接口

**获取镜头类型列表：**

```http
GET /api/v1/lenses/types/
```

**响应：** `["prime", "zoom", "macro", "fisheye", "tilt_shift", "teleconverter"]`

**获取对焦方式列表：**

```http
GET /api/v1/lenses/focus-types/
```

**响应：** `["autofocus", "manual", "autofocus_manual"]`

**搜索镜头：**

```http
GET /api/v1/lenses/search/?q=85mm&limit=10
```

## 7. 用户接口

用户接口用于管理系统用户。

### 7.1 获取用户列表

**请求方式：** GET

**路径：** `/api/v1/users/`

**查询参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| skip | integer | 否 | 0 | 跳过的记录数 |
| limit | integer | 否 | 100 | 返回数量 |
| username | string | 否 | - | 用户名筛选 |
| email | string | 否 | - | 邮箱筛选 |
| role | string | 否 | - | 角色筛选 |
| is_active | boolean | 否 | - | 按激活状态筛选 |

**用户角色：**

| 值 | 说明 |
|----|------|
| ADMIN | 管理员 |
| USER | 普通用户 |

**响应示例：**

```json
[
  {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "role": "ADMIN",
    "is_active": true,
    "create_time": "2024-01-15T10:30:00",
    "update_time": "2024-01-15T10:30:00"
  }
]
```

### 7.2 获取单个用户

**请求方式：** GET

**路径：** `/api/v1/users/{user_id}`

### 7.3 获取当前用户信息

**请求方式：** GET

**路径：** `/api/v1/users/me`

### 7.4 创建用户

**请求方式：** POST

**路径：** `/api/v1/users/`

**请求体：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名，4-50字符 |
| email | string | 否 | 邮箱地址 |
| password | string | 是 | 密码，最少6字符 |
| role | string | 否 | 角色，默认 USER |

### 7.5 更新用户

**请求方式：** PUT

**路径：** `/api/v1/users/{user_id}`

**请求体：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 否 | 用户名 |
| email | string | 否 | 邮箱地址 |
| password | string | 否 | 新密码 |
| role | string | 否 | 角色 |
| is_active | boolean | 否 | 是否激活 |

### 7.6 更新当前用户

**请求方式：** PUT

**路径：** `/api/v1/users/me`

### 7.7 删除用户

**请求方式：** DELETE

**路径：** `/api/v1/users/{user_id}`

### 7.8 激活/停用用户

**请求方式：** PATCH

**路径：** `/api/v1/users/{user_id}/activate` 或 `/api/v1/users/{user_id}/deactivate`

## 8. 认证接口

### 8.1 用户登录

**请求方式：** POST

**路径：** `/api/v1/auth/login`

**请求头：** `Content-Type: application/x-www-form-urlencoded`

**请求体：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名 |
| password | string | 是 | 密码 |

**错误响应：**

```json
{
  "detail": "用户名或密码错误"
}
```

或

```json
{
  "detail": "用户已被停用"
}
```

### 8.2 刷新令牌

**请求方式：** POST

**路径：** `/api/v1/auth/refresh`

**请求头：** `Authorization: Bearer {token}`

### 8.3 获取当前用户

**请求方式：** GET

**路径：** `/api/v1/auth/me`

**请求头：** `Authorization: Bearer {token}`

## 9. 通用错误码

### 9.1 HTTP 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 201 | 资源创建成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 422 | 数据验证错误 |
| 500 | 服务器内部错误 |

### 9.2 常见错误信息

```json
{ "detail": "用户名或密码错误" }
```

```json
{ "detail": "用户已被停用" }
```

```json
{ "detail": "需要管理员权限" }
```

```json
{ "detail": "品牌不存在" }
```

```json
{ "detail": "品牌名称 'Sony' 已存在" }
```

### 9.3 前端处理建议

- **401 错误**：令牌过期，自动引导用户重新登录
- **403 错误**：权限不足，隐藏相关操作按钮
- **400/422 错误**：参数验证失败，显示具体错误信息
- **500 错误**：服务器错误，记录日志并提示用户重试

## 附录

### 接口索引

| 模块 | 接口 | 方法 | 路径 | 公开 |
|------|------|------|------|------|
| 认证 | 登录 | POST | /api/v1/auth/login | 是 |
| 认证 | 刷新令牌 | POST | /api/v1/auth/refresh | 否 |
| 认证 | 当前用户 | GET | /api/v1/auth/me | 否 |
| 品牌 | 列表 | GET | /api/v1/brands/ | 是 |
| 品牌 | 单个 | GET | /api/v1/brands/{id} | 是 |
| 品牌 | 名称查询 | GET | /api/v1/brands/name/{name} | 是 |
| 品牌 | 创建 | POST | /api/v1/brands/ | 否 |
| 品牌 | 更新 | PUT | /api/v1/brands/{id} | 否 |
| 品牌 | 删除 | DELETE | /api/v1/brands/{id} | 否 |
| 品牌 | 激活/停用 | PATCH | /api/v1/brands/{id}/activate,deactivate | 否 |
| 品牌 | 类型列表 | GET | /api/v1/brands/types/ | 是 |
| 卡口 | 列表 | GET | /api/v1/mounts/ | 是 |
| 卡口 | 单个 | GET | /api/v1/mounts/{id} | 是 |
| 卡口 | 名称查询 | GET | /api/v1/mounts/name/{name} | 是 |
| 卡口 | 创建 | POST | /api/v1/mounts/ | 否 |
| 卡口 | 更新 | PUT | /api/v1/mounts/{id} | 否 |
| 卡口 | 删除 | DELETE | /api/v1/mounts/{id} | 否 |
| 卡口 | 搜索 | GET | /api/v1/mounts/search/ | 是 |
| 相机 | 列表 | GET | /api/v1/cameras/ | 是 |
| 相机 | 单个 | GET | /api/v1/cameras/{id} | 是 |
| 相机 | 创建 | POST | /api/v1/cameras/ | 否 |
| 相机 | 更新 | PUT | /api/v1/cameras/{id} | 否 |
| 相机 | 删除 | DELETE | /api/v1/cameras/{id} | 否 |
| 相机 | 激活/停用 | PATCH | /api/v1/cameras/{id}/activate,deactivate | 否 |
| 镜头 | 列表 | GET | /api/v1/lenses/ | 是 |
| 镜头 | 单个 | GET | /api/v1/lenses/{id} | 是 |
| 镜头 | 型号查询 | GET | /api/v1/lenses/model/{model} | 是 |
| 镜头 | 创建 | POST | /api/v1/lenses/ | 否 |
| 镜头 | 更新 | PUT | /api/v1/lenses/{id} | 否 |
| 镜头 | 删除 | DELETE | /api/v1/lenses/{id} | 否 |
| 镜头 | 激活/停用 | PATCH | /api/v1/lenses/{id}/activate,deactivate | 否 |
| 镜头 | 类型列表 | GET | /api/v1/lenses/types/ | 是 |
| 镜头 | 对焦方式列表 | GET | /api/v1/lenses/focus-types/ | 是 |
| 镜头 | 搜索 | GET | /api/v1/lenses/search/ | 是 |
| 用户 | 列表 | GET | /api/v1/users/ | 否 |
| 用户 | 单个 | GET | /api/v1/users/{id} | 否 |
| 用户 | 当前用户 | GET | /api/v1/users/me | 否 |
| 用户 | 创建 | POST | /api/v1/users/ | 否 |
| 用户 | 更新 | PUT | /api/v1/users/{id} | 否 |
| 用户 | 更新自己 | PUT | /api/v1/users/me | 否 |
| 用户 | 删除 | DELETE | /api/v1/users/{id} | 否 |
| 用户 | 激活/停用 | PATCH | /api/v1/users/{id}/activate,deactivate | 否 |

### JavaScript 请求示例

```javascript
const API_BASE = 'http://localhost:8000/api/v1';

// 登录
const login = async (username, password) => {
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);
  
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: formData
  });
  return res.json();
};

// API 请求封装
const request = async (method, path, data = null, token = null) => {
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  
  const options = { method, headers };
  if (data) options.body = JSON.stringify(data);
  
  const res = await fetch(`${API_BASE}${path}`, options);
  if (!res.ok) throw new Error((await res.json()).detail);
  return res.json();
};

// 获取品牌列表
const getBrands = (token) => request('GET', '/brands/', null, token);

// 获取相机列表
const getCameras = (params = {}, token) => {
  const query = new URLSearchParams(params).toString();
  return request('GET', `/cameras/?${query}`, null, token);
};
```

文档版本：1.0.0
最后更新：2025年12月24日
