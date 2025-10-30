#!/bin/bash
# Git初始化和首次提交脚本

echo "🚀 初始化Git仓库..."

# 如果已经是git仓库，跳过init
if [ ! -d ".git" ]; then
    git init
    echo "✓ Git仓库已初始化"
else
    echo "✓ Git仓库已存在"
fi

# 添加所有文件
git add .

# 首次提交
git commit -m "Initial commit: 文档处理工具 v1.0.0

功能:
- 二维码和PDF生成
- OSS集成和自动上传
- 支持村/乡目录结构
- GitHub Actions自动构建
- 完整的文档体系
"

echo ""
echo "✅ 本地提交完成！"
echo ""
echo "下一步操作："
echo "1. 在GitHub上创建新仓库"
echo "2. 运行以下命令关联远程仓库："
echo ""
echo "   git remote add origin https://github.com/your-username/wendangchuli2.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3. 创建首个发布版本："
echo "   git tag -a v1.0.0 -m \"Release version 1.0.0\""
echo "   git push origin v1.0.0"
echo ""
echo "GitHub Actions将自动构建Windows可执行文件！"
