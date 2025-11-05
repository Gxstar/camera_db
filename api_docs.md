# API接口文档

本系统提供完整的RESTful API接口，支持相机设备、镜头、品牌和卡口的CRUD操作，包含用户认证和权限管理。

## 基础信息

- **API前缀**: `/api/v1`
- **认证方式**: JWT Bearer Token
- **文档地址**: `/docs` (自定义Swagger UI)

## 认证接口

### 用户登录
- **端点**: `POST /api/v1/auth/login`
- **权限**: 公开访问
- **描述**: 用户登录获取访问令牌
- **请求体**:
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **响应**: 包含访问令牌和用户信息

### 刷新令牌
- **端点**: `POST /api/v1/auth/refresh`
- **权限**: 需要登录
- **描述**: 刷新访问令牌

### 获取当前用户信息
- **端点**: `GET /api/v1/auth/me`
- **权限**: 需要登录
- **描述**: 获取当前登录用户信息

## 用户管理接口

### 创建用户
- **端点**: `POST /api/v1/users/`
- **权限**: 需要管理员权限
- **描述**: 创建新用户

### 获取用户列表
- **端点**: `GET /api/v1/users/`
- **权限**: 需要登录
- **描述**: 获取用户列表，支持筛选
- **查询参数**:
  - `username`: 按用户名筛选
  - `email`: 按邮箱筛选
  - `role`: 按角色筛选
  - `is_active`: 按激活状态筛选
  - `skip`: 跳过记录数
  - `limit`: 返回记录数

### 获取单个用户
- **端点**: `GET /api/v1/users/{user_id}`
- **权限**: 需要登录
- **描述**: 根据ID获取用户信息

### 更新用户信息
- **端点**: `PUT /api/v1/users/{user_id}`
- **权限**: 需要管理员权限
- **描述**: 更新用户信息

### 删除用户
- **端点**: `DELETE /api/v1/users/{user_id}`
- **权限**: 需要管理员权限
- **描述**: 删除用户

### 激活/停用用户
- **端点**: `PATCH /api/v1/users/{user_id}/activate` / `PATCH /api/v1/users/{user_id}/deactivate`
- **权限**: 需要管理员权限
- **描述**: 激活或停用用户

### 获取当前用户信息
- **端点**: `GET /api/v1/users/me`
- **权限**: 需要登录
- **描述**: 获取当前登录用户信息

### 更新当前用户信息
- **端点**: `PUT /api/v1/users/me`
- **权限**: 需要登录
- **描述**: 更新当前登录用户信息

## 品牌管理接口

### 创建品牌
- **端点**: `POST /api/v1/brands/`
- **权限**: 需要管理员权限
- **描述**: 创建新品牌

### 获取品牌列表
- **端点**: `GET /api/v1/brands/`
- **权限**: 公开访问
- **描述**: 获取品牌列表，支持筛选
- **查询参数**:
  - `is_active`: 按激活状态筛选
  - `brand_type`: 按品牌类型筛选
  - `skip`: 跳过记录数
  - `limit`: 返回记录数

### 获取单个品牌
- **端点**: `GET /api/v1/brands/{brand_id}`
- **权限**: 公开访问
- **描述**: 根据ID获取品牌信息

### 根据名称获取品牌
- **端点**: `GET /api/v1/brands/name/{brand_name}`
- **权限**: 公开访问
- **描述**: 根据品牌名称获取品牌信息

### 更新品牌信息
- **端点**: `PUT /api/v1/brands/{brand_id}`
- **权限**: 需要管理员权限
- **描述**: 更新品牌信息

### 删除品牌
- **端点**: `DELETE /api/v1/brands/{brand_id}`
- **权限**: 需要管理员权限
- **描述**: 删除品牌

### 激活/停用品牌
- **端点**: `PATCH /api/v1/brands/{brand_id}/activate` / `PATCH /api/v1/brands/{brand_id}/deactivate`
- **权限**: 需要管理员权限
- **描述**: 激活或停用品牌

### 获取品牌类型列表
- **端点**: `GET /api/v1/brands/types/`
- **权限**: 公开访问
- **描述**: 获取所有品牌类型列表

## 相机管理接口

### 创建相机
- **端点**: `POST /api/v1/cameras/`
- **权限**: 需要管理员权限
- **描述**: 创建新相机

### 获取相机列表
- **端点**: `GET /api/v1/cameras/`
- **权限**: 公开访问
- **描述**: 获取相机列表，支持筛选
- **查询参数**:
  - `is_active`: 按激活状态筛选
  - `brand_id`: 按品牌ID筛选
  - `mount_id`: 按卡口ID筛选
  - `sensor_size`: 按传感器尺寸筛选
  - `skip`: 跳过记录数
  - `limit`: 返回记录数

### 获取单个相机
- **端点**: `GET /api/v1/cameras/{camera_id}`
- **权限**: 公开访问
- **描述**: 根据ID获取相机信息

### 更新相机信息
- **端点**: `PUT /api/v1/cameras/{camera_id}`
- **权限**: 需要管理员权限
- **描述**: 更新相机信息

### 删除相机
- **端点**: `DELETE /api/v1/cameras/{camera_id}`
- **权限**: 需要管理员权限
- **描述**: 删除相机

### 激活/停用相机
- **端点**: `PATCH /api/v1/cameras/{camera_id}/activate` / `PATCH /api/v1/cameras/{camera_id}/deactivate`
- **权限**: 需要管理员权限
- **描述**: 激活或停用相机

## 镜头管理接口

### 创建镜头
- **端点**: `POST /api/v1/lenses/`
- **权限**: 需要管理员权限
- **描述**: 创建新镜头

### 获取镜头列表
- **端点**: `GET /api/v1/lenses/`
- **权限**: 公开访问
- **描述**: 获取镜头列表，支持筛选
- **查询参数**:
  - `is_active`: 按激活状态筛选
  - `brand_id`: 按品牌ID筛选
  - `mount_id`: 按卡口ID筛选
  - `lens_type`: 按镜头类型筛选
  - `focus_type`: 按对焦方式筛选
  - `has_stabilization`: 按防抖功能筛选
  - `skip`: 跳过记录数
  - `limit`: 返回记录数

### 获取单个镜头
- **端点**: `GET /api/v1/lenses/{lens_id}`
- **权限**: 公开访问
- **描述**: 根据ID获取镜头信息

### 根据型号获取镜头
- **端点**: `GET /api/v1/lenses/model/{model}`
- **权限**: 公开访问
- **描述**: 根据镜头型号获取镜头信息

### 更新镜头信息
- **端点**: `PUT /api/v1/lenses/{lens_id}`
- **权限**: 需要管理员权限
- **描述**: 更新镜头信息

### 删除镜头
- **端点**: `DELETE /api/v1/lenses/{lens_id}`
- **权限**: 需要管理员权限
- **描述**: 删除镜头

### 激活/停用镜头
- **端点**: `PATCH /api/v1/lenses/{lens_id}/activate` / `PATCH /api/v1/lenses/{lens_id}/deactivate`
- **权限**: 需要管理员权限
- **描述**: 激活或停用镜头

### 获取镜头类型列表
- **端点**: `GET /api/v1/lenses/types/`
- **权限**: 公开访问
- **描述**: 获取所有镜头类型列表

### 获取对焦方式列表
- **端点**: `GET /api/v1/lenses/focus-types/`
- **权限**: 公开访问
- **描述**: 获取所有对焦方式列表

### 搜索镜头
- **端点**: `GET /api/v1/lenses/search/`
- **权限**: 公开访问
- **描述**: 根据关键词搜索镜头
- **查询参数**:
  - `q`: 搜索关键词
  - `skip`: 跳过记录数
  - `limit`: 返回记录数

## 卡口管理接口

### 创建卡口
- **端点**: `POST /api/v1/mounts/`
- **权限**: 需要管理员权限
- **描述**: 创建新卡口

### 获取卡口列表
- **端点**: `GET /api/v1/mounts/`
- **权限**: 公开访问
- **描述**: 获取卡口列表，支持筛选
- **查询参数**:
  - `is_active`: 按激活状态筛选
  - `skip`: 跳过记录数
  - `limit`: 返回记录数

### 获取单个卡口
- **端点**: `GET /api/v1/mounts/{mount_id}`
- **权限**: 公开访问
- **描述**: 根据ID获取卡口详情

### 根据名称获取卡口
- **端点**: `GET /api/v1/mounts/name/{name}`
- **权限**: 公开访问
- **描述**: 根据名称获取卡口

### 更新卡口信息
- **端点**: `PUT /api/v1/mounts/{mount_id}`
- **权限**: 需要管理员权限
- **描述**: 更新卡口信息

### 删除卡口
- **端点**: `DELETE /api/v1/mounts/{mount_id}`
- **权限**: 需要管理员权限
- **描述**: 删除卡口

### 激活/停用卡口
- **端点**: `PATCH /api/v1/mounts/{mount_id}/activate` / `PATCH /api/v1/mounts/{mount_id}/deactivate`
- **权限**: 需要管理员权限
- **描述**: 激活或停用卡口

### 为卡口添加品牌支持
- **端点**: `POST /api/v1/mounts/{mount_id}/brands`
- **权限**: 需要管理员权限
- **描述**: 为卡口添加品牌支持关系

### 从卡口移除品牌支持
- **端点**: `DELETE /api/v1/mounts/{mount_id}/brands/{brand_id}`
- **权限**: 需要管理员权限
- **描述**: 从卡口移除品牌支持关系

### 获取卡口支持的品牌列表
- **端点**: `GET /api/v1/mounts/{mount_id}/brands`
- **权限**: 公开访问
- **描述**: 获取支持该卡口的品牌列表

### 获取使用卡口的相机列表
- **端点**: `GET /api/v1/mounts/{mount_id}/cameras`
- **权限**: 公开访问
- **描述**: 获取使用该卡口的相机列表

### 获取使用卡口的镜头列表
- **端点**: `GET /api/v1/mounts/{mount_id}/lenses`
- **权限**: 公开访问
- **描述**: 获取使用该卡口的镜头列表

### 搜索卡口
- **端点**: `GET /api/v1/mounts/search/`
- **权限**: 公开访问
- **描述**: 根据关键词搜索卡口
- **查询参数**:
  - `query`: 搜索关键词
  - `skip`: 跳过记录数
  - `limit`: 返回记录数

## 权限说明

- **公开访问**: 无需登录即可访问
- **需要登录**: 需要有效的JWT令牌
- **需要管理员权限**: 需要管理员角色的用户才能访问

## 错误码说明

- `200`: 请求成功
- `400`: 请求参数错误
- `401`: 未授权访问
- `403`: 权限不足
- `404`: 资源未找到
- `500`: 服务器内部错误

## 使用示例

### 用户登录
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=password"
```

### 获取品牌列表
```bash
curl -X GET "http://localhost:8000/api/v1/brands/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 创建新相机
```bash
curl -X POST "http://localhost:8000/api/v1/cameras/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "EOS R5",
    "brand_id": 1,
    "mount_id": 1,
    "sensor_size": "全画幅"
  }'
```