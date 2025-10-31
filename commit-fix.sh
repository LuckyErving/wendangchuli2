#!/bin/bash
# 提交GitHub Actions修复

echo "📝 提交GitHub Actions修复..."

# 添加修改的文件
git add .github/workflows/build.yml
git add CHANGELOG.md
git add "GitHub_Actions指南.md"
git add BUGFIX_ACTIONS.md

# 提交
git commit -m "fix: 更新GitHub Actions到最新版本

- 更新 actions/checkout v3 → v4
- 更新 actions/setup-python v4 → v5  
- 更新 actions/upload-artifact v3 → v4
- 移除不存在的icon.ico引用
- 添加更多PyInstaller隐藏导入
- 更新相关文档

修复了弃用警告，确保构建流程正常运行。
"

echo ""
echo "✅ 提交完成！"
echo ""
echo "下一步："
echo "1. 推送到GitHub: git push origin main"
echo "2. 测试构建: 在GitHub Actions页面手动触发"
echo "3. 或创建Tag: git tag v1.0.1 && git push origin v1.0.1"
