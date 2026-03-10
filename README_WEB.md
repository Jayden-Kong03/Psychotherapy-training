# 🧠 心理咨询模拟训练系统

一个基于动力学和客体关系取向的心理咨询模拟训练平台，支持多种中国国情心理疾病的模拟训练和督导分析。

## ✨ 功能特点

- 🎭 **真实来访者模拟**：支持抑郁、焦虑、PTSD、双相、强迫症5种常见心理疾病
- 🔄 **情绪动态变化**：根据咨询师回应类型（共情/挑战/支持/提问）实时计算病人情绪
- 📊 **动力学督导分析**：基于弗洛伊德、克莱因、温尼科特等经典理论的专业督导
- 💾 **数据库存储**：使用Supabase存储咨询记录和来访者信息
- 🌐 **Web界面**：简洁易用的Streamlit界面，可在线访问

## 🚀 快速开始

### 本地运行

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动应用
streamlit run app.py
```

应用将在 `http://localhost:8501` 启动

### 在线部署

#### 🌟 推荐方式：Streamlit Cloud（最简单）

1. **上传到GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <你的GitHub仓库地址>
   git push -u origin main
   ```

2. **部署到Streamlit Cloud**
   - 访问 [https://share.streamlit.io](https://share.streamlit.io)
   - 点击 "New app"
   - 选择你的GitHub仓库和 `app.py`
   - 点击 "Deploy"

3. **获取分享链接**
   - 部署完成后，你会得到一个公开链接，例如：
   ```
   https://your-app-name.streamlit.app
   ```

#### 🤗 备选方式：Hugging Face Spaces

1. 访问 [https://huggingface.co/spaces](https://huggingface.co/spaces)
2. 创建新的Space，选择 "Streamlit" SDK
3. 上传所有文件
4. 自动部署，获取分享链接

详细部署指南请查看 [DEPLOYMENT.md](DEPLOYMENT.md)

## 💡 使用说明

### 开始新咨询
在输入框中输入：
```
开始新的咨询
```
系统会随机生成一个来访者（抑郁、焦虑、PTSD、双相、强迫症）

### 继续之前的咨询
在输入框中输入：
```
继续咨询
```
系统会继续上一次的来访者，模拟一周后的第二次咨询

### 正常对话
直接输入咨询师的话，系统会：
- 自动识别回应类型（共情/挑战/支持/提问）
- 动态计算病人情绪变化
- 生成符合症状的回应

### 结束咨询并督导
在输入框中输入：
```
结束咨询，请督导分析
```
系统会：
- 模拟来访者离开场景
- 生成动力学取向的督导报告
- 引用经典理论文献

## 📁 项目结构

```
.
├── app.py                          # Streamlit Web应用
├── config/
│   └── agent_llm_config.json       # 智能体配置
├── src/
│   ├── agents/
│   │   └── agent.py                # 核心智能体逻辑
│   ├── tools/
│   │   ├── consultation_db.py      # 数据库操作
│   │   ├── academic_search.py      # 学术文献检索
│   │   └── dialogue_record.py      # 对话记录
│   └── storage/
│       └── database/
│           ├── model.py            # 数据库模型
│           └── supabase_client.py  # Supabase客户端
├── tests/
│   └── test_advanced_consultation.py  # 测试脚本
├── requirements.txt                # 依赖列表
├── DEPLOYMENT.md                   # 部署指南
└── README.md                       # 本文件
```

## 🎓 来访者档案

### 抑郁症
- **姓名**：张丽，29岁，互联网产品经理
- **症状**：情绪低落、兴趣丧失、失眠、自我责备
- **动力学概念化**：严厉超我与真实自我需求的冲突

### 焦虑症
- **姓名**：王强，31岁，金融分析师
- **症状**：广泛性焦虑、担忧、心悸、坐立不安
- **动力学概念化**：安全感需求与现实不确定性的冲突

### PTSD
- **姓名**：李梅，35岁，教师
- **症状**：创伤后应激、闪回、回避、情感麻木
- **动力学概念化**：创伤记忆的整合与解离

### 双相情感障碍
- **姓名**：陈浩，27岁，自由职业者
- **症状**：情绪波动剧烈、抑郁期和轻躁狂交替
- **动力学概念化**：抑郁期自我贬低与轻躁狂期夸大幻想的冲突

### 强迫症
- **姓名**：刘芳，33岁，会计
- **症状**：强迫性检查、反复确认、仪式化行为
- **动力学概念化**：控制需求与无法控制的焦虑

## 📊 督导分析框架

基于动力学理论，督导报告包含：

1. **个案动力学概念化**
   - 核心心理冲突
   - 主要防御机制
   - 客体关系模式
   - 移情表现

2. **咨询技术评估**
   - 动力学技术运用
   - 移情与反移情处理
   - 解释时机和深度
   - 边界维护

3. **文献理论支撑**
   - 引用弗洛伊德、克莱因、温尼科特等经典理论
   - 仅引用已发表的学术论文和著作

4. **优点与不足**
5. **专业建议**

## 🔐 环境变量配置

部署时需要设置以下环境变量：

```bash
COZE_WORKLOAD_IDENTITY_API_KEY=your_api_key
COZE_INTEGRATION_MODEL_BASE_URL=your_base_url
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

## 🌍 分享链接

部署成功后，你会得到一个公开的分享链接：

- **Streamlit Cloud**：`https://your-app-name.streamlit.app`
- **Hugging Face**：`https://huggingface.co/spaces/your-username/your-space`
- **自托管**：`https://therapy.yourdomain.com`

## 📝 注意事项

1. **仅供专业训练使用**：本系统为心理咨询师专业训练设计
2. **保密性**：部署时注意数据隐私保护
3. **API成本**：注意监控API调用次数
4. **版本更新**：定期更新依赖和代码

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 提交GitHub Issue
- 发送邮件到项目维护者

---

**愿这个系统能帮助更多的咨询师成长！** 🧠✨
