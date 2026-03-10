"""
对话记录工具
用于保存和检索咨询师与病人模拟智能体的对话记录
"""
import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from langchain.tools import tool
from langchain.tools import ToolRuntime
from utils.coze_compat import new_context

DIALOGUES_DIR = "assets/dialogues"

def _ensure_dialogues_dir():
    """确保对话记录目录存在"""
    if not os.path.exists(DIALOGUES_DIR):
        os.makedirs(DIALOGUES_DIR, exist_ok=True)

@tool
def create_dialogue_session(
    user_id: str,
    patient_profile: str,
    runtime: ToolRuntime = None
) -> str:
    """
    创建一个新的对话会话
    
    Args:
        user_id: 用户/咨询师ID
        patient_profile: 病人档案描述（症状、背景等）
        runtime: 运行时上下文
    
    Returns:
        会话ID
    """
    ctx = runtime.context if runtime else new_context(method="create_dialogue_session")
    _ensure_dialogues_dir()
    
    session_id = f"{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    session_data = {
        "session_id": session_id,
        "user_id": user_id,
        "patient_profile": patient_profile,
        "dialogues": [],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    file_path = os.path.join(DIALOGUES_DIR, f"{session_id}.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(session_data, f, ensure_ascii=False, indent=2)
    
    return session_id

@tool
def add_dialogue_message(
    session_id: str,
    role: str,
    content: str,
    emotion_state: Optional[str] = None,
    runtime: ToolRuntime = None
) -> str:
    """
    添加一条对话消息到会话中
    
    Args:
        session_id: 会话ID
        role: 角色（counselor 或 patient）
        content: 对话内容
        emotion_state: 情绪状态（仅 patient 角色需要）
        runtime: 运行时上下文
    
    Returns:
        成功消息
    """
    ctx = runtime.context if runtime else new_context(method="add_dialogue_message")
    _ensure_dialogues_dir()
    
    file_path = os.path.join(DIALOGUES_DIR, f"{session_id}.json")
    
    if not os.path.exists(file_path):
        return f"Error: Session {session_id} not found"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        session_data = json.load(f)
    
    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    }
    
    if emotion_state and role == "patient":
        message["emotion_state"] = emotion_state
    
    session_data["dialogues"].append(message)
    session_data["updated_at"] = datetime.now().isoformat()
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(session_data, f, ensure_ascii=False, indent=2)
    
    return f"Message added to session {session_id}"

@tool
def get_dialogue_session(
    session_id: str,
    runtime: ToolRuntime = None
) -> str:
    """
    获取对话会话的完整记录
    
    Args:
        session_id: 会话ID
        runtime: 运行时上下文
    
    Returns:
        对话记录的JSON字符串
    """
    ctx = runtime.context if runtime else new_context(method="get_dialogue_session")
    _ensure_dialogues_dir()
    
    file_path = os.path.join(DIALOGUES_DIR, f"{session_id}.json")
    
    if not os.path.exists(file_path):
        return f"Error: Session {session_id} not found"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        session_data = json.load(f)
    
    return json.dumps(session_data, ensure_ascii=False, indent=2)

@tool
def get_dialogue_history_text(
    session_id: str,
    runtime: ToolRuntime = None
) -> str:
    """
    获取对话会话的历史记录文本格式（用于督导分析）
    
    Args:
        session_id: 会话ID
        runtime: 运行时上下文
    
    Returns:
        对话历史文本
    """
    ctx = runtime.context if runtime else new_context(method="get_dialogue_history_text")
    _ensure_dialogues_dir()
    
    file_path = os.path.join(DIALOGUES_DIR, f"{session_id}.json")
    
    if not os.path.exists(file_path):
        return f"Error: Session {session_id} not found"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        session_data = json.load(f)
    
    patient_profile = session_data.get("patient_profile", "")
    dialogues = session_data.get("dialogues", [])
    
    history_text = f"""病人档案：{patient_profile}

对话历史：
"""
    
    for msg in dialogues:
        role_name = "咨询师" if msg["role"] == "counselor" else "病人"
        timestamp = msg.get("timestamp", "")
        emotion = f" [{msg.get('emotion_state', '')}]" if msg.get('emotion_state') else ""
        history_text += f"\n[{timestamp}] {role_name}{emotion}：{msg['content']}"
    
    return history_text

@tool
def end_dialogue_session(
    session_id: str,
    summary: str,
    runtime: ToolRuntime = None
) -> str:
    """
    结束对话会话并添加总结
    
    Args:
        session_id: 会话ID
        summary: 会话总结
        runtime: 运行时上下文
    
    Returns:
        成功消息
    """
    ctx = runtime.context if runtime else new_context(method="end_dialogue_session")
    _ensure_dialogues_dir()
    
    file_path = os.path.join(DIALOGUES_DIR, f"{session_id}.json")
    
    if not os.path.exists(file_path):
        return f"Error: Session {session_id} not found"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        session_data = json.load(f)
    
    session_data["summary"] = summary
    session_data["ended_at"] = datetime.now().isoformat()
    session_data["updated_at"] = datetime.now().isoformat()
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(session_data, f, ensure_ascii=False, indent=2)
    
    return f"Session {session_id} ended with summary"
