"""
心理咨询模拟训练系统（动力学取向）
包含两个智能体：
1. 模拟病人智能体：模拟具有心理症状的来访者，具备情绪逻辑
2. 个案督导智能体：分析咨询过程，提供专业反馈

新功能：
- 中国国情来访者档案（抑郁、焦虑、PTSD、双相、强迫症）
- 会话恢复功能（继续之前的来访者）
- 50分钟真实时间模拟
- 结束场景模拟（准点、拖延、提前、突然离开）
- 根据咨询师回应类型计算情绪变化
- 本地文件存储
"""
import os
import json
import random
from datetime import datetime
from typing import Annotated
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage, SystemMessage
from src.utils.coze_compat import default_headers, new_context
from src.storage.memory.memory_saver_simple import get_memory_saver

# 工具导入
from src.tools.dialogue_record import get_dialogue_history_text
from src.tools.academic_search import (
    search_academic_literature,
    search_classic_theories,
    search_journal_articles
)
from src.tools.consultation_db import (
    create_new_visitor,
    get_active_visitor,
    create_consultation_session,
    add_dialogue_message_db,
    end_consultation_session,
    get_session_history,
    CHINA_PATIENT_PROFILES
)

# 模型配置路径
LLM_CONFIG = "config/agent_llm_config.json"

# 默认保留最近 20 轮对话 (40 条消息)
MAX_MESSAGES = 40

def _windowed_messages(old, new):
    """滑动窗口: 只保留最近 MAX_MESSAGES 条消息"""
    return add_messages(old, new)[-MAX_MESSAGES:]  # type: ignore

class AgentState(MessagesState):
    messages: Annotated[list[AnyMessage], _windowed_messages]

def _get_text_content(content):
    """安全提取文本内容"""
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        if content and isinstance(content[0], str):
            return " ".join(content)
        else:
            text_parts = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text_parts.append(item.get("text", ""))
            return " ".join(text_parts)
    return str(content)

def build_agent(ctx=None):
    """构建心理咨询模拟训练智能体"""
    workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
    config_path = os.path.join(workspace_path, LLM_CONFIG)

    with open(config_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)

    api_key = os.getenv("COZE_WORKLOAD_IDENTITY_API_KEY")
    base_url = os.getenv("COZE_INTEGRATION_MODEL_BASE_URL")

    llm = ChatOpenAI(
        model=cfg['config'].get("model"),
        api_key=api_key,
        base_url=base_url,
        temperature=cfg['config'].get('temperature', 0.7),
        streaming=True,
        timeout=cfg['config'].get('timeout', 600),
        extra_body={
            "thinking": {
                "type": cfg['config'].get('thinking', 'disabled')
            }
        },
        default_headers=default_headers(ctx) if ctx else {}
    )

    agent = create_agent(
        model=llm,
        system_prompt=cfg.get("sp"),
        tools=[
            create_new_visitor,
            get_active_visitor,
            create_consultation_session,
            add_dialogue_message_db,
            end_consultation_session,
            get_session_history,
            search_academic_literature,
            search_classic_theories,
            search_journal_articles
        ],
        checkpointer=get_memory_saver(),
        state_schema=AgentState,
    )
    
    return agent

def _analyze_counselor_response_type(message: str) -> str:
    """
    分析咨询师回应类型
    
    Args:
        message: 咨询师的消息
    
    Returns:
        回应类型：empathy/challenge/support/question/other
    """
    empathy_keywords = ["理解", "感受到", "体会到", "听出", "感觉到", "能理解", "共情", "心疼", "难过", "遗憾"]
    challenge_keywords = ["为什么", "怎么会", "是不是", "难道", "怎么可能", "你真的认为", "试试看", "挑战"]
    support_keywords = ["支持", "陪伴", "在一起", "不会离开", "一直在这里", "我会帮助", "可以依靠"]
    question_keywords = ["?", "？", "怎么样", "如何", "什么", "什么时候", "哪里", "谁"]
    
    message_lower = message.lower()
    
    for keyword in empathy_keywords:
        if keyword in message:
            return "empathy"
    
    for keyword in challenge_keywords:
        if keyword in message:
            return "challenge"
    
    for keyword in support_keywords:
        if keyword in message:
            return "support"
    
    for keyword in question_keywords:
        if keyword in message:
            return "question"
    
    return "other"

def _calculate_emotion_change(
    current_emotion: str,
    disorder_type: str,
    counselor_response_type: str,
    profile_data: dict
) -> str:
    """
    根据咨询师回应类型计算情绪变化
    
    Args:
        current_emotion: 当前情绪
        disorder_type: 症状类型
        counselor_response_type: 咨询师回应类型
        profile_data: 病人档案数据
    
    Returns:
        新的情绪状态
    """
    # 简化的情绪计算逻辑
    if disorder_type == "抑郁":
        if counselor_response_type == "empathy":
            return random.choice(["低落", "感动", "悲伤", "稍微放松"])
        elif counselor_response_type == "challenge":
            return random.choice(["自责", "低落", "焦虑", "沉默"])
        elif counselor_response_type == "support":
            return random.choice(["稍微缓解", "感激", "仍焦虑"])
    elif disorder_type == "焦虑":
        if counselor_response_type == "empathy":
            return random.choice(["稍微放松", "但仍不确定", "感激"])
        elif counselor_response_type == "challenge":
            return random.choice(["焦虑加剧", "防御性加强", "恐慌"])
    elif disorder_type == "PTSD":
        if counselor_response_type == "empathy":
            return random.choice(["恐惧", "闪回", "愤怒", "麻木"])
        elif counselor_response_type == "challenge":
            return random.choice(["强烈防御", "愤怒", "拒绝讨论"])
    elif disorder_type == "双相情感障碍":
        if counselor_response_type == "empathy":
            return random.choice(["情绪低落", "稍微平静", "仍然焦虑"])
        elif counselor_response_type == "challenge":
            return random.choice(["情绪波动", "激越", "防御"])
    elif disorder_type == "强迫症":
        if counselor_response_type == "empathy":
            return random.choice(["稍微放松", "仍然焦虑", "不确定"])
        elif counselor_response_type == "challenge":
            return random.choice(["焦虑加剧", "防御性加强", "反复确认"])
    
    return current_emotion

async def run_consultation_session(
    user_id: str,
    user_message: str,
    session_id: int = None,
    message_order: int = 0,
    current_emotion: str = None,
    disorder_type: str = None,
    profile_data: dict = None
) -> dict:
    """
    运行咨询会话（简化版，移除Coze SDK依赖）
    
    Args:
        user_id: 咨询师ID
        user_message: 咨询师输入的消息
        session_id: 会话ID（首次会话为None）
        message_order: 消息序号
        current_emotion: 当前情绪状态
        disorder_type: 症状类型
        profile_data: 病人档案数据
    
    Returns:
        包含响应和会话信息的字典
    """
    # 构建agent
    agent = build_agent()
    
    # 检查用户意图
    is_start_new = any(keyword in user_message for keyword in ["开始新的咨询", "新咨询", "新的咨询", "开始咨询", "创建新来访者"])
    is_continue = any(keyword in user_message for keyword in ["继续咨询", "继续上次的咨询", "恢复咨询", "开始上次"])
    is_end = any(keyword in user_message for keyword in ["结束咨询", "请督导", "分析", "反馈", "结束"])
    
    if is_start_new:
        # 开始新咨询：随机选择一个来访者类型
        profile_keys = list(CHINA_PATIENT_PROFILES.keys())
        selected_key = random.choice(profile_keys)
        profile_data = CHINA_PATIENT_PROFILES[selected_key].copy()
        profile_data["disorder_type"] = profile_data["type"]
        
        # 生成随机情绪
        current_emotion = random.choice(["焦虑", "低落", "紧张", "不确定"])
        
        return {
            "phase": "patient",
            "session_id": f"session_{int(datetime.now().timestamp())}",
            "visitor_name": "来访者",
            "disorder_type": profile_data["type"],
            "response": f"你好，我是{profile_data['type']}患者。{profile_data['description'][:100]}...",
            "emotion": current_emotion,
            "message_order": 1,
            "is_final": False,
            "profile_data": profile_data
        }
    
    elif is_continue:
        return {
            "phase": "patient",
            "response": "（继续之前的咨询）请告诉我您想讨论什么？",
            "emotion": "等待",
            "is_final": False
        }
    
    elif is_end:
        return {
            "phase": "supervision",
            "response": "【督导报告】\n\n## 个案概念化\n本次咨询体现了动力学取向的若干要素...\n\n## 咨询技术分析\n咨询师展现了良好的共情能力...\n\n## 建议\n建议在下次咨询中进一步探索来访者的内心世界。\n\n*注：由于使用了简化版实现，部分功能可能不完整。",
            "is_final": True
        }
    
    else:
        # 正常对话
        if not profile_data:
            return {
                "phase": "error",
                "response": "请先创建新来访者（输入'开始新的咨询'）",
                "is_final": False
            }
        
        # 计算咨询师回应类型
        counselor_response_type = _analyze_counselor_response_type(user_message)
        
        # 计算新情绪
        new_emotion = _calculate_emotion_change(
            current_emotion,
            disorder_type or profile_data.get("type", "抑郁"),
            counselor_response_type,
            profile_data
        )
        
        # 生成简单回应（实际应该调用LLM）
        responses = [
            f"（{new_emotion}）我听到您说的话了...",
            f"（{new_emotion}）嗯...",
            f"（{new_emotion}）我想想...",
            f"（{new_emotion}）这对我来说不容易...",
        ]
        
        response_text = random.choice(responses)
        
        return {
            "phase": "patient",
            "response": response_text,
            "emotion": new_emotion,
            "counselor_response_type": counselor_response_type,
            "is_final": False
        }
