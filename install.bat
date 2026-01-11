@echo off
chcp 65001 >nul
echo 开始安装NekoAgent

echo 检查Python版本...
python -c "import sys; print(f'Python {sys.version} ({sys.executable})')" || (echo 未找到Python！ & pause & exit /b 1)

echo 创建缓存目录
mkdir cache

echo 创建虚拟环境
python -m venv venv || (echo 虚拟环境创建失败！ & pause & exit /b 1)

echo 升级pip
.\venv\Scripts\python.exe -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

echo 安装依赖
.\venv\Scripts\pip.exe install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

echo.
echo 安装完成！请确保已安装 Microsoft Visual C++ Redistributable：
echo https://aka.ms/vs/17/release/vc_redist.x64.exe
echo.
pause