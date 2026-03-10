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
- 数据库存储（Supabase）
"""
import os
import json
import random
import time
from datetime import datetime
from typing import Annotated
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage
from utils.coze_compat import default_headers, new_context
from storage.memory.memory_saver import get_memory_saver

# 工具导入
from tools.dialogue_record import get_dialogue_history_text
from tools.academic_search import (
    search_academic_literature,
    search_classic_theories,
    search_journal_articles
)
from tools.consultation_db import (
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
    response_map = profile_data.get('counselor_response_map', {})
    possible_changes = response_map.get(counselor_response_type, ["无明显变化"])
    
    emotional_states = profile_data.get('emotional_states', [])
    
    # 根据症状类型和回应类型决定情绪变化
    if disorder_type == "抑郁":
        if counselor_response_type == "empathy":
            # 抑郁患者对共情可能产生放松或流泪
            return random.choice(["低落", "感动", "悲伤", "稍微放松"])
        elif counselor_response_type == "challenge":
            # 抑郁患者对挑战可能更加自我批评
            return random.choice(["自责", "低落", "焦虑", "沉默"])
        elif counselor_response_type == "support":
            # 抑郁患者对支持可能短暂缓解
            return random.choice(["稍微缓解", "感激", "仍焦虑"])
    elif disorder_type == "焦虑":
        if counselor_response_type == "empathy":
            return random.choice(["稍微放松", "但仍不确定", "感激"])
        elif counselor_response_type == "challenge":
            return random.choice(["焦虑加剧", "防御性加强", "恐慌"])
    elif disorder_type == "PTSD":
        if counselor_response_type == "empathy":
            # PTSD患者可能被触发闪回
            return random.choice(["恐惧", "闪回", "愤怒", "麻木"])
        elif counselor_response_type == "challenge":
            return random.choice(["强烈防御", "愤怒", "拒绝讨论"])
    elif disorder_type == "双相情感障碍":
        if counselor_response_type == "empathy":
            # 根据当前阶段（轻躁狂或抑郁）反应不同
            return random.choice(["兴奋", "愤怒", "低落", "感激"])
    elif disorder_type == "强迫症":
        if counselor_response_type == "empathy":
            return random.choice(["被理解", "很快又焦虑", "稍微放松"])
        elif counselor_response_type == "challenge":
            return random.choice(["焦虑加剧", "防御性加强", "困惑"])
    
    # 默认返回一个随机情绪状态
    return random.choice(emotional_states) if emotional_states else current_emotion

def _simulate_departure_scene(disorder_type: str, session_duration: int) -> dict:
    """
    模拟来访者离开场景
    
    Args:
        disorder_type: 症状类型
        session_duration: 实际咨询时长（分钟）
    
    Returns:
        离开场景信息
    """
    departure_scenes = {
        "抑郁": [
            {"type": "ontime", "description": "（准时站起身，轻轻点点头）好的，时间到了，那我先走了。谢谢老师。", "probability": 0.5},
            {"type": "delay", "description": "（收拾东西很慢，沉默了很久）老师……其实……（又沉默了几秒）算了，下次再说吧。", "probability": 0.3},
            {"type": "early", "description": "（突然站起来，低着头）对不起，我头有点晕，今天先到这里可以吗？", "probability": 0.2}
        ],
        "焦虑": [
            {"type": "ontime", "description": "（看表）哦，已经到了吗？好的，那老师下周见。谢谢！", "probability": 0.4},
            {"type": "delay", "description": "（反复确认）老师，还有几分钟对吗？我想再多说一件事……", "probability": 0.4},
            {"type": "early", "description": "（突然站起来）对不起，我想上洗手间……下次再来。", "probability": 0.2}
        ],
        "PTSD": [
            {"type": "ontime", "description": "（迅速站起来，避免眼神接触）时间到了，我先走了。", "probability": 0.5},
            {"type": "early", "description": "（突然站起来，声音颤抖）对不起，我……我现在很难受，我必须走了。", "probability": 0.4},
            {"type": "abrupt", "description": "（没有任何预警，突然站起来就走，没有说再见）", "probability": 0.1}
        ],
        "双相情感障碍": [
            {"type": "ontime", "description": "（兴奋地）时间到了！好的，下周见老师！今天聊得挺好的！", "probability": 0.3},
            {"type": "delay", "description": "（过度活跃）老师等等，我还有好多话没说完！再给我5分钟好不好？", "probability": 0.3},
            {"type": "early", "description": "（突然变得低落）算了，没什么好说的，我走了。", "probability": 0.4}
        ],
        "强迫症": [
            {"type": "delay", "description": "（反复检查自己的东西有没有落下）老师，我的水杯还在吗？我的包呢？请确认一下……", "probability": 0.6},
            {"type": "ontime", "description": "（确认了几遍自己的东西）好的，时间到了，老师再见。", "probability": 0.4}
        ]
    }
    
    scenes = departure_scenes.get(disorder_type, departure_scenes["抑郁"])
    
    # 根据概率选择离开类型
    rand = random.random()
    cumulative = 0
    selected_scene = scenes[0]
    
    for scene in scenes:
        cumulative += scene["probability"]
        if rand <= cumulative:
            selected_scene = scene
            break
    
    return selected_scene

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
    运行咨询会话
    
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
    from coze_coding_dev_sdk import LLMClient
    
    # 读取配置
    workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
    config_path = os.path.join(workspace_path, LLM_CONFIG)
    
    with open(config_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    
    ctx = new_context(method="consultation")
    client = LLMClient(ctx=ctx)
    
    # 检查是否是开始新咨询或继续咨询
    is_start_new = any(keyword in user_message for keyword in ["开始新的咨询", "新咨询", "新的咨询", "开始咨询", "创建新来访者"])
    is_continue = any(keyword in user_message for keyword in ["继续咨询", "继续上次的咨询", "恢复咨询", "开始上次"])
    is_end = any(keyword in user_message for keyword in ["结束咨询", "请督导", "分析", "反馈", "结束"])
    
    if is_start_new:
        # 开始新咨询：创建新来访者
        visitor_result = create_new_visitor(
            user_id=user_id,
            disorder_type=None,  # 随机选择
            runtime=type('obj', (object,), {'context': ctx})()
        )
        visitor_data = json.loads(visitor_result)
        
        visitor_id = visitor_data["visitor_id"]
        disorder_type = visitor_data["disorder_type"]
        profile_data = visitor_data
        current_emotion = random.choice(profile_data["emotional_states"])
        
        # 创建新会话
        session_result = create_consultation_session(
            visitor_id=visitor_id,
            session_number=1,
            runtime=type('obj', (object,), {'context': ctx})()
        )
        session_data = json.loads(session_result)
        session_id = session_data["session_id"]
        message_order = 0
        
        # 生成首次问候
        first_prompt = f"""你是一名{profile_data['disorder_type']}症状的病人，名叫{profile_data['name']}。

你的档案：
{profile_data['profile']}

这是你的第一次心理咨询，你提前到了咨询室。请根据你的症状和性格特点，模拟你见到咨询师时的第一次问候。

要求：
1. 必须包含行为描写（在括号里）
2. 体现你的症状特征
3. 体现你的情绪状态（{current_emotion}）
4. 可以表现出紧张、犹豫、讨好等特征
5. 只说对话内容，不要解释"""
        
        response = client.invoke(
            messages=[HumanMessage(content=first_prompt)],
            model=cfg['config'].get("model"),
            temperature=0.85,
            extra_body={"thinking": {"type": "disabled"}}
        )
        
        response_text = _get_text_content(response.content)
        
        # 记录对话
        add_dialogue_message_db(
            session_id=session_id,
            role="patient",
            content=response_text,
            emotion_state=current_emotion,
            message_order=message_order,
            runtime=type('obj', (object,), {'context': ctx})()
        )
        
        return {
            "phase": "patient",
            "session_id": session_id,
            "visitor_id": visitor_id,
            "visitor_name": profile_data['name'],
            "disorder_type": disorder_type,
            "session_number": 1,
            "response": response_text,
            "emotion": current_emotion,
            "message_order": message_order + 1,
            "is_final": False
        }
    
    elif is_continue:
        # 继续之前的咨询
        visitor_result = get_active_visitor(
            user_id=user_id,
            runtime=type('obj', (object,), {'context': ctx})()
        )
        visitor_data = json.loads(visitor_result)
        
        if "error" in visitor_data:
            return {
                "phase": "error",
                "response": "没有找到活跃的来访者，请先创建新来访者（输入'开始新的咨询'）"
            }
        
        visitor_id = visitor_data["visitor_id"]
        disorder_type = visitor_data["disorder_type"]
        session_number = visitor_data["total_sessions"] + 1
        profile_data = CHINA_PATIENT_PROFILES[disorder_type]
        current_emotion = random.choice(profile_data["emotional_states"])
        
        # 创建新会话
        session_result = create_consultation_session(
            visitor_id=visitor_id,
            session_number=session_number,
            runtime=type('obj', (object,), {'context': ctx})()
        )
        session_data = json.loads(session_result)
        session_id = session_data["session_id"]
        message_order = 0
        
        # 生成第二次咨询的问候
        second_prompt = f"""你是一名{disorder_type}症状的病人，这是你的第{session_number}次心理咨询。

你的档案：
{profile_data['profile']}

距离上次咨询已经过了一周，你再次来到咨询室。请根据你的症状和性格特点，模拟你见到咨询师时的问候。

要求：
1. 必须包含行为描写（在括号里）
2. 体现你的症状特征
3. 可以表现出与上次不同的情绪或行为
4. 可以提到过去一周的情况
5. 不一定要记得上次聊了什么内容
6. 只说对话内容，不要解释"""
        
        response = client.invoke(
            messages=[HumanMessage(content=second_prompt)],
            model=cfg['config'].get("model"),
            temperature=0.85,
            extra_body={"thinking": {"type": "disabled"}}
        )
        
        response_text = _get_text_content(response.content)
        
        # 记录对话
        add_dialogue_message_db(
            session_id=session_id,
            role="patient",
            content=response_text,
            emotion_state=current_emotion,
            message_order=message_order,
            runtime=type('obj', (object,), {'context': ctx})()
        )
        
        return {
            "phase": "patient",
            "session_id": session_id,
            "visitor_id": visitor_id,
            "visitor_name": visitor_data["name"],
            "disorder_type": disorder_type,
            "session_number": session_number,
            "response": response_text,
            "emotion": current_emotion,
            "message_order": message_order + 1,
            "is_final": False
        }
    
    elif is_end:
        # 结束咨询，进入督导
        
        if not session_id:
            return {
                "phase": "error",
                "response": "没有活跃的会话，无法结束咨询"
            }
        
        # 模拟离开场景
        departure_scene = _simulate_departure_scene(disorder_type, 0)
        
        # 结束会话
        end_consultation_session(
            session_id=session_id,
            departure_type=departure_scene["type"],
            summary=f"来访者{departure_scene['type']}离开",
            runtime=type('obj', (object,), {'context': ctx})()
        )
        
        # 获取对话历史进行督导分析
        history_text = get_session_history(
            session_id=session_id,
            runtime=type('obj', (object,), {'context': ctx})()
        )
        
        # 提取关键主题
        extract_prompt = f"""请从以下咨询对话中提取关键主题和症状特征（不超过100字）：\n\n{history_text}"""
        
        extract_response = client.invoke(
            messages=[HumanMessage(content=extract_prompt)],
            model=cfg['config'].get("model"),
            temperature=0.3,
            extra_body={"thinking": {"type": "disabled"}}
        )
        
        key_topics = _get_text_content(extract_response.content)
        
        # 构建动力学督导提示
        supervision_prompt = f"""你现在是一名心理动力学和客体关系取向的资深督导专家。请基于动力学理论框架对以下咨询过程进行专业督导分析。

## 对话记录

{history_text}

## 关键主题识别

{key_topics}

## 离开场景

{departure_scene["description"]}

## 督导分析要求

请严格按照以下动力学框架进行分析，所有理论观点必须标注文献来源：

### 一、个案动力学概念化
1. **核心心理冲突**
2. **主要防御机制**
3. **客体关系模式**
4. **移情表现**

### 二、咨询技术评估
1. **动力学技术运用**
2. **移情与反移情处理**
3. **解释时机和深度**
4. **边界维护**

### 三、文献理论支撑
针对每个分析点，必须引用：
- [作者, 年份] "理论观点"，出处

### 四、优点与不足
### 五、动力学取向专业建议

请提供完整的动力学督导报告。"""
        
        # 调用 LLM 生成督导报告
        messages = [HumanMessage(content=supervision_prompt)]
        
        response = client.invoke(
            messages=messages,
            model=cfg['config'].get("model"),
            temperature=0.7,
            max_completion_tokens=8192,
            extra_body={"thinking": {"type": "disabled"}}
        )
        
        response_text = _get_text_content(response.content)
        
        return {
            "phase": "supervision",
            "session_id": session_id,
            "departure_scene": departure_scene,
            "response": response_text,
            "is_final": True
        }
    
    else:
        # 正常对话：咨询师与病人对话
        if not session_id or not disorder_type or not profile_data:
            return {
                "phase": "error",
                "response": "请先开始新咨询（输入'开始新的咨询'）或继续之前的咨询（输入'继续咨询'）"
            }
        
        # 分析咨询师回应类型
        counselor_response_type = _analyze_counselor_response_type(user_message)
        
        # 记录咨询师输入
        add_dialogue_message_db(
            session_id=session_id,
            role="counselor",
            content=user_message,
            counselor_response_type=counselor_response_type,
            message_order=message_order,
            runtime=type('obj', (object,), {'context': ctx})()
        )
        
        # 计算情绪变化
        new_emotion = _calculate_emotion_change(
            current_emotion,
            disorder_type,
            counselor_response_type,
            profile_data
        )
        
        # 获取当前对话历史（简要）
        history_text = get_session_history(
            session_id=session_id,
            runtime=type('obj', (object,), {'context': ctx})()
        )
        
        # 构建模拟病人提示
        patient_prompt = f"""你是一名{disorder_type}症状的病人。

你的档案：
{profile_data['profile']}

当前对话历史：
{history_text}

咨询师刚刚说：{user_message}

咨询师回应类型：{counselor_response_type}

你的当前情绪状态：{current_emotion}，咨询师回应后你的新情绪状态：{new_emotion}

请根据你的症状、情绪状态和咨询师回应做出回应。你的回应应该：
1. 符合病人的症状特征和性格特点
2. 体现真实的情绪反应（{new_emotion}）
3. 可以表现出各种真实情况：情绪波动、沉默不语、言语攻击、考虑结束咨询等
4. 回应要自然、真实
5. 如果咨询师的话让你感到不适，可以表现出防御或攻击
6. 必须包含行为描写（在括号里）
7. 只说对话内容，不要解释你的情绪状态"""
        
        response = client.invoke(
            messages=[HumanMessage(content=patient_prompt)],
            model=cfg['config'].get("model"),
            temperature=0.85,
            extra_body={"thinking": {"type": "disabled"}}
        )
        
        response_text = _get_text_content(response.content)
        
        # 记录病人回应
        add_dialogue_message_db(
            session_id=session_id,
            role="patient",
            content=response_text,
            emotion_state=new_emotion,
            message_order=message_order + 1,
            runtime=type('obj', (object,), {'context': ctx})()
        )
        
        return {
            "phase": "patient",
            "session_id": session_id,
            "response": response_text,
            "emotion": new_emotion,
            "counselor_response_type": counselor_response_type,
            "message_order": message_order + 2,
            "is_final": False
        }
