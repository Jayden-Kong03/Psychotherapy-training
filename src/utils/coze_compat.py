"""
Coze Coding Utils 兼容层
为Streamlit Cloud环境提供最小化的Coze工具包替代方案
"""
import os
import time
import uuid
from typing import Optional, Dict, Any

class SimpleContext:
    """简化的Context类"""
    def __init__(self, class_name: str = None, method: str = None, **kwargs):
        self._data = {
            'method': method,
            'class_name': class_name,
            'request_id': f"req_{int(time.time())}_{uuid.uuid4().hex[:8]}",
            'created_at': time.time()
        }
        self._data.update(kwargs)
    
    def __getattr__(self, name):
        return self._data.get(name)
    
    def __setattr__(self, name, value):
        if name.startswith('_'):
            super().__setattr__(name, value)
        else:
            self._data[name] = value

def new_context(method: str = None, **kwargs) -> SimpleContext:
    """创建新的上下文对象"""
    return SimpleContext(method=method, **kwargs)

def default_headers(ctx: Any = None) -> Dict[str, str]:
    """生成默认的请求头"""
    return {
        "Content-Type": "application/json",
        "X-Request-ID": getattr(ctx, "request_id", str(uuid.uuid4())),
    }
