#!/usr/bin/env python3
"""
测试授权URL生成
"""

from google_auth_oauthlib.flow import InstalledAppFlow

# 范围：只读文档权限
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def main():
    try:
        print("🔧 测试OAuth配置...")
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        
        print("✅ 配置加载成功")
        print(f"📋 项目ID: {flow.client_config.get('project_id', '未设置')}")
        print(f"📋 客户端ID: {flow.client_config.get('client_id', '未设置')}")
        print(f"📋 redirect_uris: {flow.client_config.get('redirect_uris', [])}")
        
        # 生成授权URL
        auth_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        print(f"\n🎯 授权URL生成成功!")
        print(f"🔗 URL: {auth_url}")
        print(f"📝 State: {state}")
        print(f"\n📋 授权URL长度: {len(auth_url)} 字符")
        
        # 检查URL中是否包含正确的redirect_uri
        if 'urn:ietf:wg:oauth:2.0:oob' in auth_url:
            print("✅ redirect_uri正确设置为 'urn:ietf:wg:oauth:2.0:oob'")
        else:
            print("⚠️  redirect_uri可能不正确")
            if 'http://localhost' in auth_url:
                print("   - 检测到 http://localhost")
            if 'http://127.0.0.1' in auth_url:
                print("   - 检测到 http://127.0.0.1")
            if 'https://cheese.ai' in auth_url:
                print("   - 检测到 https://cheese.ai")
        
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()