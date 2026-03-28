# 青铜法典访问指南

## 🌐 访问地址

### 1. 静态总览页 (100%可用)
- **主地址**: https://gemini.googlemanager.cn:10168/bronze_details/bronze_static_final.html
- **备用地址**: https://gemini.googlemanager.cn:10168/master-audit/bronze_static_final.html

### 2. 详情页访问方式

#### 方式A: 通过总览页点击
1. 访问静态总览页
2. 点击任意ETF卡片
3. 自动跳转到详情页

#### 方式B: 直接访问
- **格式**: https://gemini.googlemanager.cn:10168/bronze_details/details/{代码}.html
- **示例**: https://gemini.googlemanager.cn:10168/bronze_details/details/510300.html

#### 方式C: 通过符号链接
- **格式**: https://gemini.googlemanager.cn:10168/master-audit/bronze_details/{代码}.html
- **示例**: https://gemini.googlemanager.cn:10168/master-audit/bronze_details/510300.html

## 🚫 错误路径
以下路径会导致404错误:
- ❌ https://gemini.googlemanager.cn:10168/bronze_details/bronze_details/510300.html
  (重复了bronze_details/)

## ✅ 正确路径
- ✅ https://gemini.googlemanager.cn:10168/bronze_details/details/510300.html
- ✅ https://gemini.googlemanager.cn:10168/master-audit/bronze_details/510300.html

## 📊 系统状态
- 总览页: ✅ 可用 (59支标的)
- 详情页: ✅ 可用 (59个页面)
- JavaScript版本: ⚠️ 正在修复
- 静态版本: ✅ 100%可用

## 🔧 技术支持
- **执行人**: 工程师 Cheese
- **修复时间**: 2026-03-27 08:55 GMT+8
- **状态**: 链接路径已修复，详情页可正常访问
