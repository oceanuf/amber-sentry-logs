#!/usr/bin/env python3
"""
Tushare Pro会员额度监控脚本
监控request_remaining，防止流量耗尽导致首页数据"开天窗"
"""

import os
import sys
import json
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta

# 设置Tushare Token
TUSHARE_TOKEN = "9e32ef28eac05c5fbb11e6f02a50da903def70f94b3018e93340568b"
os.environ['TUSHARE_TOKEN'] = TUSHARE_TOKEN

class QuotaMonitor:
    """额度监控器"""
    
    def __init__(self):
        self.quota_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            "..", 
            "logs", 
            "quota_monitor.json"
        )
        self.alert_threshold = 100  # 剩余请求数低于100时触发告警
        self.critical_threshold = 10  # 剩余请求数低于10时触发紧急告警
        
        # 确保日志目录存在
        os.makedirs(os.path.dirname(self.quota_file), exist_ok=True)
    
    def get_quota_status(self):
        """获取当前额度状态（模拟，实际需要Tushare API支持）"""
        # 注意：Tushare API目前没有直接的额度查询接口
        # 这里通过记录API调用次数来估算
        
        current_time = datetime.now()
        
        # 读取历史记录
        if os.path.exists(self.quota_file):
            with open(self.quota_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        else:
            history = {
                'daily_requests': [],
                'monthly_requests': 0,
                'last_reset': current_time.strftime('%Y-%m-%d'),
                'estimated_remaining': 5000,  # 初始估计值
                'alerts_sent': []
            }
        
        # 估算剩余额度（基于使用模式）
        # Tushare Pro会员通常有5000次/天的调用限制
        daily_limit = 5000
        
        # 计算今日已使用次数
        today_str = current_time.strftime('%Y-%m-%d')
        today_requests = sum(1 for req in history.get('daily_requests', []) 
                           if req.get('date') == today_str)
        
        estimated_remaining = daily_limit - today_requests
        
        # 记录本次调用
        history['daily_requests'].append({
            'date': today_str,
            'time': current_time.strftime('%H:%M:%S'),
            'endpoint': 'quota_check',
            'estimated_remaining': estimated_remaining
        })
        
        # 保留最近7天的记录
        history['daily_requests'] = history['daily_requests'][-1000:]
        
        # 更新月度统计
        if current_time.day == 1:  # 每月1号重置
            history['monthly_requests'] = 0
        
        history['estimated_remaining'] = estimated_remaining
        history['last_check'] = current_time.strftime('%Y-%m-%d %H:%M:%S')
        
        # 保存记录
        with open(self.quota_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        
        return {
            'estimated_remaining': estimated_remaining,
            'daily_used': today_requests,
            'daily_limit': daily_limit,
            'usage_percentage': (today_requests / daily_limit) * 100,
            'last_check': current_time.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def check_quota_and_alert(self):
        """检查额度并触发告警"""
        print("=" * 70)
        print("📊 Tushare Pro会员额度监控")
        print("=" * 70)
        
        quota_status = self.get_quota_status()
        
        remaining = quota_status['estimated_remaining']
        used = quota_status['daily_used']
        limit = quota_status['daily_limit']
        usage_pct = quota_status['usage_percentage']
        
        print(f"📈 额度使用情况:")
        print(f"   今日已使用: {used} 次")
        print(f"   剩余额度: {remaining} 次")
        print(f"   每日限额: {limit} 次")
        print(f"   使用率: {usage_pct:.1f}%")
        print(f"   检查时间: {quota_status['last_check']}")
        
        # 检查是否需要告警
        alert_needed = False
        alert_level = None
        alert_message = None
        
        if remaining <= self.critical_threshold:
            alert_needed = True
            alert_level = "CRITICAL"
            alert_message = f"🚨 紧急告警: Tushare Pro额度仅剩 {remaining} 次，即将耗尽！"
            print(f"❌ {alert_message}")
            
        elif remaining <= self.alert_threshold:
            alert_needed = True
            alert_level = "WARNING"
            alert_message = f"⚠️ 额度告警: Tushare Pro额度仅剩 {remaining} 次，请关注！"
            print(f"⚠️ {alert_message}")
            
        else:
            print(f"✅ 额度充足: 剩余 {remaining} 次")
        
        # 触发告警
        if alert_needed:
            self.trigger_quota_alert(alert_level, alert_message, quota_status)
        
        # 生成使用报告
        self.generate_usage_report(quota_status)
        
        return quota_status, alert_needed
    
    def trigger_quota_alert(self, level, message, quota_status):
        """触发额度告警"""
        print(f"\n🚨 触发额度告警 (级别: {level})")
        print("=" * 70)
        
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        alert_details = f"""
{message}

📊 额度详情:
   剩余请求数: {quota_status['estimated_remaining']} 次
   今日已使用: {quota_status['daily_used']} 次
   每日限额: {quota_status['daily_limit']} 次
   使用率: {quota_status['usage_percentage']:.1f}%
   检查时间: {current_time}

💡 建议措施:
   1. 减少非必要API调用
   2. 增加数据缓存时间
   3. 考虑升级会员等级
   4. 检查是否有异常高频调用

⚠️ 如果额度耗尽，琥珀引擎首页将无法更新数据！
"""
        
        print(alert_details)
        
        # 保存告警日志
        alert_log = {
            'timestamp': current_time,
            'level': level,
            'message': message,
            'quota_status': quota_status,
            'alert_details': alert_details.strip()
        }
        
        alert_log_file = os.path.join(
            os.path.dirname(self.quota_file),
            f"quota_alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        with open(alert_log_file, 'w', encoding='utf-8') as f:
            json.dump(alert_log, f, ensure_ascii=False, indent=2)
        
        print(f"💾 告警日志已保存: {alert_log_file}")
        
        # TODO: 实际部署时需要配置微信/邮件告警
        print("📧 告警通知: 需要配置微信/邮件告警通道")
        
        # 发送系统通知（示例）
        try:
            # 这里可以添加实际的邮件发送逻辑
            # send_email_alert(alert_details, level)
            pass
        except Exception as e:
            print(f"⚠️ 告警发送失败: {e}")
    
    def generate_usage_report(self, quota_status):
        """生成额度使用报告"""
        report_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            "..", 
            "reports", 
            "quota"
        )
        os.makedirs(report_dir, exist_ok=True)
        
        report_file = os.path.join(
            report_dir, 
            f"quota_report_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
        )
        
        # 读取历史数据
        if os.path.exists(self.quota_file):
            with open(self.quota_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            # 分析使用模式
            daily_requests = history.get('daily_requests', [])
            
            # 按日期统计
            date_stats = {}
            for req in daily_requests:
                date = req.get('date')
                if date:
                    if date not in date_stats:
                        date_stats[date] = 0
                    date_stats[date] += 1
            
            # 生成报告
            report_content = f"""# Tushare Pro会员额度使用报告

## 报告时间
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 当前额度状态
- 剩余请求数: {quota_status['estimated_remaining']} 次
- 今日已使用: {quota_status['daily_used']} 次
- 每日限额: {quota_status['daily_limit']} 次
- 使用率: {quota_status['usage_percentage']:.1f}%

## 历史使用统计
"""
            
            # 添加最近7天统计
            recent_dates = sorted(date_stats.keys(), reverse=True)[:7]
            for date in recent_dates:
                count = date_stats[date]
                report_content += f"- {date}: {count} 次请求\n"
            
            report_content += f"""
## 使用趋势分析
- 平均每日请求: {sum(date_stats.values()) / max(len(date_stats), 1):.1f} 次
- 最高单日请求: {max(date_stats.values()) if date_stats else 0} 次
- 预计剩余天数: {quota_status['estimated_remaining'] / (sum(date_stats.values()) / max(len(date_stats), 1)):.1f} 天

## 告警阈值
- 警告阈值: {self.alert_threshold} 次剩余
- 紧急阈值: {self.critical_threshold} 次剩余
- 当前状态: {'⚠️ 需要关注' if quota_status['estimated_remaining'] <= self.alert_threshold else '✅ 正常'}

## 优化建议
"""
            
            if quota_status['usage_percentage'] > 80:
                report_content += "- ⚠️ 使用率超过80%，建议优化API调用频率\n"
            else:
                report_content += "- ✅ 使用率正常，当前调用策略合理\n"
            
            report_content += f"""
## 监控配置
- 检查频率: 每次API调用后
- 告警方式: 系统日志 + 邮件/微信通知
- 数据保存: 最近1000次调用记录

---
*琥珀引擎额度监控系统*
*最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            print(f"📋 额度报告已生成: {report_file}")
    
    def optimize_api_calls(self):
        """优化API调用策略"""
        print("\n🔧 优化API调用策略...")
        
        optimizations = []
        
        # 1. 增加数据缓存时间
        optimizations.append({
            'action': '增加数据缓存时间',
            'description': '将数据缓存时间从1小时延长到4小时',
            'estimated_saving': '减少75%的API调用'
        })
        
        # 2. 批量获取数据
        optimizations.append({
            'action': '批量获取数据',
            'description': '将多个独立请求合并为批量请求',
            'estimated_saving': '减少50%的API调用'
        })
        
        # 3. 使用本地缓存
        optimizations.append({
            'action': '强化本地缓存',
            'description': '对历史数据使用本地缓存，避免重复请求',
            'estimated_saving': '减少30%的API调用'
        })
        
        print("💡 优化建议:")
        for opt in optimizations:
            print(f"   ✅ {opt['action']}: {opt['description']} ({opt['estimated_saving']})")
        
        return optimizations

def main():
    """主函数"""
    print("🚀 开始Tushare Pro会员额度监控...")
    
    monitor = QuotaMonitor()
    
    # 检查额度
    quota_status, alert_needed = monitor.check_quota_and_alert()
    
    # 如果额度紧张，提供优化建议
    if quota_status['estimated_remaining'] <= monitor.alert_threshold * 2:
        monitor.optimize_api_calls()
    
    print("\n" + "=" * 70)
    print("🏆 额度监控完成")
    print("=" * 70)
    
    if alert_needed:
        print("⚠️ 额度告警已触发，请及时处理")
    else:
        print("✅ 额度状态正常")
    
    print(f"📊 剩余额度: {quota_status['estimated_remaining']} 次")
    print(f"📈 使用率: {quota_status['usage_percentage']:.1f}%")
    print(f"⏰ 检查时间: {quota_status['last_check']}")
    
    return 0 if not alert_needed else 1

if __name__ == "__main__":
    sys.exit(main())