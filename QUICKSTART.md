# 🚀 快速部署到 Render（5分钟上线）

这是最简单的部署方式，完全免费，无需信用卡！

---

## 第一步：准备 Replicate API Token

1. 打开 https://replicate.com
2. 注册/登录账号
3. 访问 https://replicate.com/account/api-tokens
4. 点击 "Create token"，复制保存（格式：`r8_xxxxxxxxxxxx`）

---

## 第二步：推送代码到 GitHub

```bash
# 确保你在项目目录
cd /Users/zl/Claude\ code游乐园/ai-image-generator

# 查看状态
git status

# 添加所有修改
git add .

# 提交修改
git commit -m "🚀 准备部署：修复安全漏洞，添加部署配置"

# 推送到 GitHub
git push origin main
```

如果还没有创建 GitHub 仓库：

```bash
# 在 GitHub 上创建新仓库（不要初始化 README）
# 然后执行：
git remote add origin https://github.com/你的用户名/ai-image-generator.git
git branch -M main
git push -u origin main
```

---

## 第三步：部署到 Render

### 1. 注册 Render

- 访问 https://render.com
- 点击 "Get Started for Free"
- 选择 "Sign in with GitHub"（推荐）

### 2. 连接仓库

- 登录后，点击右上角 "New +" → "Web Service"
- 找到你的项目仓库并点击 "Connect"

### 3. 配置服务

填写以下信息：

```
Name: ai-image-generator (或你喜欢的名字)
Region: Oregon (US West) 或其他最近的区域
Branch: main
Runtime: Python 3

Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app

Instance Type: Free
```

### 4. 设置环境变量

在 "Environment Variables" 部分，点击 "Add Environment Variable"：

| Key | Value |
|-----|-------|
| `REPLICATE_API_TOKEN` | 你第一步复制的 token |
| `FLASK_ENV` | `production` |
| `SECRET_KEY` | 随机字符串（如：`my-super-secret-key-2024`） |

> 💡 SECRET_KEY 可以用这个命令生成：`python3 -c "import secrets; print(secrets.token_urlsafe(32))"`

### 5. 开始部署

- 点击底部蓝色按钮 "Create Web Service"
- 等待 3-5 分钟，Render 会自动：
  - 安装依赖
  - 启动服务
  - 分配域名

### 6. 访问你的网站

部署成功后，页面顶部会显示你的网站 URL：

```
https://ai-image-generator-xxxx.onrender.com
```

点击就能访问了！🎉

---

## 常见问题

### ❓ 首次访问很慢怎么办？

**答**：免费版服务闲置 15 分钟后会休眠，第一次访问需要 30-60 秒启动。这是正常的！

### ❓ 如何查看日志？

**答**：在 Render Dashboard → 选择你的服务 → 点击 "Logs" 标签

### ❓ 如何更新代码？

**答**：推送新代码到 GitHub，Render 会自动重新部署：

```bash
git add .
git commit -m "更新功能"
git push
```

### ❓ 能绑定自己的域名吗？

**答**：可以！在 Settings → Custom Domain → 添加域名，然后在你的 DNS 提供商添加 CNAME 记录。

### ❓ 免费版有什么限制？

**答**：
- 750 小时/月运行时间（够用）
- 闲置 15 分钟休眠
- 512MB 内存
- 无持久化存储（图片会定期清空）

---

## 🎉 成功部署检查清单

测试以下功能确保正常：

- [ ] 网站能正常打开
- [ ] 文字生图功能正常
- [ ] 图生图功能正常
- [ ] 图片可以下载
- [ ] 画廊显示正常

全部正常就大功告成了！🎨

---

## 下一步

想要更好的体验？可以考虑：

1. **Railway** - 更快的启动速度，$5 免费额度
2. **Fly.io** - 全球 CDN，性能更好
3. **自己的服务器** - 使用 Docker 部署

详细步骤见 `DEPLOY.md` 文件。

---

需要帮助？检查 Render 的日志输出或提交 Issue！
