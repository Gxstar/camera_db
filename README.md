# 相机数据库管理系统

一个用于管理相机设备、镜头和品牌的数据库系统。

## 项目结构

```
camera_db/
├── model/           # 数据模型
├── api/            # API接口
├── database/       # 数据库配置
├── alembic/        # 数据库迁移
└── main.py         # 主程序入口
```

## 模型关联关系

### 一对多关系

#### 品牌 ↔ 相机
- **关系**: 一个品牌可以拥有多个相机
- **品牌端**: `cameras: List["Camera"]`
- **相机端**: `brand_id: int` (外键，必需字段)
- **加载策略**: 品牌加载相机时使用 `joined` 策略

#### 品牌 ↔ 镜头
- **关系**: 一个品牌可以拥有多个镜头
- **品牌端**: `lenses: List["Lens"]`
- **镜头端**: `brand_id: int` (外键，必需字段)
- **加载策略**: 品牌加载镜头时使用 `joined` 策略

#### 卡口 ↔ 相机
- **关系**: 一个卡口可以对应多个相机，一个相机只能属于一个卡口
- **卡口端**: `cameras: List["Camera"]`
- **相机端**: `mount_id: int` (外键，必需字段)
- **加载策略**: 卡口加载相机时使用 `joined` 策略

#### 卡口 ↔ 镜头
- **关系**: 一个卡口可以对应多个镜头，一个镜头只能属于一个卡口
- **卡口端**: `lenses: List["Lens"]`
- **镜头端**: `mount_id: int` (外键，必需字段)
- **加载策略**: 卡口加载镜头时使用 `joined` 策略

### 多对多关系

#### 品牌 ↔ 卡口
- **关系**: 一个品牌可以拥有多个卡口，一个卡口也可以被多个品牌使用
- **示例**: 
  - 佳能品牌拥有 EF、RF 卡口
  - L卡口被徕卡、松下、适马等多个品牌使用
- **实现方式**: 通过关联表 `BrandMount` 实现真正的多对多关系
- **关联表字段**: 
  - `brand_id`: 品牌ID (外键)
  - `mount_id`: 卡口ID (外键)
  - `is_primary`: 是否为主要卡口
  - `compatibility_notes`: 兼容性说明

### 关系图
```
Brand (1) ←→ (N) Camera
   │
   ├── (N) Lens
   └── (N) Mount (1) ←→ (N) Camera
                │
                └── (N) Lens
```

## 模型字段说明

### 1. 用户模型 (User)

**文件**: `model/user.py`

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| id | int | ✅ | 主键ID |
| username | str | ✅ | 用户名 |
| email | str | ✅ | 邮箱地址 |
| password_hash | str | ✅ | 密码哈希 |
| role | UserRole | ✅ | 用户角色 |
| is_active | bool | ✅ | 是否激活 |
| created_at | datetime | ✅ | 创建时间 |
| updated_at | datetime | ✅ | 更新时间 |

**用户角色枚举 (UserRole)**:
- `USER`: 普通用户
- `ADMIN`: 管理员
- `EDITOR`: 编辑者
- `VIEWER`: 查看者

### 2. 品牌模型 (Brand)

**文件**: `model/brand.py`

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| id | int | ✅ | 主键ID |
| name | str | ✅ | 品牌名称 |
| country | Optional[str] | ❌ | 国家/地区 |
| founded_year | Optional[int] | ❌ | 成立年份 |
| website | Optional[str] | ❌ | 官方网站 |
| description | Optional[str] | ❌ | 品牌描述 |
| is_active | bool | ✅ | 是否在用 |
| created_at | datetime | ✅ | 创建时间 |
| updated_at | datetime | ✅ | 更新时间 |
| cameras | List[Camera] | ❌ | 相机列表 |
| lenses | List[Lens] | ❌ | 镜头列表 |

### 3. 相机模型 (Camera)

**文件**: `model/camera.py`

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| id | int | ✅ | 主键ID |
| brand_id | int | ✅ | 品牌外键 |
| brand | Brand | ❌ | 品牌对象 |
| mount_id | int | ✅ | 卡口外键 |
| mount | Mount | ❌ | 卡口对象 |
| sensor_size | Optional[SensorSize] | ❌ | 传感器尺寸 |
| series | Optional[str] | ❌ | 相机系列 |
| model | str | ✅ | 相机型号 |
| megapixels | Optional[float] | ❌ | 像素数量 |
| ibis_level | Optional[str] | ❌ | 机身防抖级别 |
| has_hot_shoe | bool | ✅ | 是否有热靴 |
| has_built_in_flash | bool | ✅ | 是否有内置闪光灯 |
| has_wifi | bool | ✅ | 是否有WiFi |
| has_bluetooth | bool | ✅ | 是否有蓝牙 |
| release_date | Optional[str] | ❌ | 发布日期 |
| release_price | Optional[float] | ❌ | 发布价格 |
| weight | Optional[float] | ❌ | 重量(克) |
| is_active | bool | ✅ | 是否在用 |
| description | Optional[str] | ❌ | 描述信息 |
| created_at | datetime | ✅ | 创建时间 |
| updated_at | datetime | ✅ | 更新时间 |

**传感器尺寸枚举 (SensorSize)**:
- `MEDIUM_FORMAT`: 中画幅
- `FULL_FRAME`: 全画幅
- `APS_C`: 半画幅
- `M43`: M43画幅
- `ONE_INCH`: 一英寸
- `OTHER`: 其他

### 4. 卡口模型 (Mount)

**文件**: `model/mount.py`

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| id | int | ✅ | 主键ID |
| name | str | ✅ | 卡口名称 |
| flange_distance | Optional[float] | ❌ | 法兰距(mm) |
| release_year | Optional[int] | ❌ | 发布年份 |
| is_active | bool | ✅ | 是否在用 |
| description | Optional[str] | ❌ | 备注说明 |
| created_at | datetime | ✅ | 创建时间 |
| updated_at | datetime | ✅ | 更新时间 |
| cameras | List[Camera] | ❌ | 相机列表 |
| lenses | List[Lens] | ❌ | 镜头列表 |
| brands | List[Brand] | ❌ | 支持品牌列表 |

### 5. 关联表模型 (BrandMount)

**文件**: `model/brand_mount.py`

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| brand_id | int | ✅ | 品牌ID (外键) |
| mount_id | int | ✅ | 卡口ID (外键) |
| is_primary | bool | ✅ | 是否为主要卡口 |
| compatibility_notes | str | ✅ | 兼容性说明 |
| brand | Brand | ❌ | 品牌对象 |
| mount | Mount | ❌ | 卡口对象 |

### 6. 镜头模型 (Lens)

**文件**: `model/lens.py`

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| id | int | ✅ | 主键ID |
| brand_id | int | ✅ | 品牌外键 |
| brand | Brand | ❌ | 品牌对象 |
| mount_id | int | ✅ | 卡口外键 |
| mount | Mount | ❌ | 卡口对象 |
| model | str | ✅ | 镜头型号 |
| series | Optional[str] | ❌ | 镜头系列 |
| min_focal_length | float | ✅ | 最小焦距(mm) |
| max_focal_length | float | ✅ | 最大焦距(mm) |
| lens_type | LensType | ✅ | 镜头类型 |
| max_aperture_min | float | ✅ | 最大光圈(最小焦距端) |
| max_aperture_max | Optional[float] | ❌ | 最大光圈(最大焦距端) |
| is_constant_aperture | bool | ✅ | 是否恒定光圈 |
| weight | Optional[float] | ❌ | 重量(克) |
| height | Optional[float] | ❌ | 高度(mm) |
| diameter | Optional[float] | ❌ | 直径(mm) |
| filter_size | Optional[float] | ❌ | 滤镜口径(mm) |
| focus_type | FocusType | ✅ | 对焦方式 |
| has_stabilization | bool | ✅ | 是否支持防抖 |
| min_focus_distance | Optional[float] | ❌ | 最近对焦距离(m) |
| magnification | Optional[float] | ❌ | 放大倍率 |
| release_date | Optional[str] | ❌ | 发布日期 |
| release_price | Optional[float] | ❌ | 发布价格(元) |
| is_active | bool | ✅ | 是否在用 |
| description | Optional[str] | ❌ | 备注说明 |
| created_at | datetime | ✅ | 创建时间 |
| updated_at | datetime | ✅ | 更新时间 |

**镜头类型枚举 (LensType)**:
- `ZOOM`: 变焦镜头
- `PRIME`: 定焦镜头

**对焦方式枚举 (FocusType)**:
- `AUTO`: 自动对焦
- `MANUAL`: 手动对焦

## 智能特性

### 自动判断逻辑

#### 镜头类型判断
- 当 `min_focal_length == max_focal_length` 时，自动设为 `PRIME` (定焦)
- 否则自动设为 `ZOOM` (变焦)

#### 恒定光圈判断
- 当 `max_aperture_min == max_aperture_max` 时，自动设为 `True` (恒定光圈)
- 否则自动设为 `False` (非恒定光圈)

## 数据库配置

- **数据库引擎**: SQLite (开发环境)
- **ORM框架**: SQLModel
- **迁移工具**: Alembic
- **连接配置**: `database/engine.py`

## API接口

### 可用接口
- `GET /api/users` - 获取用户列表
- `GET /api/brands` - 获取品牌列表
- `GET /api/cameras` - 获取相机列表
- `POST /api/cameras` - 创建相机
- `PUT /api/cameras/{id}` - 更新相机
- `DELETE /api/cameras/{id}` - 删除相机

## 安装和运行

1. 安装依赖:
```bash
uv sync
```

2. 初始化数据库:
```bash
# 生成初始迁移脚本
alembic revision --autogenerate -m "Initial migration"

# 执行数据库迁移
alembic upgrade head
```

3. 运行应用:
```bash
python main.py
```

## Alembic 数据库迁移命令

### 常用命令

- **查看当前迁移状态**:
```bash
alembic current
```

- **生成新的迁移脚本**:
```bash
alembic revision --autogenerate -m "描述信息"
```

- **执行迁移到最新版本**:
```bash
alembic upgrade head
```

- **回滚到上一个版本**:
```bash
alembic downgrade -1
```

- **回滚到特定版本**:
```bash
alembic downgrade <版本号>
```

- **查看迁移历史**:
```bash
alembic history
```

### 迁移流程

1. 修改模型文件后，生成迁移脚本：
```bash
alembic revision --autogenerate -m "添加新字段"
```

2. 检查生成的迁移脚本是否正确

3. 执行迁移：
```bash
alembic upgrade head
```

### 注意事项

- 迁移脚本会自动检测模型变化并生成相应的SQL语句
- 确保在生成迁移脚本前数据库表结构与模型定义一致
- 对于SQLite数据库，某些ALTER操作可能不支持，需要手动处理

## 开发说明

- 使用 SQLModel 进行数据库操作
- 支持数据库迁移
- 包含完整的API接口
- 支持用户权限管理
- 数据模型设计合理，扩展性强