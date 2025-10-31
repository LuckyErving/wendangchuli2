#!/bin/bash
# 最终修复：只上传可执行文件，避免中文文件名问题

echo "🔧 最终修复：简化Release文件上传..."

# 删除v1.0.1 tag
echo "删除旧的v1.0.1 tag..."
git tag -d v1.0.1 2>/dev/null || true
git push origin :refs/tags/v1.0.1 2>/dev/null || true

# 提交修复
echo "提交修复..."
git add .github/workflows/build.yml
git add CHANGELOG.md

git commit -m "fix: 简化Release只上传可执行文件

- 移除中文文件名的文档上传
- 只上传 wdcl2.exe
- 在Release说明中添加文档链接
- 避免Windows环境中文编码问题
"

# 推送
echo "推送到main..."
git push origin main

sleep 2

# 重新创建tag
echo "重新创建v1.0.1 tag..."
git tag -a v1.0.1 -m "Release version 1.0.1

Bug修复:
- 更新GitHub Actions到最新版本
- 添加workflow权限配置
- 修复Release文件上传404错误
- 优化PyInstaller打包配置

完整的工作流程，可正常创建Release和上传文件。
"

# 推送tag
echo "推送tag..."
git push origin v1.0.1

echo ""
echo "✅ 完成！"
echo ""
echo "📊 检查构建："
echo "https://github.com/LuckyErving/wendangchuli2/actions"
echo ""
echo "🎉 这次应该完全成功了！"
