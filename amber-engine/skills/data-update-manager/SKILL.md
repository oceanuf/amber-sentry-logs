---
name: data-update-manager
description: 管理琥珀引擎的所有数据更新任务，包括指数数据、ETF数据、宏观数据等。使用场景：当用户需要更新财经数据、管理自动化更新任务、检查数据更新状态、配置Cron作业或手动触发数据更新时。
---

# 数据更新管理器

## 概述

数据更新管理器是一个统一的Skill，用于管理琥珀引擎的所有数据更新任务。它提供了单一入口点来管理指数数据、ETF数据、宏观数据的更新，以及自动化Cron作业的配置。

## 核心功能

### 1. 统一数据更新
- **指数数据**: 沪深300、创业板指等核心指数
- **ETF数据**: 15只核心ETF的实时数据
- **宏观数据**: 人民币汇率、美债收益率、国际/国内金价
- **黄金数据**: 国际和国内黄金价格

### 2. 自动化管理
- **Cron作业配置**: 交易日15:00自动执行
- **手动触发**: 随时手动执行数据更新
- **状态检查**: 验证数据更新状态和最后更新时间

### 3. 数据验证
- **数据源验证**: Tushare Pro API状态检查
- **数据一致性**: 确保表格数据与缓存数据一致
- **更新时间**: 验证页面更新时间显示

## 使用场景

### 场景1: 手动触发数据更新
当用户说"更新数据"、"刷新数据"或"手动更新"时，执行完整的数据更新流程。

### 场景2: 检查数据更新状态
当用户说"检查数据状态"、"验证数据更新"或"查看最后更新时间"时，检查当前数据状态。

### 场景3: 配置自动化任务
当用户说"配置自动更新"、"设置Cron作业"或"管理定时任务"时，配置或修改自动化更新任务。

### 场景4: 故障排查
当用户说"数据没有更新"、"更新失败"或"检查问题"时，诊断数据更新问题。

## 工作流程

### 步骤1: 确定用户需求
- 询问用户需要执行的具体操作
- 提供选项：手动更新、状态检查、配置自动化、故障排查

### 步骤2: 执行相应操作

#### 选项A: 手动数据更新
```bash
# 进入工作目录
cd /home/luckyelite/.openclaw/workspace/amber-engine

# 运行统一数据引擎
python3 amber_unified_data_engine.py
```

**验证步骤**:
1. 检查引擎执行日志
2. 验证数据缓存更新时间
3. 检查页面数据显示
4. 确认表格更新时间已更新

#### 选项B: 数据状态检查
```bash
# 检查缓存更新时间
jq '.update_time' output/static/data/unified_data_cache.json

# 检查页面更新时间
grep -o "数据最后更新时间.*北京时间" output/index.html

# 检查表格更新时间
grep -o "table-update-time.*</span>" output/index.html

# 检查Tushare API状态
curl -s "http://api.tushare.pro" | head -5
```

#### 选项C: 配置自动化任务
```bash
# 检查现有Cron作业
openclaw cron list

# 创建/更新Cron作业
# 使用OpenClaw Cron API配置交易日15:00自动执行
```

#### 选项D: 故障排查
```bash
# 检查文件权限
ls -la output/index.html
ls -la output/static/data/unified_data_cache.json

# 检查Python环境
python3 --version
pip3 list | grep tushare

# 检查网络连接
curl -I https://api.tushare.pro

# 检查日志文件
tail -50 logs/amber_unified_data_engine.log
```

### 步骤3: 提供结果和下一步建议
- 总结执行结果
- 提供验证链接
- 建议下一步操作

## 技术架构

### 核心文件
```
amber-engine/
├── amber_unified_data_engine.py    # 统一数据引擎主文件
├── output/
│   ├── index.html                  # 首页HTML
│   └── static/data/
│       └── unified_data_cache.json # 数据缓存文件
├── output/etf/                     # ETF页面目录
└── scripts/                        # 辅助脚本目录
```

### 数据更新流程
1. **数据获取**: 从Tushare Pro API获取实时数据
2. **数据处理**: 格式化、计算涨跌幅、应用颜色类
3. **页面更新**: 更新HTML页面中的表格和卡片
4. **缓存保存**: 保存数据到JSON缓存文件
5. **时间更新**: 更新页面中的最后更新时间

### 自动化配置
- **Cron作业ID**: `262b7a44-98f0-491c-a164-da680a91cf42`
- **执行时间**: 交易日15:00 CST (北京时间)
- **执行命令**: `python3 amber_unified_data_engine.py`
- **工作目录**: `/home/luckyelite/.openclaw/workspace/amber-engine`

## 常见问题解决

### 问题1: 数据没有更新
**可能原因**:
1. Tushare API调用失败
2. 文件权限问题
3. 正则表达式匹配失败
4. 网络连接问题

**解决方案**:
```bash
# 检查API状态
python3 -c "import tushare as ts; print(ts.get_token())"

# 检查文件权限
sudo chown luckyelite:luckyelite output/index.html
sudo chmod 644 output/index.html

# 手动运行测试
python3 test_table_update.py
```

### 问题2: 表格显示异常
**可能原因**:
1. CSS样式加载失败
2. 表格结构被修改
3. 浏览器缓存问题

**解决方案**:
```bash
# 检查CSS文件
curl -I https://amber.googlemanager.cn:10123/static/css/amber-v2.2.min.css

# 验证表格结构
grep -n "index-data-table" output/index.html

# 强制浏览器刷新
# 建议用户使用Ctrl+F5强制刷新页面
```

### 问题3: 自动化任务未执行
**可能原因**:
1. Cron作业被禁用
2. 时间配置错误
3. 执行权限问题

**解决方案**:
```bash
# 检查Cron作业状态
openclaw cron list --includeDisabled=true

# 手动触发执行
openclaw cron run --jobId=262b7a44-98f0-491c-a164-da680a91cf42

# 检查系统Cron
crontab -l
```

## 最佳实践

### 1. 定期维护
- 每月检查Tushare Token状态
- 每周验证数据更新准确性
- 每日检查自动化任务执行日志

### 2. 监控告警
- 设置数据更新失败告警
- 监控API调用频率限制
- 跟踪页面访问状态

### 3. 备份策略
- 定期备份数据缓存文件
- 备份页面模板文件
- 备份Cron作业配置

### 4. 扩展建议
- 添加更多指数到表格
- 集成更多数据源
- 添加数据质量监控
- 实现数据异常检测

## 验证标准

### 数据更新成功标准
1. ✅ 统一数据引擎执行无错误
2. ✅ 数据缓存文件更新时间戳
3. ✅ 页面显示最后更新时间
4. ✅ 表格数据与缓存数据一致
5. ✅ 颜色类正确应用（红涨绿跌）

### 自动化任务成功标准
1. ✅ Cron作业配置正确
2. ✅ 交易日15:00自动执行
3. ✅ 执行日志记录完整
4. ✅ 无权限或网络错误

## 快速命令参考

### 手动更新
```bash
cd /home/luckyelite/.openclaw/workspace/amber-engine
python3 amber_unified_data_engine.py
```

### 状态检查
```bash
# 检查更新时间
grep -o "数据最后更新时间.*北京时间" output/index.html
grep -o "table-update-time.*</span>" output/index.html

# 检查数据
jq '.indices.沪深300.close' output/static/data/unified_data_cache.json
```

### 故障排查
```bash
# 检查权限
ls -la output/index.html

# 检查日志
tail -100 logs/amber_unified_data_engine.log

# 测试API
python3 -c "import tushare as ts; ts.set_token('YOUR_TOKEN'); print('API正常')"
```

### 自动化管理
```bash
# 列出Cron作业
openclaw cron list

# 运行Cron作业
openclaw cron run --jobId=262b7a44-98f0-491c-a164-da680a91cf42

# 检查运行历史
openclaw cron runs --jobId=262b7a44-98f0-491c-a164-da680a91cf42
```

## 联系信息

- **Skill名称**: 数据更新管理器
- **维护者**: Cheese Intelligence Team
- **创建日期**: 2026-03-20
- **版本**: 1.0.0
- **适用系统**: Ubuntu 24.02, OpenClaw

---

**使用提示**: 当用户需要管理琥珀引擎的数据更新时，自动触发此Skill。提供清晰的操作选项和验证步骤，确保数据更新的可靠性和准确性。