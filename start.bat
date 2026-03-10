@echo off
chcp 65001 >nul
echo 🧠 心理咨询模拟训练系统
echo ================================
echo.

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未找到Python，请先安装Python
    pause
    exit /b 1
)

echo ✅ Python环境检查通过

REM 检查Streamlit
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Streamlit未安装，正在安装...
    pip install streamlit
    if errorlevel 1 (
        echo ❌ Streamlit安装失败
        pause
        exit /b 1
    )
    echo ✅ Streamlit安装成功
) else (
    echo ✅ Streamlit已安装
)

REM 检查依赖
echo 📦 检查依赖...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo ⚠️  部分依赖安装失败，但将继续启动
)

echo ✅ 依赖检查完成
echo.

REM 显示启动信息
echo 🚀 正在启动应用...
echo.
echo 📍 本地访问地址：http://localhost:8501
echo.
echo 💡 提示：
echo    - 输入'开始新的咨询'创建新来访者
echo    - 输入'继续咨询'恢复之前的咨询
echo    - 输入'结束咨询'进行督导分析
echo.
echo 按 Ctrl+C 停止服务
echo.
echo ================================
echo.

REM 启动Streamlit应用
streamlit run app.py --server.port=8501 --server.headless=true

pause
