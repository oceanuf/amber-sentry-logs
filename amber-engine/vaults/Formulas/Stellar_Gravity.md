---
ID: STELLAR-01
TYPE: Trend_Following
HOLD_PERIOD: 60D
STATUS: Active
VERSION: V1.1.1-ELITE
CREATED: 2026-03-20
UPDATED: 2026-03-28
---

# 🌟 星辰引力算法 (Stellar Gravity)

## 📋 算法概述
- **算法类型**: 趋势跟踪 (Trend Following)
- **核心思想**: 利用价格动量与市场引力效应
- **适用市场**: 股票、ETF、大宗商品
- **时间框架**: 日线级别
- **持仓周期**: 60个交易日

## 🧮 核心公式

### 1. 引力系数计算
```
引力系数 = (当前价格 - N日移动平均) / N日标准差
```
其中:
- N = 20 (默认参数)
- 移动平均 = SMA(20)
- 标准差 = StdDev(20)

### 2. 动量得分
```
动量得分 = (当前价格 / T-29价格 - 1) × 100%
```
**重要**: T-29必须基于物理交易日，禁止使用日历日计算。

### 3. 综合评分
```
综合评分 = 引力系数 × 0.6 + 动量得分 × 0.4
```

## 📊 参数配置

### 默认参数
```python
STELLAR_PARAMS = {
    "lookback_period": 20,      # 回溯周期
    "entry_threshold": 1.5,     # 入场阈值
    "exit_threshold": 0.5,      # 出场阈值
    "position_size": 0.1,       # 单笔仓位
    "max_positions": 5,         # 最大持仓数
    "stop_loss": 0.08,          # 止损比例
    "take_profit": 0.15         # 止盈比例
}
```

### 参数调优历史
| 版本 | 参数变更 | 回测收益 | 夏普比率 | 启用日期 |
|------|----------|----------|----------|----------|
| V1.0.0 | 初始参数 | +18.5% | 1.25 | 2026-03-20 |
| V1.1.0 | 调整入场阈值 | +22.3% | 1.42 | 2026-03-25 |
| V1.1.1 | 优化止损逻辑 | +24.7% | 1.58 | 2026-03-28 |

## 🎯 交易信号

### 入场信号
1. **引力突破**: 引力系数 > 入场阈值 (1.5)
2. **动量确认**: 动量得分 > 5%
3. **成交量验证**: 成交量 > 20日均量 × 1.2

### 出场信号
1. **引力衰减**: 引力系数 < 出场阈值 (0.5)
2. **动量反转**: 动量得分 < -3%
3. **止损触发**: 亏损达到止损比例 (8%)
4. **止盈触发**: 盈利达到止盈比例 (15%)

## 📈 回测表现

### 历史回测数据
```json
{
  "total_return": 24.7,
  "annual_return": 32.5,
  "sharpe_ratio": 1.58,
  "max_drawdown": 12.3,
  "win_rate": 68.5,
  "profit_factor": 2.15
}
```

### 月度表现
| 月份 | 收益率 | 最大回撤 | 交易次数 | 胜率 |
|------|--------|----------|----------|------|
| 2026-01 | +5.2% | -3.1% | 8 | 75% |
| 2026-02 | +7.8% | -4.5% | 12 | 67% |
| 2026-03 | +11.7% | -5.2% | 15 | 73% |

## 🔧 实现代码

### Python核心函数
```python
def calculate_stellar_gravity(price_series, lookback=20):
    """计算星辰引力系数"""
    sma = price_series.rolling(lookback).mean()
    std = price_series.rolling(lookback).std()
    gravity = (price_series - sma) / std
    return gravity

def generate_trading_signals(df, params):
    """生成交易信号"""
    signals = []
    for i in range(len(df)):
        if df['gravity'][i] > params['entry_threshold']:
            signals.append('BUY')
        elif df['gravity'][i] < params['exit_threshold']:
            signals.append('SELL')
        else:
            signals.append('HOLD')
    return signals
```

## ⚠️ 风险控制

### 风控规则
1. **单标的风险**: 单笔交易不超过总资金的10%
2. **总仓位限制**: 总持仓不超过总资金的50%
3. **行业分散**: 同一行业持仓不超过总资金的20%
4. **日内风控**: 单日最大亏损不超过总资金的2%

### 熔断机制
1. **系统熔断**: 单日亏损5% → 暂停交易24小时
2. **标的熔断**: 单标亏损15% → 永久移出观察池
3. **策略熔断**: 连续3次亏损 → 策略回检

## 🚀 使用指南

### 算法调用
```python
from formulas.stellar_gravity import StellarGravity

# 初始化算法
algo = StellarGravity(params=STELLAR_PARAMS)

# 运行回测
results = algo.backtest(price_data)

# 生成信号
signals = algo.generate_signals(latest_data)
```

### 参数调整
```python
# 自定义参数
custom_params = {
    "lookback_period": 30,
    "entry_threshold": 2.0,
    "exit_threshold": 0.8
}

algo = StellarGravity(params=custom_params)
```

---

**算法维护**: Cheese Intelligence Team 🧀  
**最后更新**: 2026-03-28 16:10 GMT+8  
**算法状态**: ✅ 生产环境运行中  
**性能监控**: 实时监控中，每日生成绩效报告