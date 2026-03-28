# 琥珀引擎核心执行准则 (Perpetual Memory Execution Rules)

## 1. 核心加权矩阵 (V4.1 主编审计版)
> **强制约束**：所有 ETF 评分逻辑必须严格对齐以下权重。严禁私自提升 Performance (S_D) 权重以诱导激进投资。

| 维度代码 | 维度名称 | 审计权重 (Weight) | 核心关注点 |
| :--- | :--- | :--- | :--- |
| **S_D_Performance** | 基金表现 | **0.30** | 超额收益 (Alpha) |
| **S_A_Liquidity** | 流动性 | **0.25** | 日均成交额 > 1000万 |
| **S_C_Cost** | 费率成本 | **0.20** | 管理+托管费 < 0.6% |
| **S_B_Correlation** | 相关性 | **0.125** | 指数跟踪误差 |
| **S_E_Management** | 管理模式 | **0.125** | 量化增强属性 |

---

## 2. 计算公式与归一化逻辑
计算结果必须强制从 10 分制映射至 100 分制，严禁出现 V4.0 版本的溢出错误。
$$Score_{final} = \sum (Dimension\_Score_{10} \times Weight) \times 10$$

## 3. 主编审计水印 (Auditor Watermark)
任何生产环境生成的 `results.json` 或 `report.html`，其 `executor` 字段必须包含：
`工程师 Cheese (Audited by Chief)`
**若缺失此后缀，则视为无效分析，禁止进入 Amber-Grid 前端展示。**

## 4. 资产池白名单 (TARGET_ETFS)
严禁在脚本运行时静默清空 `TARGET_ETFS`。分析器必须覆盖以下三大核心主题：
1. **科技自立** (512480, 588000等)
2. **绿色转型** (516160, 159857等)
3. **安全韧性** (518880, 512660等)

---
*Last Updated: 2026-03-22*
*Status: CRITICAL - MANDATORY EXECUTION*

---
## 5. [MANDATORY] 琥珀引擎原子化打分 Skill (V4.1-AUDIT)
> **协议声明**：本 Skill 是系统中唯一合法的计算逻辑。工程师 Cheese 必须且只能通过此 Skill 进行 ETF 评分。

### 5.1 Skill 输入规范 (Input Schema)
所有传入此 Skill 的数据必须符合以下结构（10分制原始数据）：
- `p_raw`: Performance (业绩分)
- `l_raw`: Liquidity (流动性分)
- `c_raw`: Cost (成本分)
- `b_raw`: Correlation (跟踪分)
- `m_raw`: Management (管理分)

### 5.2 Skill 计算核心 (Atomic Logic)
本 Skill 内部强制执行以下公式，严禁外部干预：
`Final_Score = (p_raw*0.30 + l_raw*0.25 + c_raw*0.20 + b_raw*0.125 + m_raw*0.125) * 10`

### 5.3 运行准则 (Enforcement)
1. **禁止计算**：Cheese 编写的任何 `.py` 或 `.js` 脚本中，严禁出现任何关于 ETF 分值的数学运算符号。
2. **唯一性**：所有展示在 Amber-Grid 的分值必须附带 Skill 生成的 `audit_hash`（由输入数据和主编私钥生成的指纹）。
3. **数据整理职能**：工程师 Cheese 的职能仅限于：
    - 从 Tushare/AkShare 获取原始指标。
    - 将指标归一化为 1-10 的原始分。
    - **调用本 Skill 获取结果**。
    - 整理输出为 JSON 格式。

---
*Protocol Activated: 2026-03-22*
*Authority: Chief Editor Override*
