# 🏛️ 琥珀引擎全栈技术总账 - 50万量化实验室

## 📋 摘要信息
- **架构代号**: Museum 3.0 (实战派布局)
- **核心资产**: 500,000.00 CNY 实战本金
- **部署时间**: 2026-03-27 19:15 GMT+8
- **指令依据**: [2613-167号] 50万量化实验室全栈部署与数据对齐
- **记忆版本**: V4.8 (同步至GitHub)

---

## 🌐 网络拓扑架构

### 1. 双端口物理切割状态

#### 端口 10168 (原 SSL/NFS 档案馆)
- **协议**: HTTPS (SSL only)
- **域名**: gemini.googlemanager.cn
- **根目录**: `/var/www/gemini_master/`
- **SSL证书**: `/etc/nginx/ssl/gemini/gemini.googlemanager.cn.crt`
- **功能定位**: 静态档案馆，青铜法典，算法宪法
- **访问地址**: `https://gemini.googlemanager.cn:10168/master-audit/list.html`
- **Nginx配置**: `/etc/nginx/sites-enabled/gemini_master.conf`

#### 端口 10169 (HTTP 实战实验室)
- **协议**: HTTP (无SSL，实时性优先)
- **域名**: gemini.googlemanager.cn
- **根目录**: `/home/luckyelite/.openclaw/workspace/amber-engine/amber-sentry-logs/`
- **功能定位**: 50万量化实验室，实时交易看板，动态数据
- **访问地址**: `http://gemini.googlemanager.cn:10169/`
- **Nginx配置**: `/etc/nginx/sites-enabled/amber_sentry`

### 2. 物理切割逻辑
```
10168端口 (SSL)                   10169端口 (HTTP)
├── /var/www/gemini_master/        ├── /home/luckyelite/.openclaw/workspace/
│   ├── master-audit/              │   └── amber-engine/amber-sentry-logs/
│   │   ├── list.html              │       ├── list.html (实时看板)
│   │   ├── current_standard.html  │       ├── amber_cmd.json (算法配置)
│   │   └── bronze_details/        │       ├── portfolio_v1.json (投资组合)
│   └── data/                      │       ├── archive/ (归档数据)
│                                   │       ├── scripts/ (源码目录)
│                                   │       └── trading_logs/ (交易日志)
└── 静态档案馆，只读访问            └── 动态实验室，读写访问
```

### 3. 端口验证状态
```bash
# 10168端口 (SSL)
$ curl -k https://localhost:10168/master-audit/list.html
HTTP/1.1 200 OK

# 10169端口 (HTTP)
$ curl -I http://localhost:10169/
HTTP/1.1 200 OK
Server: nginx/1.24.0 (Ubuntu)
```

---

## 🔐 权限白名单与继承逻辑

### 1. 用户组架构
```bash
# 核心用户
uid=33(www-data) gid=33(www-data) groups=33(www-data),1000(luckyelite)
uid=1000(luckyelite) gid=1000(luckyelite) groups=1000(luckyelite),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),100(users),114(lpadmin)
```

### 2. 权限继承逻辑 (防止500错误回归)

#### 2.1 10169端口根目录权限
```bash
/home/luckyelite/.openclaw/workspace/amber-engine/amber-sentry-logs/
├── 所有者: luckyelite (1000)
├── 组: www-data (33)
├── 权限: 755 (drwxr-xr-x)
└── 关键: www-data组有读取权限，luckyelite有完全权限
```

#### 2.2 关键文件权限设置
```bash
# 配置文件 (可读写)
amber_cmd.json           -rw-r--r-- luckyelite www-data
portfolio_v1.json        -rw-r--r-- luckyelite www-data

# HTML页面 (可读取)
list.html               -rw-r--r-- luckyelite luckyelite
portfolio_v1.html       -rw-r--r-- luckyelite www-data

# 脚本文件 (可执行)
scripts/live_trade_sim.py   -rwxrwxr-x luckyelite luckyelite
scripts/refresh_museum.py   -rwxrwxr-x luckyelite luckyelite
```

#### 2.3 重启安全策略
1. **目录权限检查脚本**: `check_permissions.sh` (需创建)
2. **Nginx用户配置**: 确保nginx以www-data用户运行
3. **SELinux/AppArmor**: 已禁用，避免权限拦截
4. **文件创建掩码**: umask 0022 (确保新文件www-data可读)

### 3. 500错误预防清单
| 错误类型 | 原因 | 解决方案 |
|----------|------|----------|
| **403 Forbidden** | 目录无读取权限 | `chmod 755 /path/to/dir` |
| **404 Not Found** | 文件不存在或路径错误 | 检查nginx root配置 |
| **500 Internal Error** | 脚本执行权限不足 | `chmod +x script.py` |
| **430 Permission Denied** | www-data无文件读取权限 | `chown luckyelite:www-data file` |

---

## 🔄 算法流转图 (Gist → Bias → 交易 → 广播)

### 1. 完整数据流
```
[GitHub Gist] → [REPORT_Gist_00127.md] → [Bias计算] → [live_trade_sim.py] → [portfolio_v1.json] → [amber_cmd.json] → [list.html]
      ↓               ↓                     ↓              ↓                    ↓                    ↓
  原始数据        格式化报告           偏离度分析       交易决策          投资组合更新       配置广播         前端展示
```

### 2. 各模块详细说明

#### 2.1 Gist数据获取模块
- **源文件**: `REPORT_Gist_00127.md` (位于amber-sentry-logs/)
- **格式**: Markdown表格，包含ETF代码、价格、MA20、Bias等
- **更新频率**: 每日收盘后自动生成
- **示例数据**:
  ```
  | 代码 | 名称 | 价格 | MA20 | Bias | MA20趋势 |
  |------|------|------|------|------|----------|
  | 518880 | 华安黄金ETF | 4.82 | 4.85 | -4.1% | UP |
  | 512480 | 半导体ETF | 1.22 | 1.24 | -3.8% | UP |
  ```

#### 2.2 Bias计算引擎
- **阈值**: Bias < -3.5% (猎杀线)
- **趋势要求**: MA20趋势必须为"UP"
- **优先级排序**:
  1. 华安黄金 (518880) - 优先猎杀
  2. 半导体 (512480) - 次优先
  3. 其他符合条件ETF - 按Bias偏离度排序

#### 2.3 实战交易脚本 (`live_trade_sim.py`)
```python
# 核心逻辑流程
1. load_config()              # 加载amber_cmd.json配置
2. load_portfolio()           # 加载portfolio_v1.json投资组合
3. scan_127_report()          # 读取REPORT_Gist_00127.md
4. filter_hunting_targets()   # 筛选Bias<-3.5%且MA20=UP
5. check_position_limits()    # 检查单ETF上限(100,000 CNY)
6. execute_trade()            # 执行分批次建仓(每笔20,000 CNY)
7. save_portfolio()           # 保存更新后的投资组合
8. update_amber_cmd_with_trade() # 广播交易信息
```

#### 2.4 配置广播系统 (`amber_cmd.json`)
```json
{
  "system_name": "琥珀引擎 3.0",
  "version": "3.0.0",
  "ui_priority": "trade_first",
  "portfolio_summary": {
    "total_value": 499974.18,
    "p_l_amount": -25.82,
    "p_l_ratio": "-0.01%",
    "cash_balance": 479976.0,
    "position_count": 1,
    "position_percent": "4.00%"
  },
  "market_snapshot": {
    "top_alpha": ["518880", "512480", "512660"],
    "avg_bias": "-3.1%",
    "opportunity_count": 2,
    "scan_time": "2026-03-27 19:15:00"
  }
}
```

#### 2.5 前端展示层 (`list.html`)
- **技术栈**: HTML5 + CSS3 + JavaScript (原生)
- **实时更新**: 通过`refresh_museum.py`每30秒刷新
- **核心组件**:
  1. **顶部统计区**: 大号数字显示总资产、盈亏、仓位
  2. **信号滚动条**: 实时显示捕获的交易信号
  3. **持仓明细表**: 当前持仓ETF的详细信息
  4. **交易流水区**: 按时间倒序显示所有交易记录

---

## ⏰ Crontab任务表 (自动化运维)

### 1. 关键触发点配置

#### 1.1 每15分钟 - 交易机会扫描
```bash
*/15 * * * * cd /home/luckyelite/.openclaw/workspace/amber-engine && python3 scripts/live_trade_sim.py >> /home/luckyelite/.openclaw/workspace/amber-engine/amber-sentry-logs/trading_logs/live_trade_$(date +\%Y\%m\%d).log 2>&1
```
- **脚本路径**: `/home/luckyelite/.openclaw/workspace/amber-engine/scripts/live_trade_sim.py`
- **日志位置**: `amber-sentry-logs/trading_logs/live_trade_YYYYMMDD.log`
- **执行用户**: luckyelite (需要文件写入权限)

#### 1.2 每30秒 - 数据刷新推送
```bash
* * * * * cd /home/luckyelite/.openclaw/workspace/amber-engine && python3 scripts/refresh_museum.py >> /tmp/refresh_museum.log 2>&1
* * * * * sleep 30 && cd /home/luckyelite/.openclaw/workspace/amber-engine && python3 scripts/refresh_museum.py >> /tmp/refresh_museum.log 2>&1
```
- **脚本路径**: `/home/luckyelite/.openclaw/workspace/amber-engine/scripts/refresh_museum.py`
- **功能**: 模拟市场波动，更新`amber_cmd.json`和`portfolio_v1.json`
- **输出**: 实时更新list.html中的数字显示

#### 1.3 每晚20:00 - 日报生成与Git推送
```bash
0 20 * * * cd /home/luckyelite/.openclaw/workspace/amber-engine && python3 scripts/generate_daily_report.py && cd /home/luckyelite/.openclaw/workspace/amber-engine/amber-sentry-logs && git add . && git commit -m "DAILY_REPORT: 50万实战盈亏结项报告 $(date +\%Y-\%m-\%d)" && git push origin master >> /home/luckyelite/.openclaw/workspace/amber-engine/amber-sentry-logs/trading_logs/git_push_$(date +\%Y\%m\%d).log 2>&1
```
- **日报脚本**: `scripts/generate_daily_report.py` (需创建)
- **Git仓库**: `amber-sentry-logs/` 目录下的Git仓库
- **报告格式**: Markdown，包含当日交易摘要、盈亏分析、持仓明细

### 2. Crontab当前状态
```bash
# 当前用户的crontab
$ crontab -l
0 20 * * 1-5 /bin/bash /home/luckyelite/scripts/global_gravity_automation.sh >> /home/luckyelite/scripts/automation_log.txt 2>&1
5 17 * * 1-5 /bin/bash /home/luckyelite/scripts/global_gravity_automation_fixed.sh >> /home/luckyelite/scripts/automation_domestic_log.txt 2>&1

# 注：50万量化实验室的crontab需要手动添加
```

### 3. 服务管理脚本 (推荐创建)
```bash
#!/bin/bash
# /home/luckyelite/scripts/quant_lab_control.sh

case "$1" in
  start)
    # 添加crontab任务
    (crontab -l 2>/dev/null; echo "*/15 * * * * cd /home/luckyelite/.openclaw/workspace/amber-engine && python3 scripts/live_trade_sim.py >> /home/luckyelite/.openclaw/workspace/amber-engine/amber-sentry-logs/trading_logs/live_trade_\$(date +\%Y\%m\%d).log 2>&1") | crontab -
    (crontab -l 2>/dev/null; echo "* * * * * cd /home/luckyelite/.openclaw/workspace/amber-engine && python3 scripts/refresh_museum.py >> /tmp/refresh_museum.log 2>&1") | crontab -
    (crontab -l 2>/dev/null; echo "* * * * * sleep 30 && cd /home/luckyelite/.openclaw/workspace/amber-engine && python3 scripts/refresh_museum.py >> /tmp/refresh_museum.log 2>&1") | crontab -
    echo "✅ 50万量化实验室自动化任务已启动"
    ;;
  stop)
    # 移除相关crontab任务
    crontab -l | grep -v "live_trade_sim\|refresh_museum" | crontab -
    echo "🛑 50万量化实验室自动化任务已停止"
    ;;
  status)
    echo "📊 50万量化实验室状态"
    echo "Crontab任务:"
    crontab -l | grep -E "live_trade_sim|refresh_museum" || echo "  未找到相关任务"
    echo "端口监听:"
    ss -tlnp | grep ":10169" && echo "  10169端口: ✅ 监听中" || echo "  10169端口: ❌ 未监听"
    ;;
  *)
    echo "用法: $0 {start|stop|status}"
    ;;
esac
```

---

## 🚨 禁忌指令与安全边界

### 1. 严禁操作清单
| 操作 | 风险等级 | 后果 | 安全替代方案 |
|------|----------|------|--------------|
| **修改/etc/nginx/核心配置** | 🔴 高危 | 导致10168/10169端口不可访问 | 仅修改sites-enabled/下的配置文件 |
| **删除/var/www/gemini_master/** | 🔴 高危 | 静态档案馆永久丢失 | 备份后再操作，使用rsync同步 |
| **修改www-data用户权限** | 🟡 中危 | 导致500权限错误 | 使用chown/chmod谨慎调整 |
| **直接编辑portfolio_v1.json** | 🟡 中危 | 数据不一致，交易记录丢失 | 通过live_trade_sim.py脚本更新 |
| **重启nginx不测试配置** | 🟡 中危 | 配置错误导致服务中断 | `nginx -t`测试后再重启 |

### 2. 备份策略
```bash
# 每日自动备份 (建议添加到crontab)
0 2 * * * tar -czf /backup/amber-engine_$(date +\%Y\%m\%d).tar.gz /home/luckyelite/.openclaw/workspace/amber-engine/amber-sentry-logs/

# 配置文件备份
cp /etc/nginx/sites-enabled/amber_sentry /etc/nginx/sites-enabled/amber_sentry.backup.$(date +%Y%m%d_%H%M%S)

# Git提交前备份
cd /home/luckyelite/.openclaw/workspace/amber-engine/amber-sentry-logs/
cp amber_cmd.json amber_cmd.json.backup.$(date +%Y%m%d_%H%M%S)
cp portfolio_v1.json portfolio_v1.json.backup.$(date +%Y%m%d_%H%M%S)
```

### 3. 灾难恢复流程
1. **端口不可访问**: 检查nginx状态 `systemctl status nginx`
2. **500权限错误**: 检查目录权限 `ls -la /home/luckyelite/.openclaw/workspace/amber-engine/amber-sentry-logs/`
3. **数据不一致**: 从Git恢复 `git checkout -- amber_cmd.json portfolio_v1.json`
4. **脚本执行失败**: 检查Python环境 `python3 --version` 和依赖 `pip list`

---

## 📁 文件系统地图

### 1. 核心目录结构
```
/home/luckyelite/.openclaw/workspace/amber-engine/
├── amber-sentry-logs/                    # 10169端口根目录
│   ├── amber_cmd.json                    # 算法配置中心
│   ├── portfolio_v1.json                 # 投资组合数据
│   ├── portfolio_v1.html                 # 实战看板页面
│   ├── list.html                         # 首页实时看板
│   ├── REPORT_Gist_00127.md              # 127号扫描报告
│   ├── SYSTEM_MEMORY.md                   # 系统共同记忆 (V4.8)
│   ├── archive/                           # 数据归档
│   │   ├── data/                          # 原始数据
│   │   ├── reports/                       # 日报周报
│   │   ├── tasks/                         # 任务记录
│   │   └── trading_logs/                  # 交易日志
│   └── scripts/                           # 源码目录
│       └── index.html                     # 脚本索引页
├── scripts/                               # 主脚本目录
│   ├── live_trade_sim.py                  # 实战交易脚本
│   ├── refresh_museum.py                  # 数据刷新脚本
│   └── (其他算法脚本)
└── TECHNICAL_MANIFEST.md                  # 本技术总账