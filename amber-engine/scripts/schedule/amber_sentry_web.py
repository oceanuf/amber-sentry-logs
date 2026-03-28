import requests
import time
import os
import re

# --- 核心配置 ---
# 主编已发布的 Google Doc 纯文本隧道
URL = "https://docs.google.com/document/d/e/2PACX-1vTlS_kDex6KGKE5MzoZec615Upw0Yb4ds0_MwsH5JBWBv3yy1Yvw9kG4pj2WQwaaC02IEp46cPz1AZF/pub?embedded=true"
TARGET_DIR = "./schedule/need_to_do/"
LOG_FILE = "./schedule/amber_sentry_web.log"

def fetch_command():
    try:
        # 获取云端指令流
        response = requests.get(URL, timeout=10)
        content = response.text
        
        # 匹配定界符逻辑
        if "AMBER_COMMAND_START" in content:
            # 提取 ID 作为文件名，防止重复执行相同 ID 的任务
            cmd_id_match = re.search(r"2613-\d+", content)
            cmd_id = cmd_id_match.group(0) if cmd_id_match else "unknown"
            file_name = f"{cmd_id}.md"
            target_path = os.path.join(TARGET_DIR, file_name)
            
            # 如果该指令文件已存在，说明已处理过，跳过
            if os.path.exists(target_path):
                return

            # 物理落地
            with open(target_path, "w") as f:
                f.write(content)
            
            log_msg = f"[TS: {time.strftime('%Y-%m-%d %H:%M:%S')}] ✅ [CLOUD_SYNC] 指令 {file_name} 已成功落地磁盘\n"
            print(log_msg.strip())
            with open(LOG_FILE, "a") as log:
                log.write(log_msg)
        
    except Exception as e:
        error_msg = f"[TS: {time.strftime('%Y-%m-%d %H:%M:%S')}] ❌ [SYNC_ERROR] {str(e)}\n"
        print(error_msg.strip())
        with open(LOG_FILE, "a") as log:
            log.write(error_msg)

if __name__ == "__main__":
    print("📡 [AMBER SENTRY V2.0] 云端 Web 哨兵已上线，正在监听主编指令...")
    while True:
        fetch_command()
        time.sleep(30) # 缩短轮询至 30 秒，确保响应灵敏度