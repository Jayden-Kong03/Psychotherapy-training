# 🚀 如何将系统变成可分享的链接

## 📋 完整步骤（从0到分享）

### 方案A：Streamlit Cloud（最简单，推荐）⭐

#### 第1步：准备代码
你的项目应该包含这些文件：
```
workspace/projects/
├── app.py                          # ✅ Streamlit应用（已创建）
├── config/
│   └── agent_llm_config.json       # ✅ 智能体配置
├── src/                            # ✅ 源代码目录
│   ├── agents/agent.py
│   ├── tools/
│   └── storage/database/
├── requirements.txt                # ✅ 依赖列表（已添加streamlit）
├── start.sh                        # ✅ Linux/Mac启动脚本
├── start.bat                       # ✅ Windows启动脚本
└── README_WEB.md                   # ✅ Web版README
```

#### 第2步：上传到GitHub

**选项1：使用GitHub网页**
1. 访问 [https://github.com/new](https://github.com/new)
2. 创建新仓库，命名为 `psychotherapy-training`
3. 上传所有文件

**选项2：使用命令行**
```bash
cd /workspace/projects

# 初始化Git仓库
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: Psychotherapy training system"

# 添加远程仓库
git remote add origin https://github.com/你的用户名/psychotherapy-training.git

# 推送到GitHub
git push -u origin main
```

#### 第3步：部署到Streamlit Cloud

1. **访问Streamlit Cloud**
   - 打开 [https://share.streamlit.io](https://share.streamlit.io)
   - 点击 "Sign in" 并使用GitHub账号登录

2. **创建新应用**
   - 点击 "New app" 按钮
   - 选择你的GitHub仓库：`你的用户名/psychotherapy-training`
   - 选择主文件：`app.py`
   - 应用名称：例如 `psychotherapy-training`
   - 点击 "Deploy"

3. **等待部署**
   - 通常需要1-3分钟
   - 部署成功后会显示应用状态

4. **获取分享链接**
   ```
   https://psychotherapy-training.streamlit.app
   ```

#### 第4步：配置环境变量（重要！）

在Streamlit Cloud的应用设置中：

1. 点击应用名称进入设置
2. 找到 "Secrets" 或 "Environment variables"
3. 添加以下环境变量：

| 变量名 | 值 |
|--------|-----|
| `COZE_WORKLOAD_IDENTITY_API_KEY` | 你的API密钥 |
| `COZE_INTEGRATION_MODEL_BASE_URL` | 模型基础URL |
| `SUPABASE_URL` | 你的Supabase URL |
| `SUPABASE_KEY` | 你的Supabase密钥 |

4. 点击 "Save"
5. 重新部署应用（点击 "Rerun"）

#### 第5步：测试和分享

1. **测试应用**
   - 访问你的分享链接
   - 输入"开始新的咨询"测试
   - 确认功能正常

2. **分享链接**
   - 复制分享链接
   - 发送给其他人
   - 任何人都可以通过浏览器访问！

---

### 方案B：Hugging Face Spaces（备选）🤗

#### 第1步：创建Space

1. 访问 [https://huggingface.co/spaces](https://huggingface.co/spaces)
2. 点击 "Create new Space"
3. 填写信息：
   - **Owner**：选择你的账号
   - **Space name**：例如 `psychotherapy-training`
   - **License**：选择合适的许可证（如MIT）
   - **SDK**：选择 "Streamlit"
   - **Public**：勾选（使公开可见）

#### 第2步：上传文件

**选项1：网页上传**
1. 在Space页面，点击 "Files" 标签
2. 点击 "Upload files"
3. 上传所有项目文件

**选项2：Git上传**
```bash
git clone https://huggingface.co/spaces/你的用户名/psychotherapy-training
cd psychotherapy-training
# 复制所有项目文件到这个目录
git add .
git commit -m "Upload project"
git push
```

#### 第3步：配置环境变量

1. 在Space页面，点击 "Settings" 标签
2. 找到 "Variables and secrets"
3. 添加环境变量（同方案A）

#### 第4步：获取分享链接

部署完成后，分享链接为：
```
https://huggingface.co/spaces/你的用户名/psychotherapy-training
```

---

### 方案C：自托管（需要服务器）🖥️

#### 第1步：准备服务器

- 购买云服务器（阿里云、腾讯云、AWS等）
- 安装Docker和Docker Compose

#### 第2步：部署应用

上传项目到服务器，然后：

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f
```

#### 第3步：配置域名（可选）

购买域名并配置DNS指向服务器IP

#### 第4步：获取分享链接

```
https://你的域名
```

---

## 🎯 快速测试（本地）

在部署到云端之前，你可以先在本地测试：

### Linux/Mac
```bash
cd /workspace/projects
./start.sh
```

### Windows
```bash
双击运行 start.bat
```

或者直接运行：
```bash
streamlit run app.py
```

访问：`http://localhost:8501`

---

## 📱 分享示例

部署成功后，你会得到一个公开链接，例如：

**Streamlit Cloud示例：**
```
https://psychotherapy-training.streamlit.app
```

你可以：
1. ✅ 复制链接发送给朋友
2. ✅ 在社交媒体上分享
3. ✅ 嵌入到网页中
4. ✅ 通过二维码访问

---

## ⚠️ 重要提示

### 1. 环境变量必须设置
**没有环境变量，应用将无法运行！**

### 2. API成本监控
- 关注API调用次数
- 设置预算提醒
- 避免恶意访问

### 3. 数据隐私
- 确保Supabase连接安全
- 考虑添加访问控制
- 定期备份数据

### 4. 域名配置（可选）
如果需要自定义域名：
- 购买域名
- 在部署平台配置CNAME
- 等待DNS生效

---

## 🛠️ 故障排查

### 问题1：部署失败
- 检查 `requirements.txt` 是否完整
- 查看部署日志
- 确保所有依赖已列出

### 问题2：应用无法启动
- 检查环境变量是否正确
- 查看错误日志
- 确认数据库连接正常

### 问题3：功能异常
- 检查API密钥是否有效
- 确认Supabase配置正确
- 查看浏览器控制台错误

---

## 📞 获取帮助

如果遇到问题：
1. 查看 [Streamlit文档](https://docs.streamlit.io)
2. 查看 [Hugging Face文档](https://huggingface.co/docs/hub/spaces)
3. 在GitHub提交Issue

---

## 🎉 完成！

一旦部署成功，你就拥有了一个：
- ✅ 可公开访问的Web应用
- ✅ 无需安装即可使用
- ✅ 可以分享给任何人
- ✅ 支持多用户同时使用

现在，复制分享链接，开始你的心理咨询模拟训练之旅吧！🧠✨
