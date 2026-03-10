#!/bin/bash

# 心理咨询模拟训练系统 - 快速启动脚本

echo "🧠 心理咨询模拟训练系统"
echo "================================"
echo ""

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到Python3，请先安装Python3"
    exit 1
fi

echo "✅ Python环境检查通过"

# 检查是否安装了streamlit
if ! python3 -c "import streamlit" &> /dev/null; then
    echo "⚠️  Streamlit未安装，正在安装..."
    pip install streamlit
    if [ $? -ne 0 ]; then
        echo "❌ Streamlit安装失败"
        exit 1
    fi
    echo "✅ Streamlit安装成功"
else
    echo "✅ Streamlit已安装"
fi

# 检查其他依赖
echo "📦 检查依赖..."
pip install -q -r requirements.txt
if [ $? -ne 0 ]; then
    echo "⚠️  部分依赖安装失败，但将继续启动"
fi

echo "✅ 依赖检查完成"
echo ""

# 显示启动信息
echo "🚀 正在启动应用..."
echo ""
echo "📍 本地访问地址：http://localhost:8501"
echo "📍 局域网访问地址：http://$(hostname -I | awk '{print $1}'):8501"
echo ""
echo "💡 提示："
echo "   - 输入'开始新的咨询'创建新来访者"
echo "   - 输入'继续咨询'恢复之前的咨询"
echo "   - 输入'结束咨询'进行督导分析"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""
echo "================================"
echo ""

# 启动Streamlit应用
streamlit run app.py --server.port=8501 --server.headless=true
