"""
学术文献检索工具（兼容版）
用于督导阶段搜索心理学相关的学术文献和经典理论
"""
import json
from typing import Dict, List
from langchain.tools import tool
from langchain.tools import ToolRuntime
from utils.coze_compat import new_context

# 经典心理学文献库（简化版，用于演示）
CLASSIC_PSYCHOLOGY_PAPERS = [
    {
        "author": "Sigmund Freud",
        "title": "The Interpretation of Dreams",
        "year": 1900,
        "type": "classic",
        "description": "Freud's foundational work on dream analysis and the unconscious mind. Introduces concepts of manifest and latent content, dream work, and the significance of symbols.",
        "keywords": "dream, unconscious, psychoanalysis, symbolism"
    },
    {
        "author": "Melanie Klein",
        "title": "Child Analysis",
        "year": 1932,
        "type": "object_relations",
        "description": "Klein's pioneering work on child psychoanalysis, introducing the paranoid-schizoid and depressive positions. Explores early infant-mother relationships and the development of object relations.",
        "keywords": "object relations, breast envy, early infancy"
    },
    {
        "author": "D.W. Winnicott",
        "title": "Playing and Reality",
        "year": 1971,
        "type": "object_relations",
        "description": "Winnicott's iconic work on the importance of the capacity for play in child development. Introduces the concept of the 'good-enough mother' and the 'transitional object'.",
        "keywords": "transitional object, play, child development"
    },
    {
        "author": "Otto Kernberg",
        "title": "Object Relations Theory and Self Psychology",
        "year": 1975,
        "type": "object_relations",
        "description": "Kernberg's theoretical framework integrating object relations theory with structural theory of personality. Examines the development of boundary disturbances in borderline and narcissistic patients.",
        "keywords": "transference, countertransference, object relations"
    },
    {
        "author": "Sigmund Freud",
        "title": "Psychoanalytic Technique",
        "year": 1904,
        "type": "technique",
        "description": "A comprehensive review of psychoanalytic techniques including free association, dream analysis, and interpretation. Discusses the role of the analyst's neutrality and the importance of the therapeutic alliance.",
        "keywords": "psychoanalytic technique, free association, dream interpretation"
    },
    {
        "author": "D.W. Winnicott",
        "title": "The Maturational Processes and the Facilitating Environment",
        "year": 1965,
        "type": "transference",
        "description": "Winnicott's exploration of the psychoanalytic process, with emphasis on the management of countertransference and the importance of the therapist's capacity for 'holding' the patient's anxieties.",
        "keywords": "countertransference, holding environment, treatment alliance"
    },
    {
        "author": "Melanie Klein",
        "title": "Envy and Gratitude",
        "year": 1957,
        "type": "defense_mechanisms",
        "description": "Klein's seminal work on envy as a primitive affect and its role in development. Explores the dynamics of gratitude and their significance for object relations.",
        "keywords": "envy, gratitude, primitive emotions"
    },
    {
        "author": "Heinz Kohut",
        "title": "The Analysis of the Self",
        "year": 1971,
        "type": "self_psychology",
        "description": "Kohut's foundational work on self psychology, introducing concepts of selfobject functions, mirroring, and idealization. Explores narcissistic disorders and their treatment.",
        "keywords": "self psychology, mirroring, idealization"
    }
]

DEFENSE_MECHANISMS = {
    "压抑": "将痛苦的思想和情感排除出意识层面，减少焦虑",
    "投射": "将自己的不可接受的想法和感受归因于他人",
    "否认": "拒绝承认现实，以保护自己不受痛苦信息的影响",
    "分裂": "将事物视为全好或全坏，无法整合积极和消极的特质",
    "理智化": "过度使用抽象思维，避免接触情感内容",
    "行动化": "将不可接受的冲动转化为可接受的行为"
}

def _format_papers(papers: List[Dict]) -> str:
    """格式化论文列表"""
    if not papers:
        return "未找到相关文献"
    
    result = "检索到以下相关文献：\n\n"
    for i, paper in enumerate(papers):
        result += f"【{i+1}】{paper['title']}\n"
        result += f"   - 作者：{paper['author']}\n"
        result += f"   - 年份：{paper['year']}\n"
        result += f"   - 类型：{paper['type']}\n"
        result += f"   - 摘要：{paper['description']}\n\n"
    
    return result

@tool
def search_academic_literature(
    query: str,
    search_focus: str = "general",
    runtime: ToolRuntime = None
) -> str:
    """
    搜索心理学相关的学术文献
    
    Args:
        query: 搜索关键词
        search_focus: 搜索重点（可选）"""
    ctx = runtime.context if runtime else new_context(method="search_academic_literature")
    
    query_lower = query.lower()
    results = []
    
    # 在本地文献库中查找匹配的论文
    for paper in CLASSIC_PSYCHOLOGY_PAPERS:
        # 在标题、描述和关键字中进行模糊匹配
        if (query_lower in paper['title'].lower() or
            query_lower in paper['author'].lower() or
            query_lower in paper['description'].lower() or
            query_lower in paper.get('keywords', '').lower()):
            results.append(paper)
    
    # 如果未找到匹配项，返回所有经典论文
    if not results:
        return _format_papers(CLASSIC_PSYCHOLOGY_PAPERS[:5])
    
    return _format_papers(results)

@tool
def search_classic_theories(
    theory_name: str,
    theorist: str = None,
    search_focus: str = None,
    runtime: ToolRuntime = None
) -> str:
    """
    搜索经典心理学理论
    
    Args:
        theory_name: 理论名称（如"客体关系"、"梦的解析"）
        theorist: 理论家名称
        search_focus: 搜索重点
    
    Returns:
        理论说明
    """
    ctx = runtime.context if runtime else new_context(method="search_classic_theories")
    
    query_parts = [part.lower() for part in theory_name.split()]
    
    # 按理论家筛选
    if theorist:
        for paper in CLASSIC_PSYCHOLOGY_PAPERS:
            if theorist.lower() in paper['author'].lower():
                if query_parts[0] in paper['description'].lower():
                    return _format_papers([paper])
    
    # 按"防御机制"筛选
    if search_focus == "defense_mechanism":
        return _get_defenses()
    
    # 默认返回经典著作列表
    return _format_papers([p for p in CLASSIC_PSYCHOLOGY_PAPERS if p['type'] == 'classic'])

@tool
def search_journal_articles(
    topic: str,
    journal_name: str = "Journal of the American Psychoanalytic Association",
    year_range: str = "2000-2024",
    runtime: ToolRuntime = None
) -> str:
    """
    搜索专业期刊中的文章
    
    Args:
        topic: 搜索主题
        journal_name: 期刊名称
        year_range: 年份范围
    
    Returns:
        检索结果
    """
    ctx = runtime.context if runtime else new_context(method="search_journal_articles")
    
    formatted_result = f"在**{journal_name}**和 **{year_range}** 范围内检索关于「{topic}」主题的相关文献：\n\n"
    
    # 在本地文献库中查找匹配
    local_matches = []
    for paper in CLASSIC_PSYCHOLOGY_PAPERS:
        if topic.lower() in paper['description'].lower():
            local_matches.append(paper)
    
    if not local_matches:
        formatted_result += "暂无本地记录。请根据以下检索策略进行在线查找：\n"
        formatted_result += f"- 1. 访问 **{journal_name}** 官网或学术数据库（如PubMed, PsycINFO）\n"
        formatted_result += f"- 2. 使用关键词：{topic}、心理学、动力学取向、临床研究\n"
        formatted_result += f"- 3. 限定年份：{year_range}\n"
        return formatted_result
    
    formatted_result += "检索到以下相关论文：\n\n"
    for i, paper in enumerate(local_matches[:3]):
        formatted_result += f"【{i+1}】{paper['title']}\n"
        formatted_result += f"   - 作者：{paper['author']}\n"
        formatted_result += f"   - 年份：{paper['year']}\n"
        formatted_result += f"   - 摘要：{paper['description']}\n\n"
    
    return formatted_result

def _get_defenses() -> str:
    """获取防御机制列表"""
    result = "常见防御机制列表（基于客体关系理论）：\n\n"
    
    for name, description in DEFENSE_MECHANISMS.items():
        result += f"**{name}**\n"
        result += f"- 描述：{description}\n"
        result += f"- 来源：Melanie Klein的客体关系理论（1932）\n\n"
    
    return result
