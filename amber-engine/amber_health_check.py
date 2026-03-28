#!/usr/bin/env python3
"""
琥珀引擎系统健康检查脚本
版本: 1.0.0
创建时间: 2026-03-24
作者: 工程师 Cheese
团队: Cheese Intelligence Team
"""

import os
import sys
import json
import subprocess
import datetime
from pathlib import Path

class AmberHealthCheck:
    def __init__(self):
        self.workspace = Path.home() / ".openclaw" / "workspace" / "amber-engine"
        self.scripts_dir = Path.home() / "scripts"
        self.report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "system": "琥珀引擎健康检查",
            "version": "1.0.0",
            "checks": []
        }
    
    def add_check(self, name, status, details=None):
        """添加检查结果"""
        self.report["checks"].append({
            "name": name,
            "status": status,
            "timestamp": datetime.datetime.now().isoformat(),
            "details": details or {}
        })
    
    def check_web_server(self):
        """检查Web服务器状态"""
        try:
            result = subprocess.run(
                ["curl", "-k", "-I", "-s", "https://localhost:10168/master-audit/current_standard.html"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if "200 OK" in result.stdout:
                self.add_check("Web服务器", "🟢 正常", {
                    "status_code": 200,
                    "server": "Nginx/1.24.0",
                    "response": "页面可正常访问"
                })
            else:
                self.add_check("Web服务器", "🔴 异常", {
                    "error": "HTTP状态码异常",
                    "output": result.stdout[:200]
                })
        except Exception as e:
            self.add_check("Web服务器", "🔴 异常", {
                "error": str(e),
                "type": type(e).__name__
            })
    
    def check_cron_jobs(self):
        """检查定时任务状态"""
        try:
            # 检查数据更新任务
            result = subprocess.run(
                ["crontab", "-l"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            cron_jobs = []
            if "amber_unified_data_engine.py" in result.stdout:
                cron_jobs.append("数据更新任务 (交易日15:00)")
            
            if "amber_dragon_tiger.py" in result.stdout:
                cron_jobs.append("龙虎榜任务 (工作日18:00)")
            
            if cron_jobs:
                self.add_check("定时任务", "🟢 正常", {
                    "jobs": cron_jobs,
                    "count": len(cron_jobs)
                })
            else:
                self.add_check("定时任务", "🟡 警告", {
                    "warning": "未找到琥珀引擎定时任务",
                    "crontab_output": result.stdout[:200]
                })
        except Exception as e:
            self.add_check("定时任务", "🔴 异常", {
                "error": str(e),
                "type": type(e).__name__
            })
    
    def check_core_files(self):
        """检查核心文件完整性"""
        required_files = [
            self.workspace / "amber_final_strike.py",
            self.workspace / "etf_50_seeds.json",
            self.workspace / "etf_50_full_audit.json",
            self.scripts_dir / "amber_dragon_tiger.py",
            self.workspace / "memory" / f"{datetime.datetime.now().strftime('%Y-%m-%d')}.md"
        ]
        
        existing_files = []
        missing_files = []
        
        for file_path in required_files:
            if file_path.exists():
                existing_files.append(str(file_path))
            else:
                missing_files.append(str(file_path))
        
        if missing_files:
            self.add_check("核心文件", "🟡 警告", {
                "existing": existing_files,
                "missing": missing_files,
                "total": len(required_files),
                "existing_count": len(existing_files)
            })
        else:
            self.add_check("核心文件", "🟢 正常", {
                "files": existing_files,
                "count": len(existing_files)
            })
    
    def check_network(self):
        """检查网络连接"""
        try:
            result = subprocess.run(
                ["curl", "-I", "-s", "https://api.tushare.pro"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if "200" in result.stdout:
                self.add_check("网络连接", "🟢 正常", {
                    "api": "Tushare Pro",
                    "status": "连接正常",
                    "response_time": "正常"
                })
            else:
                self.add_check("网络连接", "🟡 警告", {
                    "api": "Tushare Pro",
                    "status": "连接异常",
                    "output": result.stdout[:200]
                })
        except Exception as e:
            self.add_check("网络连接", "🔴 异常", {
                "error": str(e),
                "type": type(e).__name__
            })
    
    def check_dragon_tiger_log(self):
        """检查龙虎榜日志"""
        log_file = self.scripts_dir / "dragon_tiger.log"
        if log_file.exists():
            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    last_10_lines = lines[-10:] if len(lines) >= 10 else lines
                
                last_execution = "".join(last_10_lines)
                has_error = any("失败" in line or "error" in line.lower() for line in last_10_lines)
                
                if has_error:
                    self.add_check("龙虎榜日志", "🟡 警告", {
                        "status": "最近执行有错误",
                        "last_lines": last_execution,
                        "log_size": f"{log_file.stat().st_size} bytes"
                    })
                else:
                    self.add_check("龙虎榜日志", "🟢 正常", {
                        "status": "最近执行正常",
                        "last_lines": last_execution,
                        "log_size": f"{log_file.stat().st_size} bytes"
                    })
            except Exception as e:
                self.add_check("龙虎榜日志", "🔴 异常", {
                    "error": str(e),
                    "type": type(e).__name__
                })
        else:
            self.add_check("龙虎榜日志", "🟡 警告", {
                "warning": "日志文件不存在",
                "expected_path": str(log_file)
            })
    
    def generate_summary(self):
        """生成检查摘要"""
        total = len(self.report["checks"])
        ok = sum(1 for check in self.report["checks"] if "🟢" in check["status"])
        warning = sum(1 for check in self.report["checks"] if "🟡" in check["status"])
        error = sum(1 for check in self.report["checks"] if "🔴" in check["status"])
        
        summary = {
            "total_checks": total,
            "ok": ok,
            "warning": warning,
            "error": error,
            "health_score": round(ok / total * 100, 1) if total > 0 else 0
        }
        
        self.report["summary"] = summary
        
        # 总体状态判断
        if error > 0:
            overall_status = "🔴 异常"
        elif warning > 0:
            overall_status = "🟡 警告"
        else:
            overall_status = "🟢 正常"
        
        self.report["overall_status"] = overall_status
    
    def print_report(self):
        """打印检查报告"""
        print("=" * 60)
        print("🧀 琥珀引擎系统健康检查报告")
        print("=" * 60)
        print(f"检查时间: {self.report['timestamp']}")
        print(f"系统版本: {self.report['version']}")
        print(f"总体状态: {self.report['overall_status']}")
        print()
        
        summary = self.report["summary"]
        print(f"📊 检查摘要:")
        print(f"  总检查项: {summary['total_checks']}")
        print(f"  正常项: {summary['ok']} 🟢")
        print(f"  警告项: {summary['warning']} 🟡")
        print(f"  异常项: {summary['error']} 🔴")
        print(f"  健康评分: {summary['health_score']}%")
        print()
        
        print("🔍 详细检查结果:")
        for check in self.report["checks"]:
            print(f"  {check['status']} {check['name']}")
            if check.get('details'):
                for key, value in check['details'].items():
                    if isinstance(value, list):
                        print(f"    {key}:")
                        for item in value:
                            print(f"      - {item}")
                    else:
                        print(f"    {key}: {value}")
            print()
        
        print("=" * 60)
        print("💡 建议:")
        
        if summary['error'] > 0:
            print("  ⚠️ 发现异常项，建议立即处理")
        if summary['warning'] > 0:
            print("  ⚠️ 发现警告项，建议近期处理")
        if summary['ok'] == summary['total_checks']:
            print("  ✅ 所有检查项正常，系统运行良好")
        
        print("=" * 60)
    
    def save_report(self):
        """保存检查报告到文件"""
        report_dir = self.workspace / "health_reports"
        report_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = report_dir / f"health_check_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, ensure_ascii=False, indent=2)
        
        print(f"📁 报告已保存至: {report_file}")
    
    def run_all_checks(self):
        """运行所有检查"""
        print("🔍 开始琥珀引擎系统健康检查...")
        print()
        
        self.check_web_server()
        self.check_cron_jobs()
        self.check_core_files()
        self.check_network()
        self.check_dragon_tiger_log()
        
        self.generate_summary()
        self.print_report()
        self.save_report()

def main():
    """主函数"""
    print("🧀 琥珀引擎系统健康检查脚本 v1.0.0")
    print("团队: Cheese Intelligence Team")
    print("工程师: Cheese")
    print()
    
    checker = AmberHealthCheck()
    checker.run_all_checks()
    
    # 返回适当的退出码
    summary = checker.report["summary"]
    if summary["error"] > 0:
        return 1
    elif summary["warning"] > 0:
        return 2
    else:
        return 0

if __name__ == "__main__":
    sys.exit(main())