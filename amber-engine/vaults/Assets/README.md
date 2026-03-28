# 🔍 标的透视镜 (Assets)

## 📋 模组概述
**模组编号**: MOD-02 (全量标的扩建工程)  
**核心文件**: 518880_Gold.md, 512800_Bank.md, 510300_Index.md  
**动态逻辑**: PHP动态注入 `database/*.json` 数据  
**状态**: 🟢 活跃 (MOD-02架构已部署)

## 🚀 快速导航

### 📊 持仓清单 (基于[2613-196号]表格标准)
<table style="width:100%; border-collapse: collapse; background: #24283b;">
<thead>
<tr style="border-bottom: 2px solid #414868; color: #7aa2f7;">
<th>标的</th><th>份额</th><th>策略</th><th>持有进度</th>
</tr>
</thead>
<tbody>
<tr style="border-bottom: 1px solid #414868;">
<td style="padding: 12px 16px;"><a href="?etf=518880_Gold">🥇 黄金ETF (518880)</a></td>
<td style="padding: 12px 16px; text-align: center;">35%</td>
<td style="padding: 12px 16px;">Gravity-Dip</td>
<td style="padding: 12px 16px;"><span style="color: #9ece6a;">▓▓▓▓▓▓▓▓░░</span> 80%</td>
</tr>
<tr style="border-bottom: 1px solid #414868;">
<td style="padding: 12px 16px;"><a href="?etf=512800_Bank">🏦 银行ETF (512800)</a></td>
<td style="padding: 12px 16px; text-align: center;">65%</td>
<td style="padding: 12px 16px;">Bias-RSI</td>
<td style="padding: 12px 16px;"><span style="color: #9ece6a;">▓▓▓▓▓▓▓▓▓▓</span> 100%</td>
</tr>
</tbody>
</table>

### 👀 观察标的  
- **[📊 沪深300ETF (510300)](?etf=510300_Index)** - 观察中

## 📁 文件清单

<table style="width:100%; border-collapse: collapse; background: #24283b; margin: 20px 0;">
<thead>
<tr style="border-bottom: 2px solid #414868; color: #7aa2f7;">
<th>标的</th><th>文件</th><th>代码</th><th>类型</th><th>状态</th><th>策略</th><th>访问</th>
</tr>
</thead>
<tbody>
<tr style="border-bottom: 1px solid #414868;">
<td style="padding: 10px 12px;">🥇 黄金ETF</td>
<td style="padding: 10px 12px; font-family: monospace;">518880_Gold.md</td>
<td style="padding: 10px 12px; font-family: monospace;">518880.SH</td>
<td style="padding: 10px 12px;">黄金ETF</td>
<td style="padding: 10px 12px; color: #9ece6a;">✅ 持仓中</td>
<td style="padding: 10px 12px;">Gravity-Dip</td>
<td style="padding: 10px 12px;"><a href="?etf=518880_Gold">访问</a></td>
</tr>
<tr style="border-bottom: 1px solid #414868;">
<td style="padding: 10px 12px;">🏦 银行ETF</td>
<td style="padding: 10px 12px; font-family: monospace;">512800_Bank.md</td>
<td style="padding: 10px 12px; font-family: monospace;">512800.SH</td>
<td style="padding: 10px 12px;">银行ETF</td>
<td style="padding: 10px 12px; color: #9ece6a;">✅ 持仓中</td>
<td style="padding: 10px 12px;">Bias-RSI</td>
<td style="padding: 10px 12px;"><a href="?etf=512800_Bank">访问</a></td>
</tr>
<tr style="border-bottom: 1px solid #414868;">
<td style="padding: 10px 12px;">📊 沪深300ETF</td>
<td style="padding: 10px 12px; font-family: monospace;">510300_Index.md</td>
<td style="padding: 10px 12px; font-family: monospace;">510300.SH</td>
<td style="padding: 10px 12px;">宽基指数ETF</td>
<td style="padding: 10px 12px; color: #e0af68;">👀 观察中</td>
<td style="padding: 10px 12px;">Core-Hold</td>
<td style="padding: 10px 12px;"><a href="?etf=510300_Index">访问</a></td>
</tr>
</tbody>
</table>

## 🔧 技术规范 (MOD-02架构)

### 三位一体架构
```
Markdown模板 (视图层) ← PHP动态注入 → JSON数据 (数据层)
```

### 1. 数据层 (JSON火药库)
```json
// database/518880.json
{
  "ticker": "518880",
  "current_price": 5.012,
  "change_pct": "+0.05%",
  "nav_history": [...],  // 30日净值序列
  "position_data": {...} // 持仓数据
}
```

### 2. 视图层 (MD模板)
```markdown
---
TICKER: "518880"
NAME: "华安黄金ETF"
---

# 🥇 518880 - 黄金ETF

## 📊 净值表现
[[VALUATION_ZONE]]  <!-- 动态注入锚点 -->
```

### 3. 引擎层 (PHP动态渲染)
```php
// 检测并注入动态内容
function inject_dynamic_content($markdown) {
    if (strpos($markdown, '[[VALUATION_ZONE]]') !== false) {
        $ticker = extract_ticker_from_yaml($markdown);
        $table_html = generate_dynamic_table($ticker);
        return str_replace('[[VALUATION_ZONE]]', $table_html, $markdown);
    }
    return $markdown;
}
```

## 📊 数据接口 (MOD-02标准化)

### 1. 标的JSON数据矩阵
| 文件 | 标的 | 更新频率 | 内容 |
|------|------|----------|------|
| `database/518880.json` | 黄金ETF | 每小时 | 价格、涨跌幅、30日净值、持仓数据 |
| `database/512800.json` | 银行ETF | 每小时 | 价格、涨跌幅、30日净值、持仓数据 |
| `database/510300.json` | 沪深300ETF | 每小时 | 价格、涨跌幅、30日净值、观察数据 |

### 2. 自动化更新流水线
```python
# rebuild_minimalist.py 中的批量更新函数
def update_all_assets_json(portfolio):
    etf_list = ["518880", "512800", "510300"]
    for ticker in etf_list:
        update_asset_json(ticker, portfolio)
```

### 3. 数据源验证
- **优先源**: Tushare Pro (真值锚点)
- **备用源**: AkShare (影子验证)
- **验证逻辑**: 0.1%精度验伪，失败则全局禁用

## 🎨 视觉规范 (MOD-02标准化)

### 1. 表格样式强制规范
```html
<table style="width: 100%; border-collapse: collapse; font-family: monospace; 
              background: #1a1b26; color: #c0caf5; border-radius: 8px;">
  <!-- 动态生成内容 -->
</table>
```

### 2. 涨跌颜色逻辑
```php
// PHP动态颜色判断
$change_color = '#9ece6a'; // 绿色 (涨幅)
if (strpos($change_pct, '-') === 0) {
    $change_color = '#f7768e'; // 红色 (跌幅)
}
```

### 3. Obsidian深色主题融合
- **背景色**: `#1a1b26` (Obsidian默认暗色背景)
- **文字色**: `#c0caf5` (Obsidian默认文字颜色)
- **强调色**: `#9ece6a` (绿色) / `#f7768e` (红色)
- **边框色**: `#414868` (Obsidian边框颜色)

### 4. 响应式设计
- **宽度**: `100%` (禁止内容挤压)
- **字体**: `monospace` (确保数值对齐)
- **溢出**: `overflow-x: auto` (小屏幕滚动)

## 🚀 使用指南 (MOD-02架构)

### 1. Web访问
- **黄金ETF**: https://gemini.googlemanager.cn:10168/?etf=518880_Gold
- **银行ETF**: https://gemini.googlemanager.cn:10168/?etf=512800_Bank  
- **沪深300ETF**: https://gemini.googlemanager.cn:10168/?etf=510300_Index

### 2. 自动化更新
```bash
# 每15分钟自动更新演武场和ETF数据
*/15 * * * * cd /home/luckyelite/.openclaw/workspace/amber-engine/scripts && python3 rebuild_minimalist.py
```

### 3. 数据验证
```bash
# 手动触发数据更新
cd /home/luckyelite/.openclaw/workspace/amber-engine/scripts
python3 -c "from rebuild_minimalist import update_all_assets_json, load_portfolio; portfolio = load_portfolio(); update_all_assets_json(portfolio)"
```

## 📈 维护记录 (MOD-02里程碑)

| 日期 | 版本 | 变更内容 | 负责人 |
|------|------|----------|--------|
| 2026-03-28 | V1.0.0 | 模组初始化 | Cheese |
| 2026-03-28 | V1.0.1 | 实现数据挂载机制 | Cheese |
| 2026-03-28 | **V2.0.0** | **MOD-02 ETF标标活化工程完成** | **Cheese** |
| 2026-03-28 | **V2.1.0** | **MOD-02全量标的扩建工程完成** | **Cheese** |

### 🎯 MOD-02工程成果
1. ✅ **数据火药库**: 建立 `database/*.json` 结构化数据矩阵
2. ✅ **模板标准化**: 518880_Gold.md, 512800_Bank.md, 510300_Index.md
3. ✅ **动态注入引擎**: PHP实现零JS动态渲染
4. ✅ **视觉标准化**: Obsidian深色主题完美融合
5. ✅ **自动化流水线**: 批量更新 + 健康检查 + GitHub同步

---

**最后更新**: 2026-03-28 17:50 GMT+8  
**维护团队**: Cheese Intelligence Team 🧀  
**工程状态**: ✅ **MOD-02全量标的扩建工程完成**