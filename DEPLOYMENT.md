# 心理咨询模拟训练系统 - 部署指南

## 本地运行

### 1. 安装依赖
```bash
pip install streamlit
```

### 2. 启动应用
```bash
streamlit run app.py
```

应用将在 `http://localhost:8501` 启动

## 在线部署（推荐）

### 方式1：Streamlit Cloud（最简单）

#### 步骤1：准备代码
确保你的项目包含以下文件：
```
.
├── app.py                          # Streamlit应用主文件
├── src/                            # 源代码目录
│   ├── agents/agent.py
│   ├── tools/
│   └── storage/database/
├── config/agent_llm_config.json
├── requirements.txt                # 依赖列表
└── README.md
```

#### 步骤2：创建requirements.txt
```bash
pip freeze > requirements.txt
```

确保包含以下核心依赖：
```
streamlit
langchain
langgraph
langchain-openai
coze-coding-dev-sdk
sqlalchemy
psycopg2-binary
```

#### 步骤3：上传到GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <你的GitHub仓库地址>
git push -u origin main
```

#### 步骤4：部署到Streamlit Cloud
1. 访问 [https://share.streamlit.io](https://share.streamlit.io)
2. 点击 "New app"
3. 选择你的GitHub仓库
4. 选择 `app.py` 作为主文件
5. 点击 "Deploy"

几分钟后，你会得到一个公开的分享链接，类似：
```
https://your-app-name.streamlit.app
```

### 方式2：Hugging Face Spaces

#### 步骤1：创建Space
1. 访问 [https://huggingface.co/spaces](https://huggingface.co/spaces)
2. 点击 "Create new Space"
3. 选择 "Streamlit" SDK
4. 命名你的Space

#### 步骤2：上传文件
通过Git上传或直接在网页上上传文件：
- app.py
- src/ 目录
- config/ 目录
- requirements.txt

#### 步骤3：设置环境变量（如果需要）
在Space的Settings → Variables中设置：
- `COZE_WORKLOAD_IDENTITY_API_KEY`: 你的API密钥
- `COZE_INTEGRATION_MODEL_BASE_URL`: 模型基础URL

#### 步骤4：获取分享链接
Space构建完成后，你会得到一个公开链接，类似：
```
https://huggingface.co/spaces/your-username/your-space-name
```

### 方式3：自托管服务器

#### 使用Docker部署

创建 `Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

创建 `docker-compose.yml`:
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - COZE_WORKLOAD_IDENTITY_API_KEY=${API_KEY}
      - COZE_INTEGRATION_MODEL_BASE_URL=${BASE_URL}
```

启动：
```bash
docker-compose up -d
```

访问：`http://your-server-ip:8501`

## 环境变量配置

在部署时，需要设置以下环境变量：

| 环境变量 | 说明 | 必填 |
|---------|------|------|
| `COZE_WORKLOAD_IDENTITY_API_KEY` | API密钥 | 是 |
| `COZE_INTEGRATION_MODEL_BASE_URL` | 模型基础URL | 是 |
| `COZE_WORKSPACE_PATH` | 工作目录路径 | 否（默认自动设置） |
| `SUPABASE_URL` | Supabase数据库URL | 是 |
| `SUPABASE_KEY` | Supabase密钥 | 是 |

## 访问控制

### 公开访问
默认情况下，部署的应用是公开的，任何人都可以访问。

### 密码保护
如果需要密码保护，可以在 `app.py` 中添加：

```python
import streamlit as st

# 密码保护
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("密码", type="password", on_change=password_entered, key="password")
        if "password_correct" in st.session_state:
            if not st.session_state["password_correct"]:
                st.error("密码错误")
        return False
    
    return True

if not check_password():
    st.stop()  # 停止执行
```

## 域名配置

### 自定义域名（Streamlit Cloud）
1. 在Streamlit Cloud的应用设置中
2. 点击 "Custom domain"
3. 添加你的域名（如 `therapy.yourdomain.com`）
4. 按照提示配置DNS

### 自定义域名（Hugging Face Spaces）
1. 在Space的Settings中
2. 添加自定义域名
3. 配置DNS CNAME记录

## 性能优化

### 1. 启用缓存
在 `app.py` 中添加：
```python
@st.cache_data(ttl=3600)
def get_visitor_info(user_id):
    # 缓存来访者信息
    pass
```

### 2. 使用异步处理
```python
import asyncio

@st.experimental_fragment
async def handle_async_operation():
    # 异步处理
    pass
```

### 3. 优化数据库查询
- 使用索引
- 限制返回的数据量
- 使用连接池

## 监控和日志

### Streamlit Cloud
- 在应用设置中查看访问日志
- 使用Streamlit的内置监控工具

### 自托管
- 使用 `st.logger` 记录日志
- 配置外部日志服务（如Sentry）

## 分享链接示例

部署成功后，你会得到类似以下的分享链接：

- Streamlit Cloud: `https://psychotherapy-training.streamlit.app`
- Hugging Face: `https://huggingface.co/spaces/your-username/psychotherapy-training`
- 自托管: `https://therapy.yourdomain.com`

## 注意事项

1. **API密钥安全**：不要在代码中硬编码API密钥，使用环境变量或密钥管理服务
2. **数据隐私**：确保数据库连接使用SSL/TLS加密
3. **访问控制**：如果涉及敏感数据，考虑添加身份验证
4. **成本控制**：监控API调用次数，避免超支
5. **合规性**：确保符合相关法律法规（如数据保护法）

## 故障排查

### 问题1：应用无法启动
- 检查 `requirements.txt` 是否完整
- 查看错误日志
- 确保所有依赖已正确安装

### 问题2：数据库连接失败
- 检查环境变量是否正确设置
- 确认数据库URL格式正确
- 验证数据库访问权限

### 问题3：API调用失败
- 检查API密钥是否有效
- 确认API额度是否充足
- 查看API返回的错误信息

## 技术支持

如遇到问题，可以：
1. 查看 [Streamlit文档](https://docs.streamlit.io)
2. 访问 [Hugging Face社区](https://huggingface.co/spaces)
3. 在GitHub上提交Issue
