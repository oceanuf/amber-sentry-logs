# 🗄️ Amber-Vault 数据库配置报告

## 配置信息
- **配置时间**: 2026-03-18 20:10:34
- **数据库路径**: /home/luckyelite/.openclaw/workspace/amber-engine/amber_vault.db
- **设计目标**: 低频数据缓存，优化API额度使用

## 表结构设计

### 1. fund_portfolio_cache (基金持仓缓存)
**更新频率**: 7天/次 (基金持仓每季度更新)
**字段设计**:
- ts_code: 基金代码
- ann_date: 公告日期
- end_date: 报告期
- symbol: 股票代码
- mkv: 持仓市值(万元)
- amount: 持仓数量(万股)
- stk_mkv_ratio: 占股票市值比
- mkv_ratio: 占净值比例
- update_time: 更新时间戳

**索引策略**:
- 主键: (ts_code, end_date, symbol) 唯一约束
- 查询索引: 基金代码、报告期、股票代码

### 2. api_quota_log (API额度日志)
**监控维度**:
- API名称、请求次数、数据行数
- 响应时间、剩余额度估计
- 请求时间、状态

### 3. data_update_schedule (数据更新计划)
**智能调度**:
- 数据类型、更新频率(daily/weekly/monthly)
- 最后更新时间、下次计划时间
- 估计数据行数、API调用成本
- 启用状态、描述

### 4. cache_statistics (缓存统计)
**性能监控**:
- 缓存类型、总数据行数
- 最后更新时间、命中次数
- 未命中次数、平均响应时间
- 存储大小

## 缓存策略

### 高频数据 (每日更新)
- index_daily: 指数日线行情
- index_dailybasic: 指数估值数据
- fund_daily: ETF日线数据
- moneyflow_hsgt: 北向资金数据

### 低频数据 (7天缓存)
- fund_portfolio: 基金持仓数据 (核心节省点)
- stk_holdernumber: 股东人数数据

## API额度优化计算

### 当前配置节省:
```
fund_portfolio: 1次/天 → 1次/7天 (节省6次/周)
stk_holdernumber: 1次/天 → 1次/7天 (节省6次/周)
总计节省: 12次/周 = 48次/月
```

### 实际业务价值:
- **额度释放**: 将节省的API额度用于高频行情数据
- **数据质量**: 低频数据缓存确保数据一致性
- **系统稳定**: 避免因额度耗尽导致的数据中断

## 集成方案

### 数据流设计:
```
Tushare API → Amber-Vault缓存 → 业务查询
      ↓             ↓
  原始数据       缓存数据
      ↓             ↓
  高频更新       低频更新
      ↓             ↓
实时性优先      节省额度优先
```

### 查询逻辑:
```python
def get_fund_portfolio(ts_code, use_cache=True):
    if use_cache:
        # 先查询缓存
        cached_data = query_cache('fund_portfolio', ts_code)
        if cached_data and not is_cache_expired(cached_data):
            return cached_data
    
    # 缓存不存在或已过期，调用API
    fresh_data = call_tushare_api('fund_portfolio', ts_code)
    
    # 更新缓存
    update_cache('fund_portfolio', ts_code, fresh_data)
    
    return fresh_data
```

## 运维监控

### 监控指标:
1. **缓存命中率**: 目标 > 80%
2. **API调用次数**: 每日统计和预警
3. **数据新鲜度**: 缓存数据更新时间
4. **存储空间**: 数据库文件大小监控

### 告警规则:
- 缓存命中率 < 60%: 警告
- API调用超每日限额80%: 警告
- 数据更新失败: 紧急告警
- 存储空间 > 1GB: 警告

## 部署说明

### 初始化步骤:
1. 运行本脚本创建数据库结构
2. 初始化数据更新计划
3. 配置定时任务执行缓存更新
4. 集成到琥珀引擎查询逻辑

### 维护任务:
- 每日: 检查缓存命中率和API使用
- 每周: 清理过期缓存数据
- 每月: 分析缓存效果和优化策略

---
*配置时间: 2026-03-18 20:10:34*
*Amber-Vault 缓存系统*
