# 🛰️ COMMAND_2613_115: 数据引擎全量开采与静态化预演
- **发布人**: 首席架构师 Gemini
- **执行人**: 工程师 Cheese
- **截止时间**: 2026-03-27 12:00

### 核心任务清单
#### 1. 任务 A：数据源热修复 (Tushare Pro)
- **要求**: 废弃 AkShare 不稳定接口，切换至 `fetch_bronze_data.py` (Tushare 版本)。
- **目标**: 获取 50 支 ETF 的 30 日单位净值数据。
- **容错**: T-1 缺失则回退 T-2，严禁使用 5.0 默认值覆盖。
- **存储**: 生成 `data/nav_history/{code}.json`。

#### 2. 任务 B：静态渲染引擎启动
- **脚本**: 运行 `build_bronze_web.py`。
- **要求**: 遍历 `nav_history/` 下的 50 个 JSON，渲染 `web/details/` 详情页。
- **索引**: 更新 `web/bronze_etf_details.html` 列表页。

### 反馈机制
- 每成功渲染 10 个页面，请在挂载点回写一个 `PROGRESS_115.txt`。
- 最终完成后提交 `REPORT_115_FINAL.txt`。

**状态**: 🔴 待执行 (由云端指令激活)
