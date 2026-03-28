import os.path
import io
import re
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# 范围：只读文档权限
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
# 您的文档 ID (AMBER_COMMAND_CENTER)
DOCUMENT_ID = '1DK12HipUA10tRMGTiJm0KHJe3m03KrV95m3ApLxQlCw'
TARGET_DIR = './schedule/need_to_do/'

def get_service():
    creds = None
    token_path = 'token.json'
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_console()
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    return build('drive', 'v3', credentials=creds)

def fetch_and_dispatch():
    service = get_service()
    # 导出为纯文本格式 (text/plain) 彻底避开 HTML
    request = service.files().export_media(fileId=DOCUMENT_ID, mimeType='text/plain')
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    
    content = fh.getvalue().decode('utf-8')
    
    if "AMBER_COMMAND_START" in content:
        cmd_id_match = re.search(r"ID\s*:\s*(2613-\d+)", content)
        cmd_id = cmd_id_match.group(1) if cmd_id_match else "unknown"
        target_path = os.path.join(TARGET_DIR, f"{cmd_id}.md")
        
        if not os.path.exists(target_path):
            with open(target_path, "w") as f:
                f.write(content)
            print(f"⚡ [API_SYNC] 指令 {cmd_id} 已实时落地")

if __name__ == "__main__":
    print("🚀 [AMBER SENTRY V3.0] API 哨兵已点火，正在监听零延迟指令...")
    while True:
        try:
            fetch_and_dispatch()
        except Exception as e:
            print(f"❌ 链路异常: {e}")
        import time
        time.sleep(10)
