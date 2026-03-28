#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏛️ 琥珀引擎 [2613-122号]：心跳点火执行指南
脉冲哨兵 (Heartbeat Start) - Ubuntu侧监听脚本
执行者: 工程师 Cheese
协议: 信号塔已就绪，启动脉冲监听
"""

import requests
import time
import os
import json
import sys
from datetime import datetime

# 物理参数：主编建好的信标 Raw 地址
BEACON_RAW_URL = "https://gist.githubusercontent.com/oceanuf/ba3d0c5ac402cc67529e97591203a6d3/raw/amber_cmd.json"
LAST_CMD_ID = 2613115  # 初始对齐 ID (基于2613-115号任务)

# 日志文件
LOG_FILE = "/home/luckyelite/.openclaw/workspace/amber-engine/pulse_monitor.log"
TASK_DIR = "/home/luckyelite/.openclaw/workspace/amber-engine/schedule/need_to_do"

def log_message(message):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    
    print(log_entry)
    
    # 写入日志文件
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_entry + "\n")

def start_pulse():
    """启动脉冲监听"""
    global LAST_CMD_ID
    
    log_message("="*60)
    log_message("📡 琥珀引擎脉冲哨兵已激活")
    log_message(f"目标信标: {BEACON_RAW_URL}")
    log_message(f"初始对齐ID: {LAST_CMD_ID}")
    log_message(f"任务目录: {TASK_DIR}")
    log_message("="*60)
    
    pulse_count = 0
    
    while True:
        pulse_count += 1
        
        try:
            # 1. 嗅探云端信标
            log_message(f"🔍 第{pulse_count}次脉冲扫描...")
            r = requests.get(BEACON_RAW_URL, timeout=10)
            
            if r.status_code != 200:
                log_message(f"⚠️ 信标访问失败: HTTP {r.status_code}")
                time.sleep(60)
                continue
            
            # 2. 解析指令
            cmd = r.json()
            current_id = cmd.get('id', 0)
            current_command = cmd.get('command', '')
            
            log_message(f"📡 收到信标: ID={current_id}, 指令={current_command}")
            
            # 3. 逻辑比对：检测新指令
            if current_id > LAST_CMD_ID:
                log_message(f"🚀 [捕获新频率] ID: {current_id} | 执行指令: {current_command}")
                
                # 4. 根据指令类型执行物理动作
                if current_command == "DEPLOY_HEARTBEAT_AND_CLEAN":
                    # 执行清理动作
                    cleanup_list = cmd.get('task', {}).get('cleanup', [])
                    log_message(f"🧹 执行清理任务，目标文件: {cleanup_list}")
                    
                    for file in cleanup_list:
                        target = os.path.join(TASK_DIR, file)
                        if os.path.exists(target):
                            os.remove(target)
                            log_message(f"   ✅ 已清理过时文件: {file}")
                        else:
                            log_message(f"   ⚠️ 文件不存在: {file}")
                
                # 5. 更新本地ID，完成闭环
                LAST_CMD_ID = current_id
                log_message(f"✅ 频率 {LAST_CMD_ID} 同步成功")
                
                # 6. 创建同步确认文件
                sync_file = f"SYNC_{current_id}.txt"
                sync_path = os.path.join(TASK_DIR, sync_file)
                with open(sync_path, 'w', encoding='utf-8') as f:
                    f.write(f"频率同步确认: ID={current_id}\n")
                    f.write(f"指令: {current_command}\n")
                    f.write(f"同步时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"执行者: 工程师 Cheese\n")
                
                log_message(f"📝 同步确认文件已创建: {sync_file}")
                
            elif current_id == LAST_CMD_ID:
                log_message(f"📊 频率保持同步: ID={current_id}")
            else:
                log_message(f"⚠️ 信标ID异常: 当前{current_id} < 本地{LAST_CMD_ID}")
            
        except requests.exceptions.RequestException as e:
            log_message(f"🌐 网络连接失败: {e}")
        except json.JSONDecodeError as e:
            log_message(f"📄 JSON解析失败: {e}")
        except Exception as e:
            log_message(f"❌ 未知错误: {e}")
        
        # 7. 等待下一次脉冲
        log_message(f"⏳ 等待60秒后下一次脉冲...")
        log_message("-"*40)
        time.sleep(60)

def check_environment():
    """检查运行环境"""
    log_message("🔧 检查运行环境...")
    
    # 检查任务目录
    if not os.path.exists(TASK_DIR):
        log_message(f"❌ 任务目录不存在: {TASK_DIR}")
        os.makedirs(TASK_DIR, exist_ok=True)
        log_message(f"✅ 已创建任务目录: {TASK_DIR}")
    
    # 检查日志目录
    log_dir = os.path.dirname(LOG_FILE)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    # 检查网络连接
    try:
        test_response = requests.get("https://api.github.com", timeout=5)
        log_message(f"✅ 网络连接正常: GitHub API HTTP {test_response.status_code}")
    except:
        log_message("⚠️ 网络连接测试失败")
    
    # 检查Python依赖
    try:
        import requests
        log_message("✅ Python依赖检查通过: requests")
    except ImportError:
        log_message("❌ 缺少Python依赖: requests")
        return False
    
    return True

def main():
    """主函数"""
    print("="*60)
    print("🏛️ 琥珀引擎脉冲哨兵启动程序")
    print("协议: [2613-122号] 心跳点火执行指南")
    print("执行者: 工程师 Cheese")
    print("="*60)
    
    # 检查环境
    if not check_environment():
        print("❌ 环境检查失败，无法启动脉冲哨兵")
        return
    
    # 启动脉冲监听
    try:
        print("🚀 正在启动脉冲哨兵...")
        print(f"📡 信标地址: {BEACON_RAW_URL}")
        print(f"📊 初始ID: {LAST_CMD_ID}")
        print(f"📝 日志文件: {LOG_FILE}")
        print("="*60)
        
        start_pulse()
        
    except KeyboardInterrupt:
        log_message("🛑 脉冲哨兵被手动终止")
        print("\n🛑 脉冲哨兵已停止")
    except Exception as e:
        log_message(f"💥 脉冲哨兵崩溃: {e}")
        print(f"💥 脉冲哨兵崩溃: {e}")

if __name__ == "__main__":
    main()
