"""
学术文献检索工具
用于督导阶段搜索心理学相关的学术文献和经典理论
"""
import json
from typing import Dict, List
from langchain.tools import tool
from langchain.tools import ToolRuntime
from coze_coding_dev_sdk import SearchClient
from coze_coding_utils.runtime_ctx.context import new_context

@tool
def search_academic_literature(
    query: str,
    search_focus: str = "general",
    runtime: ToolRuntime = None
) -> str:
    """
    搜索心理学相关的学术文献
    
    Args:
        query: 搜索关键词（如：抑郁 客体关系、移情 反移情、防御机制）
        search_focus: 搜索焦点
            - "general": 一般学术搜索
            - "psychodynamic": 动力学理论
            - "object_relations": 客体关系理论
            - "trauma": 创伤理论
            - "defense": 防御机制
        runtime: 运行时上下文
    
    Returns:
        学术文献搜索结果的JSON字符串
    """
    ctx = runtime.context if runtime else new_context(method="academic_search")
    
    # 根据搜索焦点调整查询
    focus_keywords = {
        "psychodynamic": ["psychodynamic", "psychoanalytic", "dynamic therapy"],
        "object_relations": ["object relations", "Klein", "Winnicott", "internal objects"],
        "trauma": ["trauma", "PTSD", "attachment", "developmental trauma"],
        "defense": ["defense mechanisms", "Freud", "Klein", "projection", "denial"]
    }
    
    # 构建学术搜索查询
    academic_query = query
    if search_focus in focus_keywords:
        keywords = focus_keywords[search_focus]
        academic_query = f"{query} {' '.join(keywords[:2])}"
    
    # 添加学术期刊和权威网站过滤
    academic_sites = "scholar.google.com,psycnet.apa.org,academic.oup.com,springer.com,wiley.com"
    
    client = SearchClient(ctx=ctx)
    
    try:
        response = client.search(
            query=academic_query,
            search_type="web",
            count=10,
            sites=academic_sites,
            need_summary=True,
            need_content=False
        )
        
        if not response.web_items:
            return f"未找到相关学术文献：{query}"
        
        # 格式化返回结果
        results = []
        for item in response.web_items:
            result = {
                "title": item.title,
                "url": item.url,
                "site_name": item.site_name,
                "snippet": item.snippet,
                "summary": item.summary if hasattr(item, 'summary') else None,
                "publish_time": item.publish_time if hasattr(item, 'publish_time') else None
            }
            results.append(result)
        
        return json.dumps(results, ensure_ascii=False, indent=2)
    
    except Exception as e:
        return f"学术文献搜索失败：{str(e)}"

@tool
def search_classic_theories(
    topic: str,
    theorists: str = "auto",
    runtime: ToolRuntime = None
) -> str:
    """
    搜索经典心理学理论著作
    
    Args:
        topic: 理论主题（如：transference, countertransference, defense, projection）
        theorists: 理论家（如：Freud, Klein, Winnicott, Bion, Kohut）
                   设为"auto"则自动选择相关理论家
        runtime: 运行时上下文
    
    Returns:
        经典理论搜索结果
    """
    ctx = runtime.context if runtime else new_context(method="classic_theories")
    
    # 经典著作推荐网站
    classic_sites = "plato.stanford.edu,britannica.com,academic.oup.com,cambridge.org"
    
    # 如果是自动选择，根据主题推荐理论家
    if theorists == "auto":
        topic_theorist_map = {
            "transference": ["Freud", "Klein"],
            "countertransference": ["Freud", "Heimann", "Racker"],
            "defense": ["Freud", "Klein", "Anna Freud"],
            "projection": ["Freud", "Klein"],
            "splitting": ["Klein"],
            "holding": ["Winnicott"],
            "containment": ["Bion"],
            "self_object": ["Kohut"],
            "attachment": ["Bowlby", "Ainsworth"]
        }
        theorists_list = topic_theorist_map.get(topic.lower(), ["Freud", "Klein"])
        query = f"{topic} {' '.join(theorists_list)} psychoanalytic theory"
    else:
        query = f"{topic} {theorists} psychoanalytic theory classic works"
    
    client = SearchClient(ctx=ctx)
    
    try:
        response = client.search(
            query=query,
            search_type="web",
            count=8,
            sites=classic_sites,
            need_summary=True
        )
        
        if not response.web_items:
            return f"未找到经典理论：{topic}"
        
        results = []
        for item in response.web_items:
            result = {
                "title": item.title,
                "url": item.url,
                "summary": item.summary if hasattr(item, 'summary') else item.snippet
            }
            results.append(result)
        
        return json.dumps(results, ensure_ascii=False, indent=2)
    
    except Exception as e:
        return f"经典理论搜索失败：{str(e)}"

@tool
def search_journal_articles(
    topic: str,
    journal: str = "any",
    runtime: ToolRuntime = None
) -> str:
    """
    搜索专业期刊文章
    
    Args:
        topic: 研究主题
        journal: 期刊名称
            - "any": 任意期刊
            - "IJP": International Journal of Psychoanalysis
            - "JAPA": Journal of the American Psychoanalytic Association
            - "PQ": Psychoanalytic Quarterly
            - "PR": Psychoanalytic Review
        runtime: 运行时上下文
    
    Returns:
        期刊文章搜索结果
    """
    ctx = runtime.context if runtime else new_context(method="journal_search")
    
    # 期刊映射
    journal_sites = {
        "any": "onlinelibrary.wiley.com,tandfonline.com,psycnet.apa.org",
        "IJP": "onlinelibrary.wiley.com",
        "JAPA": "psycnet.apa.org",
        "PQ": "onlinelibrary.wiley.com",
        "PR": "tandfonline.com"
    }
    
    sites = journal_sites.get(journal, journal_sites["any"])
    query = f'"{topic}" psychoanalytic clinical case analysis'
    
    client = SearchClient(ctx=ctx)
    
    try:
        response = client.search(
            query=query,
            search_type="web",
            count=6,
            sites=sites,
            need_summary=True,
            time_range="5y"  # 最近5年
        )
        
        if not response.web_items:
            return f"未找到相关期刊文章：{topic}"
        
        results = []
        for item in response.web_items:
            result = {
                "title": item.title,
                "journal": item.site_name,
                "url": item.url,
                "summary": item.summary if hasattr(item, 'summary') else item.snippet,
                "year": item.publish_time if hasattr(item, 'publish_time') else None
            }
            results.append(result)
        
        return json.dumps(results, ensure_ascii=False, indent=2)
    
    except Exception as e:
        return f"期刊文章搜索失败：{str(e)}"
