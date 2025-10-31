#!/bin/bash

# 问题修复提交脚本

echo "开始提交修复..."

# 添加修改的文件
git add main.py
git add CHANGELOG.md
git add FIX_THREE_ISSUES.md

# 提交
git commit -m "fix: 修复关键问题并添加图片浏览功能

1. 修复OSS上传路径 - 包含完整目录结构
   - 上传路径：base_path/根目录名/子目录名/文件
   - 例如：test/西沟乡麻地沟村（资料扫描）/何皂皂/image.jpg

2. 修复二维码URL指向 - 指向图片浏览页面
   - URL指向自动生成的 index.html
   - 扫描二维码可直接在浏览器中查看所有图片

3. 添加PDF页面方向选择
   - 新增横向/纵向选择单选按钮
   - 支持所有页面尺寸的方向切换
   - 默认为纵向

4. 新增图片浏览页面生成功能 ⭐
   - 自动为每个目录生成 index.html
   - 网格布局展示所有图片缩略图
   - 点击图片查看大图（Lightbox效果）
   - 响应式设计，支持手机和电脑
   - 现代化UI，优秀用户体验

详见 FIX_THREE_ISSUES.md"

echo "提交完成！"
echo ""
echo "准备推送到GitHub..."
git push origin main

echo ""
echo "创建标签 v1.1.0..."
git tag -a v1.1.0 -m "v1.1.0 - 重大更新

新功能:
- 🖼️ 自动生成图片浏览页面（index.html）
- 📱 响应式设计，支持手机浏览
- 🔍 支持图片大图预览
- 📄 添加PDF页面方向选择

Bug修复:
- 修复OSS上传路径包含完整目录结构
- 修复二维码URL指向问题
- 修复无法查看图片列表的问题"

echo "推送标签..."
git push origin v1.1.0

echo ""
echo "✅ 完成！GitHub Actions将自动构建新版本。"
echo ""
echo "📊 查看构建进度："
echo "https://github.com/LuckyErving/wendangchuli2/actions"
echo ""
echo "🎉 几分钟后，请检查："
echo "https://github.com/LuckyErving/wendangchuli2/releases"
