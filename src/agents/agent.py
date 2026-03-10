"""
心理咨询模拟训练系统
包含两个智能体：
1. 模拟病人智能体：模拟具有心理症状的来访者，具备情绪逻辑
2. 个案督导智能体：分析咨询过程，提供专业反馈
"""
import os
import json
import random
from typing import Annotated
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage
from coze_coding_utils.runtime_ctx.context import default_headers, new_context
from storage.memory.memory_saver import get_memory_saver
from tools.dialogue_record import (
    create_dialogue_session,
    add_dialogue_message,
    get_dialogue_session,
    get_dialogue_history_text,
    end_dialogue_session
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

# 常见心理症状模板
PATIENT_PROFILES = {
    "抑郁": """姓名：李明，年龄：32岁
症状：重度抑郁，持续低落情绪
背景：工作压力大，近期遭遇失业，感到人生无意义
行为特征：说话缓慢，语气低沉，经常叹气，对事情缺乏兴趣
心理防御机制：回避、否认
咨询目标：帮助重新建立生活目标，缓解抑郁症状
""",
    "焦虑": """姓名：张华，年龄：28岁
症状：广泛性焦虑症，持续担忧
背景：对未来充满不确定性，担心工作和人际关系
行为特征：语速快，坐立不安，反复询问相同问题
心理防御机制：过度控制、强迫性思考
咨询目标：帮助识别焦虑触发点，学习放松技巧
""",
    "创伤": """姓名：王芳，年龄：35岁
症状：创伤后应激障碍（PTSD）
背景：半年前遭遇车祸，现在对驾驶有强烈恐惧
行为特征：回避相关话题，情绪容易激动，可能出现闪回
心理防御机制：解离、情感麻木
咨询目标：处理创伤记忆，重建安全感
""",
    "人格障碍": """姓名：赵强，年龄：40岁
症状：边缘型人格障碍倾向
背景：人际关系不稳定，情绪波动剧烈
行为特征：情绪极端化，对咨询师有理想化或贬低倾向，可能表现出攻击性
心理防御机制：分裂、投射认同
咨询目标：建立稳定的咨询关系，学习情绪调节
"""
}

# 情绪状态列表
EMOTION_STATES = [
    "平静", "焦虑", "愤怒", "悲伤", "恐惧", "烦躁",
    "内疚", "羞愧", "绝望", "兴奋", "抗拒", "沉默"
]

def get_random_patient_profile() -> tuple[str, str]:
    """随机选择一个病人档案"""
    disorder = random.choice(list(PATIENT_PROFILES.keys()))
    return disorder, PATIENT_PROFILES[disorder]

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
            create_dialogue_session,
            add_dialogue_message,
            get_dialogue_session,
            get_dialogue_history_text,
            end_dialogue_session
        ],
        checkpointer=get_memory_saver(),
        state_schema=AgentState,
    )
    
    return agent

# 便捷运行函数
async def run_consultation_session(
    user_message: str,
    session_id: str | None = None,
    patient_profile: str | None = None
) -> dict:
    """
    运行咨询会话
    
    Args:
        user_message: 咨询师输入的消息
        session_id: 会话ID（首次会话为None）
        patient_profile: 病人档案（首次会话可为None，随机生成）
    
    Returns:
        包含响应和会话信息的字典
    """
    from coze_coding_dev_sdk import LLMClient
    
    # 读取配置
    workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
    config_path = os.path.join(workspace_path, LLM_CONFIG)
    
    with open(config_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    
    api_key = os.getenv("COZE_WORKLOAD_IDENTITY_API_KEY")
    base_url = os.getenv("COZE_INTEGRATION_MODEL_BASE_URL")
    
    ctx = new_context(method="consultation")
    
    # 首次会话：创建会话并初始化病人档案
    if session_id is None:
        if patient_profile is None:
            disorder, patient_profile = get_random_patient_profile()
        
        # 创建会话
        client = LLMClient(ctx=ctx)
        create_msg = HumanMessage(
            content=f"""请创建一个新的对话会话。
用户ID：user_{random.randint(1000, 9999)}
病人档案：{patient_profile}
请调用 create_dialogue_session 工具创建会话。"""
        )
        
        response = client.invoke(
            messages=[create_msg],
            model=cfg['config'].get("model"),
            temperature=0.3,
            extra_body={"thinking": {"type": "disabled"}}
        )
        
        # 从响应中提取 session_id（简化处理）
        session_id = f"session_{random.randint(10000, 99999)}"
        
        # 实际创建会话
        create_dialogue_session(
            user_id=f"user_{random.randint(1000, 9999)}",
            patient_profile=patient_profile,
            runtime=type('obj', (object,), {'context': ctx})()
        )
        
        # 记录初始提示
        add_dialogue_message(
            session_id=session_id,
            role="system",
            content=f"系统：开始新的咨询会话，病人症状：{disorder}",
            runtime=type('obj', (object,), {'context': ctx})()
        )
    
    # 判断是否切换到督导模式
    is_supervision = any(
        keyword in user_message.lower()
        for keyword in ["结束咨询", "请督导", "结束", "督导", "分析", "反馈"]
    )
    
    if is_supervision:
        # 督导模式
        # 获取对话历史
        history_text = get_dialogue_history_text(
            session_id=session_id,
            runtime=type('obj', (object,), {'context': ctx})()
        )
        
        supervision_prompt = f"""你现在是个案督导专家。请分析以下咨询过程对话：

{history_text}

请从以下角度进行分析：
1. 咨询师使用的技巧和干预方式
2. 咨询师回应的优点
3. 咨询师回应的不足之处
4. 咨询师可能忽略的视角
5. 针对该症状的专业建议
6. 咨询师需要反思和成长的地方

请提供详细的督导报告。"""
        
        client = LLMClient(ctx=ctx)
        messages = [
            HumanMessage(content=supervision_prompt)
        ]
        
        response = client.invoke(
            messages=messages,
            model=cfg['config'].get("model"),
            temperature=0.7,
            extra_body={"thinking": {"type": "disabled"}}
        )
        
        response_text = _get_text_content(response.content)
        
        # 结束会话
        end_dialogue_session(
            session_id=session_id,
            summary="咨询会话结束，进入督导阶段",
            runtime=type('obj', (object,), {'context': ctx})()
        )
        
        return {
            "phase": "supervision",
            "session_id": session_id,
            "response": response_text,
            "is_final": True
        }
    
    else:
        # 模拟病人模式
        # 获取当前对话历史
        try:
            history_data = get_dialogue_session(
                session_id=session_id,
                runtime=type('obj', (object,), {'context': ctx})()
            )
        except:
            history_data = ""
        
        # 记录咨询师输入
        add_dialogue_message(
            session_id=session_id,
            role="counselor",
            content=user_message,
            runtime=type('obj', (object,), {'context': ctx})()
        )
        
        # 构建模拟病人提示
        patient_prompt = f"""你现在是一名心理病人（来访者）。根据以下信息模拟回应：

病人档案：
{patient_profile if patient_profile else "未知"}

当前对话历史：
{history_data if history_data else "这是首次对话"}

咨询师刚刚说：{user_message}

请根据你的症状和情绪状态做出回应。你的回应应该：
1. 符合病人的症状特征
2. 体现真实的情绪反应（如愤怒、沉默、抗拒、开心、焦虑等）
3. 可以出现各种真实情况：情绪波动、沉默不语、言语攻击、考虑结束咨询等
4. 回应要自然、真实，不要太刻意
5. 如果咨询师的话让你感到不适，可以表现出防御或攻击

请用病人的口吻回应，只说对话内容，不要解释你的情绪状态。"""
        
        client = LLMClient(ctx=ctx)
        messages = [
            HumanMessage(content=patient_prompt)
        ]
        
        response = client.invoke(
            messages=messages,
            model=cfg['config'].get("model"),
            temperature=0.85,  # 较高的温度以增加情绪变化
            extra_body={"thinking": {"type": "disabled"}}
        )
        
        response_text = _get_text_content(response.content)
        
        # 随机生成情绪状态
        emotion = random.choice(EMOTION_STATES)
        
        # 记录病人回应
        add_dialogue_message(
            session_id=session_id,
            role="patient",
            content=response_text,
            emotion_state=emotion,
            runtime=type('obj', (object,), {'context': ctx})()
        )
        
        return {
            "phase": "patient",
            "session_id": session_id,
            "response": response_text,
            "emotion": emotion,
            "is_final": False
        }
