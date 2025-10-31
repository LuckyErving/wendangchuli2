#!/bin/bash
# 修复权限问题并重新发布

echo "🔧 修复GitHub Actions权限问题..."

# 删除旧的tag（本地和远程）
echo "删除旧的v1.0.1 tag..."
git tag -d v1.0.1 2>/dev/null || true
git push origin :refs/tags/v1.0.1 2>/dev/null || true

# 提交修复
echo "提交权限修复..."
git add .github/workflows/build.yml
git add CHANGELOG.md
git add BUGFIX_ACTIONS.md

git commit -m "fix: 添加GitHub Actions权限配置

修复403错误：
- 添加 permissions: contents: write
- 允许workflow创建Release和上传文件

解决了Release创建失败的问题。
"

# 推送到main
echo "推送到main分支..."
git push origin main

# 等待一下
sleep 2

# 重新创建tag
echo "重新创建v1.0.1 tag..."
git tag -a v1.0.1 -m "Release version 1.0.1

Bug修复:
- 更新GitHub Actions到最新版本
- 添加workflow权限配置
- 修复Release创建403错误
- 优化PyInstaller打包配置
"

# 推送tag
echo "推送tag触发构建..."
git push origin v1.0.1

echo ""
echo "✅ 完成！"
echo ""
echo "📊 下一步："
echo "1. 访问 https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\(.*\)\.git/\1/')/actions"
echo "2. 查看 'Build Windows Executable' workflow"
echo "3. 等待构建完成（约3-5分钟）"
echo "4. 检查 Releases 页面"
echo ""
echo "🎉 修复完成，现在应该可以正常创建Release了！"
