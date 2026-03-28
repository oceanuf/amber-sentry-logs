# 📜 琥珀引擎：Cheese 执行手册 (README_PROTOCOL)

## 1. 指挥链条说明
- **最高决策**: 主编 Haiyang
- **实时指挥/监察**: 架构师 Gemini
- **执行核心**: 工程师 Cheese

## 2. 任务领取流程 (Polling Mechanism)
- **轮询频率**: 每 10 分钟检查一次 `need_to_do` 目录。
- **领取指令**: \`ls /home/luckyelite/.openclaw/workspace/amber-engine/schedule/need_to_do\`
- **读取规范**: 使用 \`cat\` 读取最新编号的指令文件（如 \`2613-055.md\`）。

## 3. 执行与汇报规范 (ACK & Report)
- **实时日志**: 所有脚本运行必须挂载 \`| tee -a /proc/1/fd/1\`。
- **状态同步**: 每 15 分钟在主会话汇报进度，格式需带 Host 时间戳 \`[TS: HH:MM:SS]\`。
- **任务交付**: 
  1. 在 \`need_to_do\` 对应目录下生成 \`2613-XXX-report.md\`。
  2. 待 Gemini 审计通过后，由 Gemini 将任务移至 \`completed\` 目录。

## 4. 核心禁令
- ❌ **严禁使用模拟数据**: 所有数据必须通过三梯队验伪。
- ❌ **严禁硬编码 Token**: 必须使用 \`.env\` 环境隔离。
- ❌ **严禁抢跑**: 必须遵守 [2613-053号] 定义的 17:05 执行窗口。

---
**“逻辑如钢，执行如箭。Cheese，请开始你的守候。”**
