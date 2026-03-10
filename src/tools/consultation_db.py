"""
来访者数据库工具（兼容版）
用于存储和管理来访者档案、会话记录（使用本地文件系统）
"""
import os
import json
from datetime import datetime
from typing import Optional, Dict, List
from langchain.tools import tool
from langchain.tools import ToolRuntime
from utils.coze_compat import new_context

# 本地存储目录
SESSIONS_DIR = "assets/sessions"
ACTIVE_VISITOR_FILE = "active_visitor.json"

# 中国国情来访者档案
CHINA_PATIENT_PROFILES = {
    "001": {
        "type": "抑郁状态",
        "description": "心境低落、兴趣减退、易疲劳、自我评价降低；社会功能受损，工作/学习困难；无明确生理疾病史，既往无精神病性症状，系中国国情下常见心理困扰。",
        "symptoms": "情绪低落、睡眠障碍、自我价值感降低、社交回避",
        "history": "工作压力大，最近一年经常感到疲劳，对生活失去兴趣"
    },
    "002": {
        "type": "焦虑状态",
        "description": "持续紧张不安、担忧过度；伴随躯体症状如心悸、出汗、失眠；无明显诱因或诱因不成比例；符合中国都市人群常见焦虑模式。",
        "symptoms": "紧张、担忧、心悸、失眠、注意力难以集中",
        "history": "家庭期望高，从小追求完美，近期工作变动频繁"
    },
    "003": {
        "type": "PTSD（创伤后应激障碍）",
        "description": "经历或目睹重大创伤事件后出现闪回、噩梦、回避行为；情绪反应强烈且持久；社会功能明显受损；需要专业干预。",
        "symptoms": "闪回、噩梦、回避、情绪麻木、易怒",
        "history": "三个月前经历交通事故，至今仍有闪回"
    },
    "004": {
        "type": "双相情感障碍",
        "description": "情绪波动剧烈，交替出现躁狂或轻躁狂和抑郁发作；躁狂期表现为精力充沛、话多、冲动行为；抑郁期情绪低落、兴趣丧失；需要长期药物和心理治疗。",
        "symptoms": "情绪高涨与低落交替、睡眠减少、冲动行为、自杀意念",
        "history": "家族有情感障碍病史，大学首次发病，已服药两年"
    },
    "005": {
        "type": "强迫症",
        "description": "反复出现强迫观念（侵入性思维）和强迫行为（重复性动作）；明知不合理但无法控制；严重影响日常生活和工作；中国人群中发病率约2-3%。",
        "symptoms": "反复检查、清洗、计数、强迫思维",
        "history": "从小做事追求完美，大学期间强迫症状加重，影响学业"
    }
}

def _ensure_dirs():
    """确保存储目录存在"""
    if not os.path.exists(SESSIONS_DIR):
        os.makedirs(SESSIONS_DIR, exist_ok=True)

@tool
def create_new_visitor(
    user_id: str,
    visitor_profile_id: str = None,
    custom_profile: str = None,
    runtime: ToolRuntime = None
) -> str:
    """
    激活新来访者
    
    Args:
        user_id: 咨询师ID
        visitor_profile_id: 来访者档案ID（从CHINA_PATIENT_PROFILES中选择）
        custom_profile: 自定义来访者描述
    
    Returns:
        激活的来访者信息
    """
    ctx = runtime.context if runtime else new_context(method="create_new_visitor")
    _ensure_dirs()
    
    # 确定来访者档案
    if custom_profile:
        profile = {
            "type": "自定义",
            "description": custom_profile,
            "symptoms": "",
            "history": ""
        }
    elif visitor_profile_id and visitor_profile_id in CHINA_PATIENT_PROFILES:
        profile = CHINA_PATIENT_PROFILES[visitor_profile_id].copy()
    else:
        # 默认使用第一个档案
        profile = CHINA_PATIENT_PROFILES["001"].copy()
    
    # 创建激活来访者记录
    active_visitor = {
        "user_id": user_id,
        "visitor_profile_id": visitor_profile_id or "001",
        "profile": profile,
        "activated_at": datetime.now().isoformat()
    }
    
    # 保存激活来访者
    with open(ACTIVE_VISITOR_FILE, 'w', encoding='utf-8') as f:
        json.dump(active_visitor, f, ensure_ascii=False, indent=2)
    
    result = f"已激活新来访者：\n"
    result += f"- 类型：{profile['type']}\n"
    result += f"- 描述：{profile['description']}\n"
    result += f"- 激活时间：{active_visitor['activated_at']}\n"
    
    return result

@tool
def get_active_visitor(
    user_id: str,
    runtime: ToolRuntime = None
) -> str:
    """
    查看当前激活的来访者
    
    Args:
        user_id: 咨询师ID
    
    Returns:
        激活的来访者信息
    """
    ctx = runtime.context if runtime else new_context(method="get_active_visitor")
    
    if not os.path.exists(ACTIVE_VISITOR_FILE):
        return "当前没有激活的来访者。请先使用 create_new_visitor 激活一个来访者。"
    
    with open(ACTIVE_VISITOR_FILE, 'r', encoding='utf-8') as f:
        active_visitor = json.load(f)
    
    profile = active_visitor.get("profile", {})
    
    result = f"当前激活的来访者：\n"
    result += f"- 档案ID：{active_visitor.get('visitor_profile_id')}\n"
    result += f"- 类型：{profile.get('type')}\n"
    result += f"- 描述：{profile.get('description')}\n"
    result += f"- 激活时间：{active_visitor.get('activated_at')}\n"
    
    return result

@tool
def create_consultation_session(
    user_id: str,
    session_type: str = "initial",
    duration_minutes: int = 50,
    runtime: ToolRuntime = None
) -> str:
    """
    创建新的咨询会话
    
    Args:
        user_id: 咨询师ID
        session_type: 会话类型（initial/regular/termination）
        duration_minutes: 会话时长（分钟）
    
    Returns:
        会话ID
    """
    ctx = runtime.context if runtime else new_context(method="create_consultation_session")
    _ensure_dirs()
    
    # 检查是否有激活的来访者
    if not os.path.exists(ACTIVE_VISITOR_FILE):
        return "错误：请先激活一个来访者"
    
    with open(ACTIVE_VISITOR_FILE, 'r', encoding='utf-8') as f:
        active_visitor = json.load(f)
    
    # 创建会话
    session_id = f"{active_visitor['user_id']}_{int(datetime.now().timestamp())}"
    
    session_data = {
        "session_id": session_id,
        "user_id": user_id,
        "visitor_profile_id": active_visitor.get("visitor_profile_id"),
        "session_type": session_type,
        "duration_minutes": duration_minutes,
        "started_at": datetime.now().isoformat(),
        "messages": []
    }
    
    # 保存会话
    session_file = os.path.join(SESSIONS_DIR, f"{session_id}.json")
    with open(session_file, 'w', encoding='utf-8') as f:
        json.dump(session_data, f, ensure_ascii=False, indent=2)
    
    return f"会话已创建，会话ID：{session_id}"

@tool
def add_dialogue_message_db(
    session_id: str,
    role: str,
    content: str,
    emotion: Optional[str] = None,
    runtime: ToolRuntime = None
) -> str:
    """
    添加对话消息到会话
    
    Args:
        session_id: 会话ID
        role: 角色（counselor/patient）
        content: 对话内容
        emotion: 情绪状态（仅patient需要）
    
    Returns:
        成功消息
    """
    ctx = runtime.context if runtime else new_context(method="add_dialogue_message_db")
    
    session_file = os.path.join(SESSIONS_DIR, f"{session_id}.json")
    
    if not os.path.exists(session_file):
        return f"错误：会话 {session_id} 不存在"
    
    with open(session_file, 'r', encoding='utf-8') as f:
        session_data = json.load(f)
    
    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    }
    
    if emotion and role == "patient":
        message["emotion"] = emotion
    
    session_data["messages"].append(message)
    
    # 更新会话文件
    with open(session_file, 'w', encoding='utf-8') as f:
        json.dump(session_data, f, ensure_ascii=False, indent=2)
    
    return "消息已添加到会话"

@tool
def end_consultation_session(
    session_id: str,
    session_summary: str = "",
    runtime: ToolRuntime = None
) -> str:
    """
    结束咨询会话
    
    Args:
        session_id: 会话ID
        session_summary: 会话摘要
    
    Returns:
        结束消息
    """
    ctx = runtime.context if runtime else new_context(method="end_consultation_session")
    
    session_file = os.path.join(SESSIONS_DIR, f"{session_id}.json")
    
    if not os.path.exists(session_file):
        return f"错误：会话 {session_id} 不存在"
    
    with open(session_file, 'r', encoding='utf-8') as f:
        session_data = json.load(f)
    
    session_data["ended_at"] = datetime.now().isoformat()
    session_data["summary"] = session_summary
    
    with open(session_file, 'w', encoding='utf-8') as f:
        json.dump(session_data, f, ensure_ascii=False, indent=2)
    
    return f"会话 {session_id} 已结束"

@tool
def get_session_history(
    session_id: str,
    runtime: ToolRuntime = None
) -> str:
    """
    获取会话历史记录
    
    Args:
        session_id: 会话ID
    
    Returns:
        会话历史
    """
    ctx = runtime.context if runtime else new_context(method="get_session_history")
    
    session_file = os.path.join(SESSIONS_DIR, f"{session_id}.json")
    
    if not os.path.exists(session_file):
        return f"错误：会话 {session_id} 不存在"
    
    with open(session_file, 'r', encoding='utf-8') as f:
        session_data = json.load(f)
    
    result = f"会话历史（{session_id}）：\n"
    result += f"开始时间：{session_data.get('started_at')}\n"
    result += f"会话类型：{session_data.get('session_type')}\n\n"
    
    for msg in session_data.get("messages", []):
        role = msg.get("role")
        content = msg.get("content")
        timestamp = msg.get("timestamp", "")
        emotion = msg.get("emotion", "")
        
        if role == "counselor":
            result += f"【咨询师】{content}\n"
        else:
            result += f"【来访者】{content}"
            if emotion:
                result += f" （情绪：{emotion}）"
            result += "\n"
    
    return result
