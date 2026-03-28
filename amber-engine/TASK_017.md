# 📜 琥珀引擎：代码重构任务书 [2613-017]

## 1. 公文摘要
- **发布人**：首席架构师 Gemini
- **执行人**：顶级工程师 Cheese
- **审批人**：主编 Haiyang
- **生效时间**：2026-03-25 10:00 (UTC+8)
- **核心目标**：彻底废除模拟数据，建立【Tushare Pro / AkShare / Crawler】三梯队影子验伪系统。

---

## 2. 核心架构：三梯队数据对冲获取协议 (Shadow-Benchmarking)

Cheese，请重构 `fetch_global_raw_v3.py`。严禁使用 `random` 生成模拟数据，必须遵循以下逻辑死循环：

### **执行优先级与验伪逻辑**：
1. **[Tier 1] Tushare Pro (真值锚点)**:
 - 优先调用 Tushare 接口。若成功，该标的数据作为本轮审计的"真值"。
2. **[Tier 2] AkShare (影子验证)**:
 - 若 Tushare 缺失某 ETF 数据，启动 AkShare。
 - **验伪锁**: 必须同时用 AkShare 抓取一支 Tushare 已有的标的（如 `510300.SH`）。
 - **比对公式**: `diff = abs(Ak_Price - Tu_Price) / Tu_Price`。
 - **阈值**: `diff < 0.001` (0.1%) 则通过，否则判定 AkShare 今日不可信。
3. **[Tier 3] Crawler (救急抓取)**:
 - 逻辑同 Tier 2，必须通过与 Tier 1 的影子比对验证。
4. **[Final Fallback]**: 
 - 三级全部失效或验伪未通过，返回 `DATA_UNAVAILABLE`。**禁止填充任何伪造数据。**

---

## 3. 技术重构细节 (Refactoring Requirements)

### **A. 逻辑清创**
- **彻底物理删除** 脚本中所有涉及 `generate_simulated_data` 或 `fallback_to_random` 的函数。
- 确保审计报告中的 `data_quality` 标签仅包含：`TUSHARE` / `AKSHARE_VERIFIED` / `CRAWLER_VERIFIED`。

### **B. 全局握手测试 (Global Handshake)**
- 在脚本启动的前 5 秒，执行一次"三源对撞测试"。
- 若 AkShare 在对撞测试中误差超标，立即全局禁用 Tier 2，避免后续 19 支标的重复执行无效验证。

### **C. 严格日期对齐**
- 比对数据时，必须检查 `trade_date` 字段。严禁用"今日收盘价"对比"昨日净值"。

### **D. 环境隔离**
- Tushare Token 必须从 `.env` 加载，禁止硬编码。

---

## 4. 协同与汇报规范 (ACK Protocol)

1. **执行模式**: `python3 -u fetch_global_raw_v3.py | tee -a /proc/1/fd/1`。
2. **节点确认**: 完成代码编写后，请在会话中回复：`[Node Verified: 17.1 - 源码已重构]`。
3. **验伪报告**: 第一次成功运行后，请贴出：`[Shadow Check Pass: 510300, Diff: 0.0004]`。

---

## 5. 监察官声明
主编已授权。Cheese，我们要的是绝对真实的引力场，逻辑不容许 0.1% 以外的模糊。

**"数据即生命，验伪即尊严。开始重构。"**