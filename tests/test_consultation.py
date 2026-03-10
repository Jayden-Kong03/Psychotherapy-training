"""
心理咨询模拟训练系统测试
测试模拟病人和督导智能体的完整流程
"""
import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.agents.agent import run_consultation_session

async def test_consultation_flow():
    """测试完整的咨询-督导流程"""
    print("=" * 80)
    print("心理咨询模拟训练系统测试")
    print("=" * 80)
    
    # 第一次对话：咨询师开始咨询
    print("\n【第一次对话】")
    user_input1 = "你好，我是你的咨询师。很高兴能在这里见到你，能跟我说说最近发生了什么吗？"
    print(f"咨询师: {user_input1}")
    
    result1 = await run_consultation_session(
        user_message=user_input1,
        session_id=None  # 首次会话
    )
    
    print(f"\n病人（情绪：{result1['emotion']}）: {result1['response']}")
    print(f"会话ID: {result1['session_id']}")
    
    session_id = result1['session_id']
    
    # 第二次对话：咨询师继续
    print("\n" + "=" * 80)
    print("【第二次对话】")
    user_input2 = "我理解你现在的心情很难受。能多跟我讲讲具体是什么让你感到这么痛苦吗？"
    print(f"咨询师: {user_input2}")
    
    result2 = await run_consultation_session(
        user_message=user_input2,
        session_id=session_id
    )
    
    print(f"\n病人（情绪：{result2['emotion']}）: {result2['response']}")
    
    # 第三次对话：咨询师尝试深入
    print("\n" + "=" * 80)
    print("【第三次对话】")
    user_input3 = "听起来这件事对你影响很大。我想知道，当你遇到困难时，通常怎么应对呢？"
    print(f"咨询师: {user_input3}")
    
    result3 = await run_consultation_session(
        user_message=user_input3,
        session_id=session_id
    )
    
    print(f"\n病人（情绪：{result3['emotion']}）: {result3['response']}")
    
    # 结束咨询并进入督导
    print("\n" + "=" * 80)
    print("【结束咨询，进入督导】")
    user_input4 = "结束咨询，请督导分析"
    print(f"咨询师: {user_input4}")
    
    result4 = await run_consultation_session(
        user_message=user_input4,
        session_id=session_id
    )
    
    print(f"\n【督导报告】\n{result4['response']}")
    
    print("\n" + "=" * 80)
    print("测试完成！")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    try:
        asyncio.run(test_consultation_flow())
    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()
