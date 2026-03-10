"""
心理咨询模拟训练系统 - Web界面
使用Streamlit构建可分享的Web应用
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import asyncio
import json
from datetime import datetime
from src.agents.agent import run_consultation_session

# 页面配置
st.set_page_config(
    page_title="心理咨询模拟训练系统",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-container {
        max-height: 600px;
        overflow-y: auto;
        padding: 1rem;
        border: 1px solid #ddd;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .message-counselor {
        background-color: #e3f2fd;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
        border-left: 4px solid #2196f3;
    }
    .message-patient {
        background-color: #fce4ec;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
        border-left: 4px solid #e91e63;
    }
    .emotion-tag {
        display: inline-block;
        padding: 0.2rem 0.5rem;
        border-radius: 5px;
        font-size: 0.8rem;
        margin-left: 0.5rem;
    }
    .emotion-low {
        background-color: #ff9800;
        color: white;
    }
    .emotion-anxiety {
        background-color: #f44336;
        color: white;
    }
    .session-info {
        background-color: #f5f5f5;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .supervision-report {
        background-color: #e8f5e9;
        padding: 1.5rem;
        border-radius: 10px;
        margin-top: 1rem;
        border-left: 4px solid #4caf50;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffc107;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# 初始化session state
if 'user_id' not in st.session_state:
    st.session_state.user_id = f"user_{datetime.now().strftime('%Y%m%d%H%M%S')}"

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'session_id' not in st.session_state:
    st.session_state.session_id = None

if 'visitor_info' not in st.session_state:
    st.session_state.visitor_info = None

if 'message_order' not in st.session_state:
    st.session_state.message_order = 0

if 'current_emotion' not in st.session_state:
    st.session_state.current_emotion = None

if 'disorder_type' not in st.session_state:
    st.session_state.disorder_type = None

if 'is_ended' not in st.session_state:
    st.session_state.is_ended = False

if 'profile_data' not in st.session_state:
    st.session_state.profile_data = None

# 侧边栏
with st.sidebar:
    st.header("🧠 心理咨询模拟训练")
    st.markdown("---")
    
    st.subheader("系统说明")
    st.info("""
    **使用方式：**
    1. 输入"开始新的咨询"创建新来访者
    2. 输入"继续咨询"恢复之前的咨询
    3. 正常对话进行咨询练习
    4. 输入"结束咨询"进行督导分析
    """)
    
    st.markdown("---")
    
    if st.session_state.visitor_info:
        st.subheader("📋 来访者信息")
        st.markdown(f"""
        **姓名：** {st.session_state.visitor_info.get('name', '未知')}
        
        **症状类型：** {st.session_state.visitor_info.get('disorder_type', '未知')}
        
        **咨询次数：** 第{st.session_state.visitor_info.get('session_number', 0)}次
        """)
        
        if st.session_state.current_emotion:
            st.markdown(f"**当前情绪：** {st.session_state.current_emotion}")
    
    st.markdown("---")
    
    if st.session_state.is_ended:
        st.warning("本次咨询已结束")
        if st.button("🔄 开始新咨询"):
            st.session_state.session_id = None
            st.session_state.visitor_info = None
            st.session_state.messages = []
            st.session_state.message_order = 0
            st.session_state.current_emotion = None
            st.session_state.disorder_type = None
            st.session_state.is_ended = False
            st.session_state.profile_data = None
            st.rerun()

# 主界面
st.markdown('<div class="main-header">🧠 心理咨询模拟训练系统</div>', unsafe_allow_html=True)

st.markdown("---")

# 显示对话历史
if st.session_state.messages:
    st.subheader("💬 对话记录")
    
    for msg in st.session_state.messages:
        if msg['role'] == 'counselor':
            st.markdown(f"""
            <div class="message-counselor">
                <strong>咨询师：</strong>{msg['content']}
            </div>
            """, unsafe_allow_html=True)
        else:
            emotion_html = f'<span class="emotion-tag">{msg.get("emotion", "")}</span>' if msg.get('emotion') else ''
            st.markdown(f"""
            <div class="message-patient">
                <strong>病人：</strong>{msg['content']}{emotion_html}
            </div>
            """, unsafe_allow_html=True)

# 督导报告
if 'supervision_report' in st.session_state:
    st.markdown("---")
    st.subheader("📊 督导分析报告")
    st.markdown(f'<div class="supervision-report">{st.markdown(st.session_state.supervision_report)}</div>', unsafe_allow_html=True)

# 输入区域
if not st.session_state.is_ended:
    st.markdown("---")
    st.subheader("💭 输入区域")
    
    # 快捷按钮
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🆕 开始新咨询"):
            user_input = "开始新的咨询"
    
    with col2:
        if st.button("➡️ 继续咨询"):
            user_input = "继续咨询"
    
    with col3:
        if st.button("❓ 示例回应"):
            user_input = "我理解你现在的心情，能多跟我说说你的感受吗？"
    
    with col4:
        if st.button("🏁 结束咨询"):
            user_input = "结束咨询，请督导分析"
    
    # 文本输入
    user_input = st.text_area(
        "咨询师输入",
        placeholder="请输入您的话...",
        height=100,
        key="user_input"
    )
    
    # 发送按钮
    if st.button("📤 发送", type="primary"):
        if user_input.strip():
            # 添加咨询师消息到历史
            st.session_state.messages.append({
                'role': 'counselor',
                'content': user_input
            })
            
            # 显示处理中
            with st.spinner("正在处理..."):
                try:
                    # 调用咨询会话
                    result = asyncio.run(run_consultation_session(
                        user_id=st.session_state.user_id,
                        user_message=user_input,
                        session_id=st.session_state.session_id,
                        message_order=st.session_state.message_order,
                        current_emotion=st.session_state.current_emotion,
                        disorder_type=st.session_state.disorder_type,
                        profile_data=st.session_state.profile_data
                    ))
                    
                    if result['phase'] == 'error':
                        st.error(result['response'])
                    elif result['phase'] == 'patient':
                        # 更新状态
                        st.session_state.session_id = result.get('session_id')
                        st.session_state.message_order = result.get('message_order', 0)
                        st.session_state.current_emotion = result.get('emotion')
                        
                        # 如果是第一次或继续咨询，更新来访者信息
                        if 'visitor_name' in result:
                            st.session_state.visitor_info = {
                                'name': result['visitor_name'],
                                'disorder_type': result['disorder_type'],
                                'session_number': result['session_number']
                            }
                            st.session_state.disorder_type = result['disorder_type']
                            # 注意：这里需要profile_data，但由于是从数据库获取的，需要特殊处理
                        
                        # 添加病人消息到历史
                        st.session_state.messages.append({
                            'role': 'patient',
                            'content': result['response'],
                            'emotion': result.get('emotion', '')
                        })
                        
                    elif result['phase'] == 'supervision':
                        # 督导报告
                        st.session_state.supervision_report = result['response']
                        st.session_state.is_ended = True
                        
                        # 添加离开场景
                        if 'departure_scene' in result:
                            st.session_state.messages.append({
                                'role': 'system',
                                'content': f"离开场景：{result['departure_scene']['description']}",
                                'emotion': result['departure_scene'].get('type', '')
                            })
                    
                    # 清空输入
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"处理失败：{str(e)}")
                    import traceback
                    st.error(traceback.format_exc())
else:
    st.markdown("---")
    st.warning("本次咨询已结束，请点击侧边栏的'开始新咨询'按钮重新开始")

# 页脚
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    心理咨询模拟训练系统 | 动力学取向 | 仅供专业训练使用
</div>
""", unsafe_allow_html=True)
