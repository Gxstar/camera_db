# 高级查询使用指南

本指南介绍如何使用相机镜头数据库系统的高级查询功能。

## 概述

新的查询系统提供了强大的多字段组合查询能力，支持：

- 🔍 **全文搜索** - 在多个字段中搜索关键词
- 🎯 **精确过滤** - 按具体条件筛选
- 📊 **范围查询** - 支持数值范围过滤
- 🏷️ **多值筛选** - 支持多个值的列表查询
- 📈 **灵活排序** - 按任意字段排序
- 📄 **分页查询** - 高效的分页支持

## 接口地址

- 相机查询: `GET /api/v1/cameras/query`
- 镜头查询: `GET /api/v1/lenses/query`

## 查询参数说明

### 基础参数

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `skip` | int | 跳过记录数 | `skip=20` |
| `limit` | int | 返回记录数(1-100) | `limit=10` |
| `sort_by` | string | 排序字段 | `sort_by=release_price` |
| `sort_order` | string | 排序方向(asc/desc) | `sort_order=desc` |
| `search` | string | 搜索关键词 | `search=Sony` |

### 列表参数

支持逗号分隔的多值查询：

| 参数 | 说明 | 示例 |
|------|------|------|
| `brand_ids` | 品牌ID列表 | `brand_ids=1,2,3` |
| `mount_ids` | 卡口ID列表 | `mount_ids=1,2` |
| `sensor_sizes` | 传感器尺寸列表 | `sensor_sizes=full_frame,aps_c` |

### 范围参数

支持最小值和最大值的范围查询：

| 参数 | 说明 | 示例 |
|------|------|------|
| `*_min` | 最小值 | `price_min=1000` |
| `*_max` | 最大值 | `price_max=5000` |

## 相机查询示例

### 1. 基础查询

```bash
# 查询前10个相机
GET /api/v1/cameras/query?limit=10

# 按价格降序排列
GET /api/v1/cameras/query?sort_by=release_price&sort_order=desc

# 跳过前20个，查询接下来的10个
GET /api/v1/cameras/query?skip=20&limit=10
```

### 2. 品牌和卡口过滤

```bash
# 查询佳能相机
GET /api/v1/cameras/query?brand_id=1

# 查询索尼和尼康相机
GET /api/v1/cameras/query?brand_ids=1,2

# 查询使用E卡口的相机
GET /api/v1/cameras/query?mount_id=3

# 查询佳能和索尼的全画幅相机
GET /api/v1/cameras/query?brand_ids=1,3&sensor_size=full_frame
```

### 3. 传感器和像素过滤

```bash
# 查询全画幅相机
GET /api/v1/cameras/query?sensor_size=full_frame

# 查询多种传感器尺寸
GET /api/v1/cameras/query?sensor_sizes=full_frame,aps_c

# 查询高像素相机
GET /api/v1/cameras/query?megapixels_min=30

# 查询特定像素范围
GET /api/v1/cameras/query?megapixels_min=20&megapixels_max=30
```

### 4. 价格和重量过滤

```bash
# 查询万元以下相机
GET /api/v1/cameras/query?price_max=10000

# 查询1-2万价格区间
GET /api/v1/cameras/query?price_min=10000&price_max=20000

# 查询轻便相机
GET /api/v1/cameras/query?weight_max=500

# 查询特定重量范围
GET /api/v1/cameras/query?weight_min=600&weight_max=800
```

### 5. 功能特性过滤

```bash
# 查询有WiFi的相机
GET /api/v1/cameras/query?has_wifi=true

# 查询有内置闪光灯的相机
GET /api/v1/cameras/query?has_built_in_flash=true

# 查询有热靴的相机
GET /api/v1/cameras/query?has_hot_shoe=true

# 查询有WiFi和蓝牙的相机
GET /api/v1/cameras/query?has_wifi=true&has_bluetooth=true
```

### 6. 搜索功能

```bash
# 搜索包含"R5"的相机
GET /api/v1/cameras/query?search=R5

# 搜索EOS系列
GET /api/v1/cameras/query?series=EOS

# 搜索特定型号
GET /api/v1/cameras/query?model=A7

# 搜索描述中的关键词
GET /api/v1/cameras/query?search=微单
```

### 7. 发布年份过滤

```bash
# 查询2020年后发布的相机
GET /api/v1/cameras/query?release_year_min=2020

# 查询特定年份范围
GET /api/v1/cameras/query?release_year_min=2018&release_year_max=2022
```

### 8. 复杂组合查询

```bash
# 查询索尼全画幅微单，价格1-2万
GET /api/v1/cameras/query?brand_id=3&sensor_size=full_frame&price_min=10000&price_max=20000

# 查询2020年后发布的轻便高像素相机
GET /api/v1/cameras/query?megapixels_min=30&weight_max=600&release_year_min=2020

# 查询佳能和尼康的APS-C相机，有WiFi，重量500克以下
GET /api/v1/cameras/query?brand_ids=1,2&sensor_size=aps_c&has_wifi=true&weight_max=500

# 搜索包含"5D"的相机，按发布年份降序
GET /api/v1/cameras/query?search=5D&sort_by=release_year&sort_order=desc
```

## 镜头查询示例

### 1. 基础查询

```bash
# 查询前10个镜头
GET /api/v1/lenses/query?limit=10

# 按焦距升序排列
GET /api/v1/lenses/query?sort_by=min_focal_length&sort_order=asc

# 按价格降序排列
GET /api/v1/lenses/query?sort_by=release_price&sort_order=desc
```

### 2. 镜头类型和对焦过滤

```bash
# 查询定焦镜头
GET /api/v1/lenses/query?lens_type=prime

# 查询变焦镜头
GET /api/v1/lenses/query?lens_type=zoom

# 查询自动对焦镜头
GET /api/v1/lenses/query?focus_type=auto

# 查询手动对焦定焦镜头
GET /api/v1/lenses/query?lens_type=prime&focus_type=manual
```

### 3. 焦距和光圈过滤

```bash
# 查询广角镜头
GET /api/v1/lenses/query?focal_length_max=35

# 查询长焦镜头
GET /api/v1/lenses/query?focal_length_min=100

# 查询标准变焦
GET /api/v1/lenses/query?focal_length_min=24&focal_length_max=70

# 查询大光圈镜头
GET /api/v1/lenses/query?aperture_min=1.4&aperture_max=2.8

# 查询恒定光圈变焦镜头
GET /api/v1/lenses/query?lens_type=zoom&is_constant_aperture=true
```

### 4. 功能特性过滤

```bash
# 查询带防抖的镜头
GET /api/v1/lenses/query?has_stabilization=true

# 查询轻便镜头
GET /api/v1/lenses/query?weight_max=400

# 查询特定滤镜口径
GET /api/v1/lenses/query?filter_size_min=77&filter_size_max=77
```

### 5. 复杂组合查询

```bash
# 查询索尼全画幅大光圈定焦
GET /api/v1/lenses/query?brand_id=3&lens_type=prime&aperture_min=1.8

# 查询万元内防抖变焦镜头
GET /api/v1/lenses/query?lens_type=zoom&has_stabilization=true&price_max=10000

# 查询2020年后发布的轻便定焦
GET /api/v1/lenses/query?lens_type=prime&weight_max=400&release_year_min=2020

# 查询24-70mm F2.8恒定光圈变焦镜头
GET /api/v1/lenses/query?focal_length_min=24&focal_length_max=70&aperture_min=2.8&aperture_max=2.8&is_constant_aperture=true
```

## 响应格式

查询接口返回统一的JSON格式：

```json
{
  "data": [
    {
      "id": 1,
      "model": "EOS R5",
      "brand_name": "Canon",
      "mount_name": "RF",
      "megapixels": 45.0,
      "release_price": 25999.0,
      "weight": 738.0,
      ...
    }
  ],
  "total": 150,
  "skip": 0,
  "limit": 20,
  "has_more": true
}
```

### 响应字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `data` | array | 查询结果数据 |
| `total` | int | 总记录数 |
| `skip` | int | 跳过的记录数 |
| `limit` | int | 返回记录数 |
| `has_more` | bool | 是否还有更多数据 |

## 前端集成示例

### JavaScript/TypeScript

```javascript
class CameraQueryAPI {
  constructor(baseURL = 'http://localhost:8000/api/v1') {
    this.baseURL = baseURL;
  }

  async queryCameras(params = {}) {
    const queryString = new URLSearchParams();
    
    // 处理基础参数
    if (params.skip) queryString.append('skip', params.skip);
    if (params.limit) queryString.append('limit', params.limit);
    if (params.sortBy) queryString.append('sort_by', params.sortBy);
    if (params.sortOrder) queryString.append('sort_order', params.sortOrder);
    if (params.search) queryString.append('search', params.search);
    
    // 处理过滤参数
    if (params.brandId) queryString.append('brand_id', params.brandId);
    if (params.brandIds) queryString.append('brand_ids', params.brandIds.join(','));
    if (params.sensorSize) queryString.append('sensor_size', params.sensorSize);
    if (params.megapixelsMin) queryString.append('megapixels_min', params.megapixelsMin);
    if (params.megapixelsMax) queryString.append('megapixels_max', params.megapixelsMax);
    if (params.priceMin) queryString.append('price_min', params.priceMin);
    if (params.priceMax) queryString.append('price_max', params.priceMax);
    
    const response = await fetch(`${this.baseURL}/cameras/query?${queryString}`);
    return await response.json();
  }

  // 查询示例
  async getCanonFullFrameCameras() {
    return this.queryCameras({
      brandId: 1,
      sensorSize: 'full_frame',
      sortBy: 'release_price',
      sortOrder: 'asc'
    });
  }

  async searchCameras(keyword, page = 0, pageSize = 20) {
    return this.queryCameras({
      search: keyword,
      skip: page * pageSize,
      limit: pageSize
    });
  }
}

// 使用示例
const api = new CameraQueryAPI();

// 查询索尼全画幅相机
api.queryCameras({
  brandId: 3,
  sensorSize: 'full_frame',
  limit: 10
}).then(result => {
  console.log('找到相机:', result.data.length);
  console.log('总数:', result.total);
});

// 搜索包含"微单"的相机
api.searchCameras('微单').then(result => {
  console.log('搜索结果:', result.data);
});
```

### React Hook示例

```jsx
import { useState, useEffect } from 'react';

function useCameraQuery(initialParams = {}) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [hasMore, setHasMore] = useState(false);

  const queryCameras = async (params = {}) => {
    setLoading(true);
    try {
      const queryString = new URLSearchParams({
        ...initialParams,
        ...params
      });
      
      const response = await fetch(`/api/v1/cameras/query?${queryString}`);
      const result = await response.json();
      
      setData(result.data);
      setTotal(result.total);
      setHasMore(result.has_more);
    } catch (error) {
      console.error('查询失败:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    queryCameras();
  }, []);

  return { data, loading, total, hasMore, queryCameras };
}

// 组件中使用
function CameraList() {
  const { data, loading, total, queryCameras } = useCameraQuery({
    limit: 20,
    sortBy: 'release_price',
    sortOrder: 'desc'
  });

  const handleFilterChange = (filters) => {
    queryCameras(filters);
  };

  if (loading) return <div>加载中...</div>;

  return (
    <div>
      <div>共 {total} 台相机</div>
      <CameraFilters onFilterChange={handleFilterChange} />
      <CameraGrid cameras={data} />
    </div>
  );
}
```

## 性能优化建议

1. **合理使用分页**: 避免一次查询过多数据，建议每页20-50条
2. **索引优化**: 确保常用查询字段有数据库索引
3. **缓存策略**: 对热门查询结果进行缓存
4. **延迟加载**: 大量数据时使用虚拟滚动或无限滚动
5. **查询简化**: 避免过于复杂的查询条件组合

## 常见问题

### Q: 如何查询多个品牌的相机？
A: 使用 `brand_ids` 参数，用逗号分隔：`brand_ids=1,2,3`

### Q: 如何进行模糊搜索？
A: 使用 `search` 参数，会在型号、系列和描述中搜索：`search=Sony`

### Q: 如何查询价格区间？
A: 使用 `price_min` 和 `price_max`：`price_min=10000&price_max=20000`

### Q: 如何按多个字段排序？
A: 目前支持单字段排序，如需多字段排序可在前端处理

### Q: 查询结果为空怎么办？
A: 检查查询条件是否过于严格，逐步放宽条件重试