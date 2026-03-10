"""
心理咨询模拟训练系统测试（高级功能）
测试：
1. 中国国情来访者档案
2. 会话恢复功能
3. 50分钟计时
4. 结束场景模拟
5. 根据咨询师回应类型计算情绪变化
6. 数据库存储
"""
import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.agents.agent import run_consultation_session

async def test_advanced_consultation():
    """测试高级功能"""
    print("=" * 80)
    print("心理咨询模拟训练系统测试（高级功能）")
    print("=" * 80)
    
    user_id = "test_counselor_001"
    
    # 测试1：开始新咨询
    print("\n【测试1：开始新咨询】")
    print("咨询师：开始新的咨询")
    
    result1 = await run_consultation_session(
        user_id=user_id,
        user_message="开始新的咨询"
    )
    
    print(f"\n病人（{result1['disorder_type']}）：{result1['response']}")
    print(f"情绪状态：{result1['emotion']}")
    print(f"会话ID：{result1['session_id']}")
    print(f"来访者：{result1['visitor_name']}")
    
    session_id = result1['session_id']
    visitor_name = result1['visitor_name']
    disorder_type = result1['disorder_type']
    message_order = result1['message_order']
    current_emotion = result1['emotion']
    
    # 测试2：咨询师回应
    print("\n" + "=" * 80)
    print("【测试2：咨询师回应（共情）】")
    counselor_input = "我理解你现在的心情很难受，能多跟我说说具体发生了什么吗？"
    print(f"咨询师：{counselor_input}")
    
    result2 = await run_consultation_session(
        user_id=user_id,
        user_message=counselor_input,
        session_id=session_id,
        message_order=message_order,
        current_emotion=current_emotion,
        disorder_type=disorder_type
    )
    
    print(f"\n病人（情绪：{result2['emotion']}）：{result2['response']}")
    print(f"咨询师回应类型识别：{result2['counselor_response_type']}")
    
    message_order = result2['message_order']
    current_emotion = result2['emotion']
    
    # 测试3：咨询师挑战
    print("\n" + "=" * 80)
    print("【测试3：咨询师回应（挑战）】")
    counselor_input = "你一直说自己很糟糕，但我想知道，这种感觉是从什么时候开始的？"
    print(f"咨询师：{counselor_input}")
    
    result3 = await run_consultation_session(
        user_id=user_id,
        user_message=counselor_input,
        session_id=session_id,
        message_order=message_order,
        current_emotion=current_emotion,
        disorder_type=disorder_type
    )
    
    print(f"\n病人（情绪：{result3['emotion']}）：{result3['response']}")
    print(f"咨询师回应类型识别：{result3['counselor_response_type']}")
    
    # 测试4：结束咨询并督导
    print("\n" + "=" * 80)
    print("【测试4：结束咨询并进入督导】")
    counselor_input = "结束咨询，请督导分析"
    print(f"咨询师：{counselor_input}")
    
    result4 = await run_consultation_session(
        user_id=user_id,
        user_message=counselor_input,
        session_id=session_id,
        message_order=result3['message_order'],
        current_emotion=result3['emotion'],
        disorder_type=disorder_type
    )
    
    print(f"\n离开场景：{result4['departure_scene']['description']}")
    print(f"\n【督导报告】\n{result4['response']}")
    
    # 测试5：继续之前的咨询
    print("\n" + "=" * 80)
    print("【测试5：继续之前的咨询（一周后）】")
    print("咨询师：继续咨询")
    
    result5 = await run_consultation_session(
        user_id=user_id,
        user_message="继续咨询"
    )
    
    print(f"\n病人（第{result5['session_number']}次咨询）：{result5['response']}")
    print(f"来访者：{result5['visitor_name']}")
    print(f"情绪状态：{result5['emotion']}")
    
    print("\n" + "=" * 80)
    print("测试完成！")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    try:
        asyncio.run(test_advanced_consultation())
    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()
