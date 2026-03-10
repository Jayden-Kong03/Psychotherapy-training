"""
简化版 Memory Saver（仅内存存储）
适用于Streamlit Cloud环境，无需PostgreSQL依赖
"""
from langgraph.checkpoint.memory import MemorySaver
from typing import Optional

# 全局MemorySaver实例
_memory_saver: Optional[MemorySaver] = None

def get_memory_saver() -> MemorySaver:
    """
    获取内存存储的checkpointer
    
    注意：使用内存存储，重启后数据会丢失。
    适用于Streamlit Cloud等无状态环境。
    """
    global _memory_saver
    if _memory_saver is None:
        _memory_saver = MemorySaver()
    return _memory_saver
