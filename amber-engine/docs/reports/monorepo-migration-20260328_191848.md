# 档案馆单体仓库迁移报告
## 迁移时间: 2026-03-28 19:18:48
## 法典依据: 《档案馆单体仓库同步法典 V3.1 (修正版)》（编号 2614-001）

### 迁移前目录结构
```bash
/home/luckyelite/.openclaw/workspace/amber-engine/PROGRESS_115.txt
/home/luckyelite/.openclaw/workspace/amber-engine/SOUL.md
/home/luckyelite/.openclaw/workspace/amber-engine/web/bronze_etf_details.html
/home/luckyelite/.openclaw/workspace/amber-engine/web/bronze_etf_details.html.backup
/home/luckyelite/.openclaw/workspace/amber-engine/web/bronze_etf_details_fixed.html
/home/luckyelite/.openclaw/workspace/amber-engine/web/bronze_static_final.html.backup
/home/luckyelite/.openclaw/workspace/amber-engine/web/bronze_static_final_fixed.html
/home/luckyelite/.openclaw/workspace/amber-engine/web/bronze_static_final.html
/home/luckyelite/.openclaw/workspace/amber-engine/web/index.php
/home/luckyelite/.openclaw/workspace/amber-engine/web/ACCESS_GUIDE.md
/home/luckyelite/.openclaw/workspace/amber-engine/amber_unified_data_engine.py.backup
/home/luckyelite/.openclaw/workspace/amber-engine/backup_absolute_paths_20260328_191125/access_guide.md_1774696285
/home/luckyelite/.openclaw/workspace/amber-engine/backup_absolute_paths_20260328_191125/RADAR_ACT.py_1774696285
/home/luckyelite/.openclaw/workspace/amber-engine/backup_absolute_paths_20260328_191125/refresh_museum.py_1774696285
/home/luckyelite/.openclaw/workspace/amber-engine/backup_absolute_paths_20260328_191125/archive_index.php_1774696285
/home/luckyelite/.openclaw/workspace/amber-engine/backup_absolute_paths_20260328_191125/index.php_1774696285
/home/luckyelite/.openclaw/workspace/amber-engine/backup_absolute_paths_20260328_191125/quick_update.sh_1774696285
/home/luckyelite/.openclaw/workspace/amber-engine/backup_absolute_paths_20260328_191125/GITHUB_SYNC_REPORT.md_1774696285
/home/luckyelite/.openclaw/workspace/amber-engine/backup_absolute_paths_20260328_191125/analyze_etf_value.py_1774696285
/home/luckyelite/.openclaw/workspace/amber-engine/backup_absolute_paths_20260328_191125/rebuild_minimalist_fixed.py_1774696285
/home/luckyelite/.openclaw/workspace/amber-engine/backup_absolute_paths_20260328_191125/daily_fallback_heartbeat.py_1774696285
/home/luckyelite/.openclaw/workspace/amber-engine/backup_absolute_paths_20260328_191125/2613-199-final-summary.md_1774696285
/home/luckyelite/.openclaw/workspace/amber-engine/backup_absolute_paths_20260328_191125/task_b_data_fallback_system.py_1774696285
/home/luckyelite/.openclaw/workspace/amber-engine/backup_absolute_paths_20260328_191125/2613-069-report.md_1774696285
/home/luckyelite/.openclaw/workspace/amber-engine/backup_absolute_paths_20260328_191125/琥珀引擎演武场重筑执行报告_2026-03-28_1711.md_1774696285
/home/luckyelite/.openclaw/workspace/amber-engine/backup_absolute_paths_20260328_191125/github_sync_safe.sh_1774696285
/home/luckyelite/.openclaw/workspace/amber-engine/backup_absolute_paths_20260328_191125/simple_tushare_test.py_1774696285
/home/luckyelite/.openclaw/workspace/amber-engine/backup_absolute_paths_20260328_191125/dry_run_test.py_1774696285
/home/luckyelite/.openclaw/workspace/amber-engine/backup_absolute_paths_20260328_191125/verify_sync.sh_1774696285
/home/luckyelite/.openclaw/workspace/amber-engine/backup_absolute_paths_20260328_191125/2613-070.md_1774696285
/home/luckyelite/.openclaw/workspace/amber-engine/backup_absolute_paths_20260328_191125/amber_sentry_api.py_1774696285
/home/luckyelite/.openclaw/workspace/amber-engine/backup_absolute_paths_20260328_191125/preview_sample_001.sh_1774696285
/home/luckyelite/.openclaw/workspace/amber-engine/backup_absolute_paths_20260328_191125/deploy.sh_1774696285
/home/luckyelite/.openclaw/workspace/amber-engine/backup_absolute_paths_20260328_191125/setup_data_refresher_cron.sh_1774696285
/home/luckyelite/.openclaw/workspace/amber-engine/backup_absolute_paths_20260328_191125/fifteen_five_akshare_full.py_1774696285
/home/luckyelite/.openclaw/workspace/amber-engine/backup_absolute_paths_20260328_191125/archive_only_sync.sh_1774696285
/home/luckyelite/.openclaw/workspace/amber-engine/backup_absolute_paths_20260328_191125/MEMORY.md_1774696285
/home/luckyelite/.openclaw/workspace/amber-engine/backup_absolute_paths_20260328_191125/sync_core_files.sh_1774696285
/home/luckyelite/.openclaw/workspace/amber-engine/backup_absolute_paths_20260328_191125/fifteen_five_akshare_analyzer.py_1774696285
/home/luckyelite/.openclaw/workspace/amber-engine/backup_absolute_paths_20260328_191125/琥珀引擎演武场重筑执行报告_2026-03-28_1356.md_1774696285
/home/luckyelite/.openclaw/workspace/amber-engine/backup_absolute_paths_20260328_191125/health_check_20260324_084811.json_1774696285
/home/luckyelite/.openclaw/workspace/amber-engine/backup_absolute_paths_20260328_191125/琥珀引擎演武场重筑执行报告_2026-03-28_1211.md_1774696285
/home/luckyelite/.openclaw/workspace/amber-engine/backup_absolute_paths_20260328_191125/琥珀引擎演武场重筑执行报告_2026-03-28_1741.md_1774696285
/home/luckyelite/.openclaw/workspace/amber-engine/backup_absolute_paths_20260328_191125/deploy_simple.sh_1774696285
/home/luckyelite/.openclaw/workspace/amber-engine/backup_absolute_paths_20260328_191125/generate_daily_report.py_1774696285
/home/luckyelite/.openclaw/workspace/amber-engine/backup_absolute_paths_20260328_191125/etf_data_updater.py_1774696285
/home/luckyelite/.openclaw/workspace/amber-engine/backup_absolute_paths_20260328_191125/generate_index.py_1774696285
/home/luckyelite/.openclaw/workspace/amber-engine/backup_absolute_paths_20260328_191125/琥珀引擎演武场重筑执行报告_2026-03-28_1726.md_1774696285
/home/luckyelite/.openclaw/workspace/amber-engine/backup_absolute_paths_20260328_191125/README_PROTOCOL.md_1774696285
/home/luckyelite/.openclaw/workspace/amber-engine/backup_absolute_paths_20260328_191125/琥珀引擎演武场重筑执行报告_2026-03-28_1556.md_1774696285
```

### 迁移操作记录

#### 1. 创建法典要求的目录结构
- ✅ 创建 /web/, /vaults/, /docs/reports/, /scripts/github/, /database/ 目录

#### 2. 迁移web相关文件到/web/目录
- 迁移: radar_engine.js → /web/

#### 3. 迁移报告文件到/docs/reports/目录
- 迁移: REPORT_115_FINAL.txt → /docs/reports/
- 迁移: REPORT_124_FULL_SCALE.txt → /docs/reports/
- 迁移: REPORT_INIT_SUCCESS.txt → /docs/reports/

#### 4. 迁移脚本文件到/scripts/目录
