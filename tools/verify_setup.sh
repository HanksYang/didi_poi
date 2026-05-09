#!/bin/bash
# POI 热度权重生成器 - 环境验证脚本

echo "🔍 验证 POI 热度权重生成器环境..."
echo ""

# 1. 检查 .env 文件
echo "1️⃣  检查 .env 配置..."
if [ ! -f ".env" ]; then
    echo "   ❌ .env 文件不存在"
    echo "   💡 运行: cp .env.example .env"
    exit 1
fi

# 检查 ANTHROPIC_API_KEY
if ! grep -q "ANTHROPIC_API_KEY=sk-ant" .env; then
    echo "   ⚠️  ANTHROPIC_API_KEY 未配置或格式不对"
    echo "   💡 请编辑 .env 文件，添加有效的 API Key"
fi
echo "   ✅ .env 文件存在"

# 2. 检查 Python 版本
echo ""
echo "2️⃣  检查 Python..."
if ! command -v python3 &> /dev/null; then
    echo "   ❌ Python3 未安装"
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1)
echo "   ✅ $PYTHON_VERSION"

# 3. 检查依赖包
echo ""
echo "3️⃣  检查依赖包..."
DEPS=("anthropic" "PIL" "dotenv" "numpy")
for dep in "${DEPS[@]}"; do
    if python3 -c "import $dep" 2>/dev/null; then
        echo "   ✅ $dep"
    else
        echo "   ❌ $dep (缺失)"
        MISSING=1
    fi
done

if [ $MISSING ]; then
    echo ""
    echo "   💡 安装缺失的包:"
    echo "   pip3 install anthropic pillow python-dotenv numpy --break-system-packages"
fi

# 4. 检查脚本文件
echo ""
echo "4️⃣  检查脚本文件..."
if [ -f "poi_heat_analyzer.py" ]; then
    echo "   ✅ poi_heat_analyzer.py"
else
    echo "   ❌ poi_heat_analyzer.py 不存在"
    exit 1
fi

# 5. 检查热力图文件
echo ""
echo "5️⃣  检查热力图文件..."
if [ -f "/Users/jingxifanyiguan/Desktop/36dbc7a39a26839c4284a92fcdec5420.jpg" ]; then
    echo "   ✅ 热力图文件存在"
else
    echo "   ⚠️  热力图文件路径可能不正确"
fi

# 6. 检查输出目录
echo ""
echo "6️⃣  检查输出目录..."
if [ -d "output" ]; then
    echo "   ✅ output/ 目录存在"
else
    echo "   💡 将创建 output/ 目录"
    mkdir -p output
fi

echo ""
echo "✅ 环境验证完成！"
echo ""
echo "📝 下一步："
echo "   1. 确保 .env 中的 ANTHROPIC_API_KEY 正确"
echo "   2. 如有缺失的包，运行上述安装命令"
echo "   3. 运行: python3 poi_heat_analyzer.py --image /Users/jingxifanyiguan/Desktop/36dbc7a39a26839c4284a92fcdec5420.jpg"
echo ""
