@echo off
echo ========================================
echo 琥珀引擎SSL证书安装工具
echo ========================================
echo.

echo [1] 安装根CA证书...
certutil -addstore -f "Root" amber-root-ca.crt
if %errorlevel% neq 0 (
    echo ❌ 根CA证书安装失败
    pause
    exit /b 1
)
echo ✅ 根CA证书安装成功
echo.

echo [2] 安装服务器证书...
certutil -addstore -f "CA" amber-server.crt
if %errorlevel% neq 0 (
    echo ⚠️  服务器证书安装失败，继续安装...
)
echo.

echo [3] 清理临时文件...
del amber-*.crt 2>nul
del install-certificates.bat 2>nul

echo ========================================
echo 🎉 证书安装完成！
echo ========================================
echo.
echo 请执行以下步骤：
echo 1. 完全关闭所有浏览器窗口
echo 2. 重新打开浏览器
echo 3. 访问 https://finance.cheese.ai
echo.
echo 如果仍有警告，请尝试：
echo 1. 重启电脑
echo 2. 清除浏览器SSL状态缓存
echo.
pause
