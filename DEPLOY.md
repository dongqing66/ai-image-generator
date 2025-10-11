# 🚀 部署指南

本文档提供详细的部署步骤，帮助你将 AI 图像生成器部署到各个免费云平台。

---

## 📋 部署前准备

### 1. 获取 Replicate API Token

1. 访问 https://replicate.com
2. 注册/登录账号
3. 进入 https://replicate.com/account/api-tokens
4. 创建 API Token 并复制保存

### 2. 确保代码已提交到 Git

```bash
git add .
git commit -m "准备部署"
git push origin main
```

---

## 🎯 方式一：Render 部署（推荐）

**优点**：完全免费、配置简单、自动HTTPS、持久化存储

### 步骤：

1. **创建账号**
   - 访问 https://render.com
   - 使用 GitHub 账号登录

2. **创建新服务**
   - 点击 "New +" → "Web Service"
   - 连接你的 GitHub 仓库
   - 选择这个项目

3. **配置服务**
   ```
   Name: ai-image-generator
   Region: Oregon (US West) 或选择最近的
   Branch: main
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn app:app
   ```

4. **设置环境变量**
   点击 "Environment" 标签，添加：
   ```
   REPLICATE_API_TOKEN = 你的实际token
   FLASK_ENV = production
   SECRET_KEY = 生成一个随机字符串
   ```

5. **选择免费计划**
   - Instance Type: Free
   - 点击 "Create Web Service"

6. **等待部署**
   - 首次部署需要 3-5 分钟
   - 完成后会显示你的网站URL：`https://your-app.onrender.com`

### 注意事项：
- 免费版闲置 15 分钟后会休眠
- 首次访问可能需要 30 秒启动时间
- 每月 750 小时免费使用

---

## 🎯 方式二：Railway 部署

**优点**：界面友好、部署快速、自动构建

### 步骤：

1. **创建账号**
   - 访问 https://railway.app
   - 使用 GitHub 登录

2. **创建新项目**
   - 点击 "New Project"
   - 选择 "Deploy from GitHub repo"
   - 授权并选择你的仓库

3. **配置环境变量**
   点击项目 → Settings → Variables，添加：
   ```
   REPLICATE_API_TOKEN = 你的token
   FLASK_ENV = production
   SECRET_KEY = 随机字符串
   ```

4. **自动部署**
   - Railway 会自动检测 Python 项目
   - 自动运行 requirements.txt
   - 自动分配域名

5. **查看网站**
   - 点击 "Settings" → "Domains"
   - 会显示类似 `your-app.up.railway.app` 的URL

### 注意事项：
- 新用户有 $5 免费额度
- 额度用完需要绑定信用卡（不会扣费）

---

## 🎯 方式三：Fly.io 部署

**优点**：性能好、全球CDN、支持持久化存储

### 步骤：

1. **安装 Fly CLI**
   ```bash
   # macOS
   brew install flyctl

   # Linux
   curl -L https://fly.io/install.sh | sh

   # Windows
   powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
   ```

2. **登录 Fly.io**
   ```bash
   flyctl auth login
   ```

3. **初始化项目**（项目已有 fly.toml，跳过此步骤）
   ```bash
   flyctl launch
   ```

4. **设置环境变量**
   ```bash
   flyctl secrets set REPLICATE_API_TOKEN=你的token
   flyctl secrets set FLASK_ENV=production
   flyctl secrets set SECRET_KEY=随机字符串
   ```

5. **部署**
   ```bash
   flyctl deploy
   ```

6. **查看网站**
   ```bash
   flyctl open
   ```

### 注意事项：
- 需要信用卡验证（不会扣费）
- 免费额度：3个应用 + 160GB流量/月

---

## 🎯 方式四：Docker 部署（适合自己的服务器）

如果你有自己的 VPS 或服务器：

### 步骤：

1. **构建镜像**
   ```bash
   docker build -t ai-image-generator .
   ```

2. **运行容器**
   ```bash
   docker run -d \
     -p 8080:8080 \
     -e REPLICATE_API_TOKEN=你的token \
     -e FLASK_ENV=production \
     -e SECRET_KEY=随机字符串 \
     -v $(pwd)/static/images:/app/static/images \
     --name ai-generator \
     ai-image-generator
   ```

3. **访问**
   ```
   http://你的服务器IP:8080
   ```

---

## 🔧 部署后配置

### 1. 绑定自定义域名

**Render**:
- Settings → Custom Domain → 添加域名
- 在 DNS 提供商处添加 CNAME 记录

**Railway**:
- Settings → Domains → Custom Domain
- 添加 CNAME 记录到 Railway 提供的地址

**Fly.io**:
```bash
flyctl certs add yourdomain.com
```

### 2. 配置 HTTPS

所有推荐的平台都自动提供免费 HTTPS 证书（Let's Encrypt）

### 3. 监控和日志

**Render**: Dashboard → Logs
**Railway**: 项目页面 → Deployments → View Logs
**Fly.io**:
```bash
flyctl logs
```

---

## 📊 性能对比

| 平台 | 启动速度 | 稳定性 | 免费额度 | 推荐指数 |
|------|---------|--------|---------|---------|
| Render | 慢（冷启动30s） | ⭐⭐⭐⭐ | 750h/月 | ⭐⭐⭐⭐⭐ |
| Railway | 快 | ⭐⭐⭐⭐⭐ | $5 额度 | ⭐⭐⭐⭐ |
| Fly.io | 很快 | ⭐⭐⭐⭐⭐ | 3个应用 | ⭐⭐⭐⭐ |

---

## 🐛 常见问题

### 1. 部署后访问超时

**原因**：冷启动时间过长或内存不足

**解决**：
- 等待 30-60 秒再试
- 升级到付费计划（更多内存）

### 2. API Token 无效

**原因**：环境变量没有正确设置

**解决**：
- 检查环境变量拼写
- 确保 token 没有多余空格
- 重新部署服务

### 3. 图片无法保存

**原因**：免费计划文件系统不持久化

**解决**：
- 使用对象存储（S3, Cloudinary）
- 升级到支持持久化存储的计划

### 4. 内存不足

**原因**：免费计划内存限制（256MB-512MB）

**解决**：
- 减少并发处理数量
- 升级内存配置
- 使用队列系统（Redis + Celery）

---

## 🎉 部署成功检查清单

- [ ] 网站可以正常访问
- [ ] 文字生图功能正常
- [ ] 图生图功能正常
- [ ] 图片可以下载
- [ ] 画廊显示正常
- [ ] HTTPS 工作正常
- [ ] 响应速度可接受

---

## 📞 需要帮助？

如果遇到问题：
1. 查看平台的日志输出
2. 检查环境变量是否正确
3. 确认 API Token 有效
4. 提交 Issue 到 GitHub

祝部署顺利！🎨
