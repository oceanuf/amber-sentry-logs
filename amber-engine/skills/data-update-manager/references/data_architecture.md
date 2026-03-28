# 数据架构参考

## 概述

琥珀引擎采用统一数据架构，所有数据通过单一脚本管理，确保数据一致性和可维护性。

## 数据流架构

```
Tushare Pro API
       ↓
统一数据引擎 (amber_unified_data_engine.py)
       ↓
数据缓存 (unified_data_cache.json)
       ↓
页面更新 (index.html, etf/*.html)
       ↓
用户访问 (https://amber.googlemanager.cn:10123/)
```

## 数据模块

### 1. 指数数据模块
**包含指数**:
- 沪深300 (000300.SH)
- 创业板指 (399006.SZ)

**数据结构**:
```json
{
  "沪深300": {
    "ts_code": "000300.SH",
    "trade_date": "20260320",
    "close": 4567.0179,
    "pct_chg": -0.3542,
    "pre_close": 4583.2511,
    "change": -16.2332,
    "vol": 254130449.0,
    "amount": 547850295.789,
    "data_source": "Tushare Pro",
    "status": "verified",
    "market": "A股",
    "weight": 0.5,
    "update_time": "2026-03-20 21:05:41"
  }
}
```

### 2. ETF数据模块
**包含ETF** (15只核心ETF):
1. 沪深300ETF (510300.SH)
2. 上证50ETF (510050.SH)
3. 中证500ETF (510500.SH)
4. 创业板ETF (159915.SZ)
5. 科创50ETF (588000.SH)
6. 券商ETF (512000.SH)
7. 银行ETF (512800.SH)
8. 消费ETF (159928.SZ)
9. 医药ETF (512010.SH)
10. 科技ETF (515000.SH)
11. 新能源车ETF (515030.SH)
12. 半导体ETF (512480.SH)
13. 军工ETF (512660.SH)
14. 红利ETF (510880.SH)
15. 黄金ETF (518880.SH)

**数据结构**:
```json
{
  "沪深300ETF": {
    "symbol": "510300.SH",
    "name": "沪深300ETF",
    "price": 4.567,
    "pct_chg": -0.35,
    "vol": 125000000,
    "amount_billion": 57.12,
    "trade_date": "20260320",
    "rich_score": 85.5,
    "source": "Tushare Pro"
  }
}
```

### 3. 宏观数据模块
**包含数据**:
1. 人民币汇率 (USD/CNY)
2. 美债10Y收益率
3. 国际金价 (XAUUSD)
4. 国内金价 (AU.SHF)

**数据结构**:
```json
{
  "人民币汇率": {
    "name": "人民币汇率",
    "symbol": "USDCNY.FX",
    "price": 6.88281,
    "pct_chg": 0.1153,
    "unit": "CNY",
    "source": "Tushare Pro"
  }
}
```

## 缓存文件结构

### unified_data_cache.json
```json
{
  "update_time": "2026-03-20 21:05:41",
  "indices": {
    "沪深300": {...},
    "创业板指": {...}
  },
  "etfs": {
    "沪深300ETF": {...},
    "上证50ETF": {...},
    ...
  },
  "macro": {
    "人民币汇率": {...},
    "美债10Y收益率": {...},
    "国际金价": {...},
    "国内金价": {...}
  },
  "system": {
    "last_run": "2026-03-20 21:05:41",
    "data_source": "Tushare Pro",
    "version": "3.2.7"
  }
}
```

## 页面更新机制

### 1. 表格更新
**目标文件**: `output/index.html`
**更新位置**: 指数数据表格 (`<table class="index-data-table">`)
**更新字段**:
- `col-price`: 最新点位
- `col-change`: 涨跌幅 + 颜色类

**正则表达式**:
```python
pattern = r'(data-index="沪深300".*?<td class="col-price">)[^<]*(</td>.*?<td class="col-change[^"]*">)[^<]*(</td>)'
```

### 2. 宏观四锚更新
**目标文件**: `output/index.html`
**更新位置**: 宏观四锚决策头 (`<div class="macro-anchor-content">`)
**更新字段**:
- `anchor-value`: 价格/数值
- `anchor-change`: 涨跌幅 + 颜色类

### 3. ETF页面更新
**目标文件**: `output/etf/index.html`
**更新位置**: ETF列表表格
**更新字段**: 所有ETF的价格和涨跌幅

### 4. 时间戳更新
**更新位置**:
1. 页面顶部: `数据最后更新时间`
2. 表格标题: `table-update-time`
3. ETF页面: `数据更新时间`

## 颜色系统

### 中国金融市场习惯
- **红色 (`price-up`, `change-up`)**: 上涨
- **绿色 (`price-down`, `change-down`)**: 下跌
- **中性 (`change-neutral`)**: 无变化或未知

### CSS类名
```css
.price-up { color: #f44336; }  /* 红色 - 上涨 */
.price-down { color: #4caf50; } /* 绿色 - 下跌 */

.change-up { color: #f44336; }
.change-down { color: #4caf50; }
.change-neutral { color: #666; }
```

### 应用规则
1. **指数数据**: `pct_chg > 0` → `price-up`, 否则 `price-down`
2. **宏观数据**: `pct_chg > 0` → `change-up`, 否则 `change-down`
3. **ETF数据**: 同指数数据规则

## 错误处理机制

### 五级降级保障
1. **主数据源**: Tushare Pro API
2. **备用数据源**: 免费Tushare接口
3. **第三方数据源**: AkShare
4. **缓存数据**: 上次成功获取的数据
5. **静态数据**: 预设的默认数据

### 错误处理策略
```python
try:
    # 尝试主数据源
    data = fetch_from_tushare_pro()
except Exception as e:
    logger.warning(f"主数据源失败: {e}")
    try:
        # 尝试备用数据源
        data = fetch_from_tushare_free()
    except Exception as e:
        logger.warning(f"备用数据源失败: {e}")
        # 使用缓存数据
        data = load_from_cache()
```

## 性能优化

### 1. 缓存策略
- **数据缓存**: 24小时有效
- **页面缓存**: 浏览器缓存控制
- **API缓存**: 避免重复请求

### 2. 批量更新
- 所有数据一次性获取
- 所有页面一次性更新
- 减少文件I/O操作

### 3. 增量更新
- 只更新变化的数据
- 只修改必要的HTML部分
- 减少正则表达式匹配范围

## 扩展性设计

### 1. 表格扩展
**添加新指数**:
1. 在表格中添加新行
2. 更新`update_regular_cards`方法
3. 添加数据获取逻辑

### 2. 数据源扩展
**添加新数据源**:
1. 实现新的数据获取方法
2. 集成到统一数据引擎
3. 更新错误处理链

### 3. 页面扩展
**添加新页面**:
1. 创建新模板文件
2. 添加数据更新方法
3. 配置路由和访问权限

## 监控指标

### 1. 数据质量指标
- **数据完整性**: 所有字段是否齐全
- **数据准确性**: 与权威数据源对比
- **数据及时性**: 更新时间间隔

### 2. 系统性能指标
- **API响应时间**: Tushare API调用耗时
- **页面生成时间**: HTML更新耗时
- **缓存命中率**: 缓存使用效率

### 3. 业务指标
- **用户访问量**: 页面访问统计
- **数据更新频率**: 更新成功次数
- **错误率**: 更新失败比例

## 维护指南

### 日常维护
1. **检查数据更新**: 每日验证数据准确性
2. **监控错误日志**: 检查更新失败记录
3. **备份数据缓存**: 定期备份缓存文件

### 定期维护
1. **更新API Token**: 每月检查Tushare Token状态
2. **清理日志文件**: 每周清理旧日志
3. **验证自动化任务**: 每月检查Cron作业

### 应急处理
1. **数据更新失败**: 手动触发更新，检查错误日志
2. **页面显示异常**: 检查CSS加载，验证HTML结构
3. **API限制触发**: 切换数据源，等待限制解除

## 版本历史

### v3.2.7 (当前)
- 表格形式展示指数数据
- 统一数据引擎优化
- 五级降级保障机制
- 自动化Cron作业配置

### v3.2.4
- 视觉归位紧急补丁
- 卡片高度标准化
- 响应式布局优化

### v3.2.3
- 外网访问战略部署
- 宏观双锚真实数据接入
- 数据归一化核心引擎

### v2.2
- 晨报视觉系统
- 琥珀色品牌标识
- 响应式设计优化

## 联系信息

- **架构设计**: Cheese Intelligence Team
- **数据源**: Tushare Pro
- **最后更新**: 2026-03-20
- **版本**: 3.2.7
- **状态**: 生产环境运行中