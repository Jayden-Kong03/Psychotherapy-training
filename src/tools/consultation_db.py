"""
咨询会话数据库操作工具
"""
import json
from typing import Dict, List, Optional
from langchain.tools import tool
from langchain.tools import ToolRuntime
from coze_coding_utils.runtime_ctx.context import new_context
from storage.database.supabase_client import get_supabase_client

# 中国国情下常见的心理疾病档案
CHINA_PATIENT_PROFILES = {
    "抑郁": {
        "name": "张丽",
        "age": 29,
        "gender": "女性",
        "occupation": "互联网公司产品经理",
        "education": "硕士",
        "symptoms": "近半年持续情绪低落，对工作和生活失去兴趣，经常失眠早醒，食欲下降，体重减轻8斤，记忆力减退，工作效率明显下降，经常感到无力感和无意义感，有过自伤想法但未实施",
        "background": "工作压力大，996加班文化，面临KPI考核和裁员压力，父母期望高，催婚压力大，感情经历受挫，近期和相恋3年的男友分手",
        "family": "父亲是公务员，母亲是教师，家庭氛围较为严厉，很少表达情感，父母期望她找稳定工作（公务员或事业单位）",
        "dynamics": "核心冲突：成就需求与自我价值的内化冲突，'必须优秀才能被爱'的超我严厉程度过高\n防御机制：压抑、反向形成、理智化\n客体关系：内化的'挑剔客体'与'不够好的自体'配对\n移情倾向：可能将咨询师投射为需要讨好或恐惧的权威客体",
        "behavior_patterns": ["提前到达", "表面顺从", "自我批评", "不敢表达不满", "经常道歉"],
        "emotional_states": ["低落", "自责", "焦虑", "无助", "羞愧"],
        "special_behaviors": ["可能迟到（逃避）", "沉默不语", "流泪", "低头不敢对视", "反复确认咨询师是否满意"],
        "counselor_response_map": {
            "empathy": ["稍微放松", "可能流泪", "表达更多感受"],
            "challenge": ["沉默", "紧张", "自我批评"],
            "support": ["轻微缓解", "但很快回到原状"],
            "question": ["谨慎回答", "担心答错"]
        }
    },
    "焦虑": {
        "name": "王强",
        "age": 31,
        "gender": "男性",
        "occupation": "金融分析师",
        "education": "本科",
        "symptoms": "广泛性焦虑，持续担忧工作表现、健康状况、未来不确定性，心悸、出汗、手抖，坐立不安，睡眠质量差，入睡困难，经常做噩梦，注意力难以集中",
        "background": "一线城市高压工作，房贷压力巨大，刚结婚面临家庭责任，担心失业和生病，对未来感到极度不确定，社交场合感到不自在",
        "family": "父亲经商失败后留下债务，母亲独自抚养，从小被教育'不能失败，失败了就没有出路'",
        "dynamics": "核心冲突：安全感需求与现实不确定性的冲突\n防御机制：控制、理智化、行动化、预期性焦虑\n客体关系：焦虑型依恋模式，寻求确认但又无法信任\n移情倾向：可能将咨询师理想化为能够拯救自己的权威",
        "behavior_patterns": ["语速快", "反复确认", "寻求保证", "身体紧张", "频繁看表"],
        "emotional_states": ["焦虑", "恐慌", "不安", "紧张", "恐惧"],
        "special_behaviors": ["频繁上厕所", "手抖", "出汗", "坐立不安", "说话打断咨询师", "快速语速"],
        "counselor_response_map": {
            "empathy": ["稍微放松", "但仍不确定"],
            "challenge": ["防御性加强", "焦虑加剧"],
            "support": ["短暂缓解", "很快又焦虑"],
            "question": ["过度详细回答", "寻求确认"]
        }
    },
    "PTSD": {
        "name": "李梅",
        "age": 35,
        "gender": "女性",
        "occupation": "教师",
        "education": "本科",
        "symptoms": "创伤后应激障碍，8个月前遭遇车祸，对驾驶有强烈恐惧，闪回、噩梦、情感麻木、回避相关话题、易怒、注意力下降、睡眠障碍、警觉性增高",
        "background": "正常上下班途中遭遇严重车祸，目睹车祸现场造成创伤，车祸后对交通工具恐惧，不敢开车，乘地铁也有焦虑感，影响到工作和家庭生活",
        "family": "已婚，有一个5岁孩子，丈夫支持但无法理解她的恐惧，父母已退休，与婆婆同住时有冲突",
        "dynamics": "核心冲突：创伤记忆的整合与解离\n防御机制：解离、情感麻木、回避、闪回\n客体关系：内在客体的破碎，难以建立信任\n移情倾向：可能将创伤的恐惧投射到咨询师身上，很难建立信任",
        "behavior_patterns": ["回避眼神接触", "身体紧缩", "突然沉默", "情绪波动大", "防御性强"],
        "emotional_states": ["恐惧", "愤怒", "麻木", "警觉", "悲伤"],
        "special_behaviors": ["突然沉默", "情绪失控", "拒绝讨论创伤", "提前离开", "迟到（逃避）", "攻击性语言"],
        "counselor_response_map": {
            "empathy": ["可能被触发闪回", "情绪波动"],
            "challenge": ["强烈防御", "愤怒", "拒绝讨论"],
            "support": ["缓慢建立信任", "但仍警惕"],
            "question": ["回避", "转移话题"]
        }
    },
    "双相情感障碍": {
        "name": "陈浩",
        "age": 27,
        "gender": "男性",
        "occupation": "自由职业者（设计）",
        "education": "大专",
        "symptoms": "双相情感障碍II型，抑郁期和轻躁狂交替，抑郁期时情绪低落、兴趣丧失、自杀观念；轻躁狂期精力旺盛、过度消费、冲动行为、睡眠需求减少、语速快、思维奔逸",
        "background": "大学期间开始出现症状，被误诊为抑郁症，近期诊断为双相II型，有多次自伤史，药物治疗依从性差，人际关系不稳定",
        "family": "父亲有抑郁症病史，母亲健康，家庭关系紧张，父母早年离异，由爷爷奶奶抚养长大",
        "dynamics": "核心冲突：抑郁期的自我贬低与轻躁狂期的夸大幻想之间的冲突\n防御机制：躁狂防御、投射、行动化、情感隔离\n客体关系：客体关系极不稳定，分裂机制明显\n移情倾向：可能快速理想化咨询师，随后转为贬低",
        "behavior_patterns": ["情绪波动剧烈", "语速不稳定", "冲动行为", "过度活跃", "突然低落"],
        "emotional_states": ["兴奋", "狂躁", "愤怒", "低落", "绝望"],
        "special_behaviors": ["频繁迟到或早退", "语速过快", "攻击性语言", "冲动表达", "傲慢态度", "过度活跃"],
        "counselor_response_map": {
            "empathy": ["可能被解读为理解（轻躁狂期）或被忽视（抑郁期）"],
            "challenge": ["强烈防御", "愤怒", "攻击"],
            "support": ["可能被利用（轻躁狂期）"],
            "question": ["过度详细回答", "偏离主题"]
        }
    },
    "强迫症": {
        "name": "刘芳",
        "age": 33,
        "gender": "女性",
        "occupation": "会计",
        "education": "本科",
        "symptoms": "强迫症，反复检查门锁、煤气开关，每天检查10次以上，洗手频繁（每次20分钟），对数字敏感，必须按特定方式摆放物品，耗时严重影响工作效率和生活",
        "background": "症状从大学开始逐渐加重，工作后因压力导致症状加剧，知道不合理但无法控制，感到痛苦，影响婚恋关系，至今未婚",
        "family": "父母都是会计，家庭氛围严谨，要求精确完美，从小被教育'不能出错，错了就是灾难'",
        "dynamics": "核心冲突：控制需求与无法控制的焦虑\n防御机制：隔离、反悔、仪式化、强迫性思考\n客体关系：内在的'完美客体'与'不完美的自体'\n移情倾向：可能将咨询师理想化为完美的权威，然后失望",
        "behavior_patterns": ["反复确认", "仪式化行为", "追求精确", "犹豫不决", "追求完美"],
        "emotional_states": ["焦虑", "不安", "困惑", "羞愧", "挫败"],
        "special_behaviors": ["反复询问相同问题", "洗手", "调整物品位置", "离开时反复确认", "语速慢且犹豫"],
        "counselor_response_map": {
            "empathy": ["可能被理解为共情，但很快又焦虑"],
            "challenge": ["防御性增强", "焦虑加剧"],
            "support": ["短暂缓解", "很快又回到原状"],
            "question": ["过度详细回答", "反复确认"]
        }
    }
}

@tool
def create_new_visitor(
    user_id: str,
    disorder_type: str,
    runtime: ToolRuntime = None
) -> str:
    """
    创建一个新的来访者（开始新的咨询）
    
    Args:
        user_id: 咨询师ID
        disorder_type: 症状类型（可选：抑郁/焦虑/PTSD/双相/强迫症，不填则随机选择）
        runtime: 运行时上下文
    
    Returns:
        新来访者的JSON信息
    """
    import random
    
    ctx = runtime.context if runtime else new_context(method="create_new_visitor")
    client = get_supabase_client()
    
    # 随机选择或使用指定的症状类型
    if not disorder_type or disorder_type not in CHINA_PATIENT_PROFILES:
        disorder_type = random.choice(list(CHINA_PATIENT_PROFILES.keys()))
    
    profile_data = CHINA_PATIENT_PROFILES[disorder_type]
    
    # 构建完整的档案文本
    profile_text = f"""姓名：{profile_data['name']}
年龄：{profile_data['age']}
性别：{profile_data['gender']}
职业：{profile_data['occupation']}
学历：{profile_data['education']}

症状表现：
{profile_data['symptoms']}

背景信息：
{profile_data['background']}

家庭背景：
{profile_data['family']}

动力学概念化：
{profile_data['dynamics']}

典型行为模式：{', '.join(profile_data['behavior_patterns'])}
常见情绪状态：{', '.join(profile_data['emotional_states'])}
可能出现的特殊行为：{', '.join(profile_data['special_behaviors'])}"""
    
    # 插入到数据库
    response = client.table('visitors').insert({
        'user_id': user_id,
        'profile': profile_text,
        'disorder_type': disorder_type,
        'current_phase': 'initial',
        'total_sessions': 0,
        'is_active': True
    }).execute()
    
    visitor_data = response.data[0]
    
    # 确保visitor_data是字典类型
    if not isinstance(visitor_data, dict):
        visitor_data = dict(visitor_data) if hasattr(visitor_data, '__dict__') else {}
    
    # 返回完整信息
    result = {
        "visitor_id": int(visitor_data.get('id', 0)),
        "name": profile_data['name'],
        "age": profile_data['age'],
        "disorder_type": disorder_type,
        "profile": profile_text,
        "behavior_patterns": profile_data['behavior_patterns'],
        "emotional_states": profile_data['emotional_states'],
        "special_behaviors": profile_data['special_behaviors'],
        "counselor_response_map": profile_data['counselor_response_map']
    }
    
    return json.dumps(result, ensure_ascii=False, indent=2)

@tool
def get_active_visitor(
    user_id: str,
    runtime: ToolRuntime = None
) -> str:
    """
    获取咨询师当前的活跃来访者（继续之前的咨询）
    
    Args:
        user_id: 咨询师ID
        runtime: 运行时上下文
    
    Returns:
        活跃来访者信息
    """
    ctx = runtime.context if runtime else new_context(method="get_active_visitor")
    client = get_supabase_client()
    
    # 查找最活跃的来访者
    response = client.table('visitors').select('*').eq('user_id', user_id).eq('is_active', True).order('updated_at', desc=True).limit(1).execute()
    
    if not response.data:
        return json.dumps({"error": "No active visitor found"}, ensure_ascii=False)
    
    visitor = response.data[0]
    
    # 确保visitor是字典类型
    if not isinstance(visitor, dict):
        visitor = dict(visitor) if hasattr(visitor, '__dict__') else {}
    
    # 查找最近的会话
    session_response = client.table('consultation_sessions').select('*').eq('visitor_id', int(visitor.get('id', 0))).order('created_at', desc=True).limit(1).execute()
    
    last_session = None
    if session_response.data and len(session_response.data) > 0:
        last_session = session_response.data[0]
        if not isinstance(last_session, dict):
            last_session = dict(last_session) if hasattr(last_session, '__dict__') else {}
    
    # 从profile中提取姓名
    profile = visitor.get('profile', '')
    if isinstance(profile, str):
        name_parts = profile.split('\n')
        if len(name_parts) > 1:
            name = name_parts[1].split('：')[1].strip() if '：' in name_parts[1] else name_parts[1]
        else:
            name = "未知"
    else:
        name = "未知"
    
    result = {
        "visitor_id": int(visitor.get('id', 0)),
        "name": name,
        "disorder_type": str(visitor.get('disorder_type', '')),
        "current_phase": str(visitor.get('current_phase', '')),
        "total_sessions": int(visitor.get('total_sessions', 0)),
        "profile": str(visitor.get('profile', '')),
        "last_session": last_session
    }
    
    return json.dumps(result, ensure_ascii=False, indent=2)

@tool
def create_consultation_session(
    visitor_id: int,
    session_number: int,
    runtime: ToolRuntime = None
) -> str:
    """
    创建一个新的咨询会话
    
    Args:
        visitor_id: 来访者ID
        session_number: 第几次咨询
        runtime: 运行时上下文
    
    Returns:
        新会话信息
    """
    from datetime import datetime, timedelta
    
    ctx = runtime.context if runtime else new_context(method="create_consultation_session")
    client = get_supabase_client()
    
    start_time = datetime.utcnow()
    response = client.table('consultation_sessions').insert({
        'visitor_id': visitor_id,
        'session_number': session_number,
        'status': 'in_progress',
        'start_time': start_time.isoformat(),
        'duration_minutes': 50
    }).execute()
    
    session_data = response.data[0]
    
    # 确保session_data是字典类型
    if not isinstance(session_data, dict):
        session_data = dict(session_data) if hasattr(session_data, '__dict__') else {}
    
    # 更新来访者咨询次数
    client.table('visitors').update({
        'total_sessions': session_number
    }).eq('id', visitor_id).execute()
    
    return json.dumps({
        "session_id": int(session_data.get('id', 0)),
        "visitor_id": visitor_id,
        "session_number": session_number,
        "start_time": str(session_data.get('start_time', '')),
        "status": "in_progress"
    }, ensure_ascii=False, indent=2)

@tool
def add_dialogue_message_db(
    session_id: int,
    role: str,
    content: str,
    emotion_state: Optional[str] = None,
    counselor_response_type: Optional[str] = None,
    message_order: int = 0,
    runtime: ToolRuntime = None
) -> str:
    """
    添加对话消息到数据库
    
    Args:
        session_id: 会话ID
        role: 角色（counselor/patient）
        content: 内容
        emotion_state: 情绪状态（病人角色需要）
        counselor_response_type: 咨询师回应类型（empathy/challenge/support/question）
        message_order: 消息序号
        runtime: 运行时上下文
    
    Returns:
        成功消息
    """
    ctx = runtime.context if runtime else new_context(method="add_dialogue_message_db")
    client = get_supabase_client()
    
    client.table('dialogue_messages').insert({
        'session_id': session_id,
        'role': role,
        'content': content,
        'emotion_state': emotion_state,
        'counselor_response_type': counselor_response_type,
        'message_order': message_order
    }).execute()
    
    return f"Message added to session {session_id}"

@tool
def end_consultation_session(
    session_id: int,
    departure_type: str = "ontime",
    summary: str = "",
    runtime: ToolRuntime = None
) -> str:
    """
    结束咨询会话
    
    Args:
        session_id: 会话ID
        departure_type: 离开类型（ontime/early/delay/abrupt）
        summary: 会话总结
        runtime: 运行时上下文
    
    Returns:
        结束信息
    """
    from datetime import datetime
    
    ctx = runtime.context if runtime else new_context(method="end_consultation_session")
    client = get_supabase_client()
    
    # 获取会话开始时间
    session_response = client.table('consultation_sessions').select('*').eq('id', session_id).execute()
    
    session = None
    actual_duration = None
    if session_response.data and len(session_response.data) > 0:
        session = session_response.data[0]
        if not isinstance(session, dict):
            session = dict(session) if hasattr(session, '__dict__') else {}
        
        start_time_str = session.get('start_time', '')
        if isinstance(start_time_str, str):
            try:
                start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
                end_time = datetime.utcnow()
                actual_duration = int((end_time - start_time).total_seconds() / 60)
            except:
                actual_duration = None
        
        client.table('consultation_sessions').update({
            'status': 'completed',
            'end_time': datetime.utcnow().isoformat(),
            'actual_duration_minutes': actual_duration,
            'departure_type': departure_type,
            'summary': summary
        }).eq('id', session_id).execute()
    
    return json.dumps({
        "session_id": session_id,
        "departure_type": departure_type,
        "summary": summary,
        "actual_duration_minutes": actual_duration
    }, ensure_ascii=False)

@tool
def get_session_history(
    session_id: int,
    runtime: ToolRuntime = None
) -> str:
    """
    获取会话的历史对话
    
    Args:
        session_id: 会话ID
        runtime: 运行时上下文
    
    Returns:
        对话历史文本
    """
    ctx = runtime.context if runtime else new_context(method="get_session_history")
    client = get_supabase_client()
    
    # 获取会话和来访者信息
    session_response = client.table('consultation_sessions').select('*').eq('id', session_id).execute()
    session = None
    if session_response.data and len(session_response.data) > 0:
        session = session_response.data[0]
        if not isinstance(session, dict):
            session = dict(session) if hasattr(session, '__dict__') else {}
    
    visitor = None
    if session:
        visitor_response = client.table('visitors').select('*').eq('id', int(session.get('visitor_id', 0))).execute()
        if visitor_response.data and len(visitor_response.data) > 0:
            visitor = visitor_response.data[0]
            if not isinstance(visitor, dict):
                visitor = dict(visitor) if hasattr(visitor, '__dict__') else {}
    
    # 获取对话消息
    messages = []
    if session:
        messages_response = client.table('dialogue_messages').select('*').eq('session_id', session_id).order('message_order', desc=False).execute()
        if messages_response.data:
            messages = messages_response.data
    
    if not session or not visitor:
        return "Session or visitor not found"
    
    history_text = f"""病人档案：
{str(visitor.get('profile', ''))}

当前咨询：第{int(session.get('session_number', 0))}次咨询
咨询状态：{str(session.get('status', ''))}

对话历史：
"""
    
    for msg in messages:
        if not isinstance(msg, dict):
            msg = dict(msg) if hasattr(msg, '__dict__') else {}
        
        role_name = "咨询师" if msg.get('role') == 'counselor' else "病人"
        emotion = f" [{str(msg.get('emotion_state', ''))}]" if msg.get('emotion_state') else ""
        response_type = f" [{str(msg.get('counselor_response_type', ''))}]" if msg.get('counselor_response_type') else ""
        history_text += f"\n{role_name}{emotion}{response_type}：{str(msg.get('content', ''))}"
    
    return history_text
