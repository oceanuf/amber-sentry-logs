#!/usr/bin/env python3
"""
测试OAuth授权流程
"""

import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# 范围：只读文档权限
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def main():
    creds = None
    token_path = 'token.json'
    
    # 检查是否存在token
    if os.path.exists(token_path):
        print("🔑 检测到现有token文件")
        try:
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            print("✅ Token文件读取成功")
        except Exception as e:
            print(f"❌ Token文件读取失败: {e}")
            os.remove(token_path)
            creds = None
    
    # 如果token无效或不存在
    if not creds or not creds.valid:
        print("🔄 需要新的OAuth授权")
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Token过期，尝试刷新...")
            try:
                creds.refresh(Request())
                print("✅ Token刷新成功")
            except Exception as e:
                print(f"❌ Token刷新失败: {e}")
                creds = None
        
        if not creds:
            print("🚀 开始新的OAuth授权流程")
            try:
                # 尝试使用console流程
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                print("✅ 从credentials.json加载成功")
                print(f"📋 项目ID: {flow.client_config.get('project_id', '未设置')}")
                print(f"📋 客户端ID: {flow.client_config.get('client_id', '未设置')}")
                
                # 获取授权URL
                auth_url, _ = flow.authorization_url(prompt='consent')
                print(f"\n🔗 授权URL: {auth_url}")
                print("\n📝 请访问上方链接进行授权，然后将返回的授权码粘贴到此处")
                
                # 等待用户输入
                auth_code = input("请输入授权码: ").strip()
                
                # 获取token
                flow.fetch_token(code=auth_code)
                creds = flow.credentials
                print("✅ 授权成功，获取到访问令牌")
                
            except Exception as e:
                print(f"❌ 授权流程失败: {e}")
                return
    
    # 保存token
    with open(token_path, 'w') as token:
        token.write(creds.to_json())
    print(f"💾 Token已保存到 {token_path}")
    print(f"📊 令牌信息:")
    print(f"   - 访问令牌: {'已设置' if creds.token else '未设置'}")
    print(f"   - 刷新令牌: {'已设置' if creds.refresh_token else '未设置'}")
    print(f"   - 过期时间: {creds.expiry if creds.expiry else '未设置'}")

if __name__ == "__main__":
    main()