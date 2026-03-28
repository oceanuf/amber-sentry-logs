# 🔗 琥珀引擎001号样板 - 访问指南

## 🎯 快速访问

### 方法1：直接点击链接
**主访问链接**: [http://localhost:8000/stock/601628.html](http://localhost:8000/stock/601628.html)

### 方法2：命令行访问
```bash
# 如果使用curl
curl http://localhost:8000/stock/601628.html

# 如果使用wget
wget -O china_life_sample.html http://localhost:8000/stock/601628.html
```

### 方法3：浏览器手动输入
在浏览器地址栏输入：
```
http://localhost:8000/stock/601628.html
```

## 🌐 网络配置说明

### 本地访问
- **服务器IP**: 127.0.0.1 (localhost)
- **端口**: 8000
- **协议**: HTTP
- **访问范围**: 仅本机访问

### 如果需要外部访问
```bash
# 停止当前服务器
pkill -f "python3 -m http.server 8000"

# 启动允许外部访问的服务器
cd /home/luckyelite/.openclaw/workspace/amber-engine/output
python3 -m http.server 8000 --bind 0.0.0.0
```

外部访问链接: `http://<服务器IP>:8000/stock/601628.html`

## 📱 多设备访问指南

### 同一网络下的其他设备
1. 获取本机IP地址:
   ```bash
   hostname -I
   # 示例输出: 192.168.1.100
   ```

2. 在其他设备浏览器访问:
   ```
   http://192.168.1.100:8000/stock/601628.html
   ```

### 移动设备访问
1. 确保移动设备和服务器在同一WiFi网络
2. 在手机浏览器输入:
   ```
   http://<服务器IP>:8000/stock/601628.html
   ```

## 🔍 页面验证

### 验证服务器状态
```bash
# 检查服务器是否运行
ps aux | grep "python3 -m http.server 8000"

# 检查端口监听
netstat -tlnp | grep 8000

# 测试HTTP响应
curl -I http://localhost:8000/stock/601628.html
# 应返回: HTTP/1.0 200 OK
```

### 验证页面内容
```bash
# 检查页面标题
curl -s http://localhost:8000/stock/601628.html | grep -o "<title>[^<]*</title>"
# 应返回: <title>中国人寿 (601628.SH) - 琥珀引擎财经分析</title>

# 检查关键内容
curl -s http://localhost:8000/stock/601628.html | grep -c "中国人寿"
# 应返回大于0的数字
```

## 🛠️ 故障排除

### 问题1：无法访问页面
```bash
# 解决方案：
# 1. 检查服务器是否运行
ps aux | grep "python3 -m http.server"

# 2. 如果没有运行，重新启动
cd /home/luckyelite/.openclaw/workspace/amber-engine/output
python3 -m http.server 8000 &

# 3. 检查防火墙
sudo ufw status
# 如果需要，允许8000端口
sudo ufw allow 8000
```

### 问题2：端口被占用
```bash
# 解决方案：
# 1. 查找占用8000端口的进程
sudo lsof -i :8000

# 2. 停止占用进程或使用其他端口
python3 -m http.server 8080  # 使用8080端口
```

### 问题3：页面显示异常
```bash
# 解决方案：
# 1. 检查文件是否存在
ls -la /home/luckyelite/.openclaw/workspace/amber-engine/output/stock/601628.html

# 2. 检查文件权限
chmod 644 /home/luckyelite/.openclaw/workspace/amber-engine/output/stock/601628.html

# 3. 查看服务器日志
tail -f /tmp/amber_test.log
```

## 📊 访问统计（可选）

### 启用访问日志
```bash
# 停止当前服务器
pkill -f "python3 -m http.server"

# 启动带详细日志的服务器
cd /home/luckyelite/.openclaw/workspace/amber-engine/output
python3 -m http.server 8000 2>&1 | tee /tmp/amber_access.log
```

### 查看访问记录
```bash
# 实时查看访问日志
tail -f /tmp/amber_access.log

# 统计访问次数
grep -c "GET /stock/601628.html" /tmp/amber_access.log
```

## 🎨 页面功能测试清单

访问页面后，请验证以下功能：

### ✅ 必须验证的项目
1. [ ] 页面正常加载，无错误提示
2. [ ] 标题显示正确：中国人寿 (601628.SH)
3. [ ] 琥珀指标卡显示4个指标
4. [ ] 行情表格显示5行数据
5. [ ] 涨跌颜色正确（红色上涨，绿色下跌）
6. [ ] 所有链接可点击
7. [ ] 页面响应式布局正常

### 🔍 详细验证项目
1. **视觉验证**
   - [ ] V2.2视觉风格一致
   - [ ] 琥珀色主题正确
   - [ ] 字体大小合适
   - [ ] 间距符合25px标准

2. **数据验证**
   - [ ] 股票代码正确：601628.SH
   - [ ] 最新价格：42.73
   - [ ] 涨跌幅：+0.54%
   - [ ] 5日均价：42.29
   - [ ] RICH评分：8.7

3. **功能验证**
   - [ ] 表格排序正确（最新日期在前）
   - [ ] 数字格式正确（两位小数）
   - [ ] 单位转换正确（万手）
   - [ ] 导航链接有效

## 📞 技术支持

### 紧急联系方式
- **服务器状态**: `ps aux | grep "python3 -m http.server"`
- **错误日志**: `/tmp/amber_test.log`
- **页面文件**: `/home/luckyelite/.openclaw/workspace/amber-engine/output/stock/601628.html`

### 重启服务
```bash
# 完整重启流程
pkill -f "python3 -m http.server"
cd /home/luckyelite/.openclaw/workspace/amber-engine/output
python3 -m http.server 8000 > /tmp/amber_test.log 2>&1 &
echo "服务器已重启，访问: http://localhost:8000/stock/601628.html"
```

---

## 🚀 访问成功提示

如果看到以下内容，说明访问成功：

1. **浏览器标题**: "中国人寿 (601628.SH) - 琥珀引擎财经分析"
2. **页面头部**: 大大的"中国人寿"标题和股票代码
3. **琥珀指标卡**: 4个彩色指标卡片
4. **行情表格**: 5行数据表格
5. **分析内容**: 公司概况、核心优势、投资建议

**现在可以开始审核了！** 🎯