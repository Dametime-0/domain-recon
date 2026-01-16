# DomainRecon
基于 Python + Requests 的轻量级域名信息收集工具，专为新手设计，支持子域名扫描、自定义端口扫描、页面标题爬取，支持代理和多格式结果导出。

## 🌟 核心功能
- ✅ 子域名字典爆破（支持自定义字典）
- ✅ 自定义端口扫描（默认扫描 80/443/22 等常见端口）
- ✅ 自动获取页面标题（多层解析兜底，适配99%网站）
- ✅ 代理支持（避免 IP 被封）
- ✅ 多格式结果导出（TXT/JSON/CSV）
- ✅ 彩色终端输出 + 扫描进度条（新手友好）
- ✅ 轻量级无重型依赖（核心仅需 requests/colorama/tqdm）

## 📦 安装
### 1. 克隆仓库
```bash
git clone https://github.com/你的GitHub用户名/domain-recon.git
cd domain-recon
```

### 2. 安装依赖(必选)
```bash
pip install requests colorama tqdm
```
### 3. 安装依赖(可选)
```bash
# lxml解析器（比Python内置解析器更快，可选）
pip install lxml
```

## 🚀 使用教程
### 基础使用（默认端口 + TXT 输出）
```bash
python run.py -d baidu.com
```

### 自定义端口 + JSON 导出
```bash
python run.py -d baidu.com -p 80,443,8080 -o baidu_result.json -f json
```

### 代理扫描 + CSV 导出
```bash
python run.py -d baidu.com --proxy http://127.0.0.1:8080 -o baidu_result.csv -f csv
```

### 自定义子域名字典
```bash
python run.py -d baidu.com -w my_subdomains.txt -o baidu_result.txt
```

### 参数说明
```plaintext
参数	       必选	  说明	                      示例
-d/--domain	是	目标域名	                  -d baidu.com
-w/--wordlist	否	子域名字典路径	          -w my_subdomains.txt
-o/--output	否	结果保存文件	          -o result.txt
-p/--ports	否	自定义扫描端口（逗号分隔）  -p 80,443,8080
-f/--format	否	输出格式（txt/json/csv）	  -f json
--proxy	        否      代理地址	                  --proxy http://127.0.0.1:8080
```

### ❓ 常见问题（FAQ）
Q1: 为什么 m.baidu.com 显示 No Title？

A1: 百度移动端域名（m.baidu.com）的标题由 JavaScript 动态渲染，静态解析无法获取，属于正常现象。PC 端域名（www.baidu.com）可正常解析。

Q2: 扫描时提示 SSL 警告？

A2: 脚本已内置关闭 SSL 证书验证警告的逻辑，该警告不影响使用，无需处理。

### 📸 效果截图
![脚本运行效果](https://github.com/你的GitHub用户名/domain-recon/raw/main/screenshot.png)

### ⚠️ 免责声明
本工具仅用于学习和合法的安全测试，禁止用于未经授权的扫描。使用本工具造成的一切后果，由使用者自行承担。

### 📄 许可证
本项目采用 MIT 许可证 - 详见 LICENSE 文件。

### ✨ 贡献
欢迎提 Issue 或 Pull Request 来完善这个工具！

