# 🎨 Replicate AI 图像生成器

一个基于 Replicate API 的现代化 Web 图像生成应用，支持文字生图和图生图功能。

## ✨ 功能特点

### 🎯 核心功能
- **文字生图**: 输入文本描述生成精美图像
- **图生图**: 上传最多3张图片进行风格转换
- **多模型支持**: 8个不同的AI模型可选
- **批量处理**: 支持多张图片同时上传

### 🎨 用户界面
- **响应式设计**: 支持手机、平板、电脑
- **玻璃质感**: 现代化毛玻璃UI设计
- **拖拽上传**: 支持拖拽文件上传
- **实时预览**: 图片选择后立即预览

### 📱 图片管理
- **智能画廊**: 分页浏览所有生成的图片
- **一键下载**: 直接下载高质量图片
- **删除管理**: 可选择性删除不需要的图片
- **模型标记**: 显示使用的AI模型信息

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Flask
- Replicate API账户

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/yourusername/replicate-web.git
cd replicate-web
```

2. **安装依赖**
```bash
pip install flask replicate
```

3. **设置API密钥**
```bash
# 方法1：环境变量（推荐）
export REPLICATE_API_TOKEN=your_token_here

# 方法2：创建 .env.local 文件
cp .env.example .env.local
# 然后编辑 .env.local 填入你的API密钥
```

4. **运行应用**
```bash
python app.py
```

5. **访问应用**
打开浏览器访问: http://localhost:8080

## 🎯 支持的AI模型

- **Google Imagen 4** - 高质量输出
- **Ideogram V3 Turbo** - 快速生成  
- **FLUX 1.1 Pro** - 精准控制
- **FLUX Dev** - 实验性功能
- **FLUX Kontext Pro** - 图像编辑专用
- **Google Nano Banana** - 轻量级快速
- **Llama Vision** - 多模态理解
- **Claude 3.5 Sonnet** - 智能生成

## 📁 项目结构

```
replicate-web/
├── app.py              # Flask应用主文件
├── templates/
│   └── index.html      # 前端页面
├── static/
│   ├── css/           # 样式文件
│   ├── js/            # JavaScript文件  
│   └── images/        # 生成的图片存储
├── uploads/           # 临时上传文件
└── README.md          # 项目说明
```

## 🔧 配置说明

在使用前需要：

1. 注册 [Replicate](https://replicate.com) 账户
2. 获取API Token
3. 设置环境变量或直接在代码中配置

## 🌟 特色功能

### 多图上传
支持同时上传最多3张图片，比官方单图限制更强大：
- 拖拽多选支持
- 图片预览网格
- 单独删除功能

### 智能分页
- 每页显示9张图片
- 自动隐藏分页（图片少时）
- 删除后智能页面调整

### 模型切换
- 下拉选择不同AI模型
- 显示模型特点说明
- 自动错误恢复

## 🔐 安全提醒

- API Token不要提交到Git
- 生成的图片注意版权
- 建议使用环境变量存储敏感信息

## 📝 更新日志

- v1.0.0: 基础文字生图功能
- v1.1.0: 添加图生图功能  
- v1.2.0: 多模型支持
- v1.3.0: 图片管理和删除
- v1.4.0: 分页功能
- v1.5.0: 多图片上传支持

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

---

**🎨 享受AI创作的乐趣！**