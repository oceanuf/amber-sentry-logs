# 🔍 标的透视镜 (Assets)

## 📋 模组概述
**模组编号**: MOD-02  
**核心文件**: 518880_Gold.md, 512800_Bank.md  
**动态逻辑**: 注入 `database/nav_30d.json` (30日净值曲线)  
**状态**: 🟢 活跃

## 📁 文件清单

### 1. 黄金ETF (518880)
- **文件**: `518880_Gold.md`
- **标的代码**: 518880.SH
- **类型**: 黄金ETF
- **状态**: ✅ 持仓中

### 2. 银行ETF (512800)
- **文件**: `512800_Bank.md`
- **标的代码**: 512800.SH
- **类型**: 银行ETF
- **状态**: ✅ 持仓中

## 🔧 技术规范

### 数据挂载机制
标的详情使用"模版+数据注入"架构：

```markdown
# 518880 - 黄金ETF

## 📊 净值表现
[[VALUATION_ZONE]]

## 📈 技术指标
- 30日涨幅: {{30d_return}}%
- 年化波动率: {{annual_volatility}}%
```

### PHP数据注入
```php
// 数据注入逻辑
$asset_data = json_decode(file_get_contents('database/518880.json'), true);
$valuation_html = generate_valuation_table($asset_data);
$markdown = str_replace('[[VALUATION_ZONE]]', $valuation_html, $markdown);
```

## 📊 数据接口

### 1. 30日净值曲线
- **文件**: `database/nav_30d.json`
- **更新频率**: 每日闭市后
- **内容**: 各标的30日净值数据

### 2. 标的详情数据
- **文件**: `database/518880.json`, `database/512800.json`
- **更新频率**: 每日闭市后
- **内容**: 标的详细财务数据

### 3. 实时价格数据
- **文件**: `database/prices_live.json`
- **更新频率**: 15分钟
- **内容**: 实时价格与涨跌幅

## 🎨 视觉规范

### Obsidian暗色风格表格
```html
<table class="obsidian-dark">
  <thead>
    <tr>
      <th>日期</th>
      <th>单位净值</th>
      <th>日涨跌</th>
    </tr>
  </thead>
  <tbody>
    <!-- 动态生成行 -->
  </tbody>
</table>
```

### CSS样式
```css
.obsidian-dark {
  background: #1a1a1a;
  color: #d4d4d4;
  border: 1px solid #333;
}
.obsidian-dark th {
  background: #2d2d2d;
  color: #ffffff;
}
```

## 🚀 使用指南

### 查看标的详情
```markdown
查看黄金ETF: [[518880_Gold.md]]
查看银行ETF: [[512800_Bank.md]]
```

### 查看净值曲线
```markdown
查看30日净值: [[database/nav_30d.json#518880]]
```

## 📈 维护记录

| 日期 | 版本 | 变更内容 | 负责人 |
|------|------|----------|--------|
| 2026-03-28 | V1.0.0 | 模组初始化 | Cheese |
| 2026-03-28 | V1.0.1 | 实现数据挂载机制 | Cheese |

---

**最后更新**: 2026-03-28 16:06 GMT+8  
**维护团队**: Cheese Intelligence Team 🧀