琥珀引擎SSL证书安装指南
================================

问题：访问 https://finance.cheese.ai 时出现安全警告

原因：自签名证书缺少完整的证书链

解决方案：

方法1：一键安装（推荐）
--------------------
1. 下载所有证书文件
2. 双击运行 install-certificates.bat
3. 按照提示完成安装
4. 重启浏览器

方法2：手动安装
-------------
步骤1：安装根CA证书
1. 双击 amber-root-ca.crt
2. 点击"安装证书"
3. 选择"本地计算机" → 下一步
4. 选择"将所有的证书都放入下列存储"
5. 点击"浏览" → 选择"受信任的根证书颁发机构"
6. 完成安装

步骤2：安装服务器证书
1. 双击 amber-server.crt
2. 点击"安装证书"
3. 选择"本地计算机" → 下一步
4. 选择"将所有的证书都放入下列存储"
5. 点击"浏览" → 选择"中间证书颁发机构"
6. 完成安装

步骤3：清理浏览器缓存
1. 完全关闭所有浏览器窗口
2. 清除SSL状态缓存：
   - Chrome: chrome://net-internals/#hsts
   - Edge: edge://net-internals/#hsts
   - Firefox: about:preferences#privacy → 清除数据

步骤4：验证安装
1. 打开命令提示符
2. 运行：certutil -store Root | findstr "Cheese Intelligence"
3. 应该看到根CA证书信息

如果仍有问题：
1. 重启电脑
2. 使用不同浏览器测试
3. 检查系统时间是否正确

技术支持：Cheese Intelligence Team
