# GitHub Actions 打包指南

## 功能说明

本项目配置了GitHub Actions自动构建流程，可以自动将Python应用打包为Windows可执行文件(.exe)。

## 触发方式

### 方式1：推送Tag（推荐）

当你推送一个版本标签时，会自动触发构建并创建Release：

```bash
# 创建并推送tag
git tag v1.0.0
git push origin v1.0.0
```

### 方式2：手动触发

在GitHub仓库页面：
1. 点击"Actions"标签
2. 选择"Build Windows Executable"工作流
3. 点击"Run workflow"按钮
4. 选择分支，点击"Run workflow"

## 构建流程

GitHub Actions会自动执行以下步骤：

1. **检出代码**：拉取最新代码
2. **设置Python环境**：安装Python 3.9
3. **安装依赖**：安装requirements.txt中的所有包
4. **使用PyInstaller打包**：
   - 打包为单文件可执行程序
   - 无控制台窗口（GUI应用）
   - 包含所有必要的依赖
5. **创建发布包**：
   - 包含可执行文件
   - 包含文档文件
6. **上传Artifact**：构建产物可供下载
7. **创建Release**（仅Tag触发）：自动创建GitHub Release

## 下载构建产物

### 从Actions下载

1. 进入GitHub仓库的"Actions"页面
2. 点击最新的成功构建
3. 在"Artifacts"区域下载"windows-executable"
4. 解压后即可使用

### 从Releases下载（Tag触发）

1. 进入GitHub仓库的"Releases"页面
2. 找到对应版本
3. 下载`文档处理工具.exe`及相关文档

## 本地构建

如果你想在本地构建可执行文件：

### Windows系统

```batch
REM 激活虚拟环境
.venv\Scripts\activate

REM 构建
python -m PyInstaller main.spec

REM 或使用构建脚本
build.bat
```

### macOS/Linux系统

```bash
# 激活虚拟环境
source .venv/bin/activate

# 构建
python -m PyInstaller main.spec

# 或使用构建脚本
./build.sh
```

构建完成后，可执行文件位于`dist/`目录。

## PyInstaller配置说明

`main.spec`文件定义了打包配置：

```python
# 单文件模式
onefile=True

# 无控制台窗口（GUI应用）
console=False

# 包含的数据文件
datas=[('oss_helper.py', '.')]

# 隐藏导入（确保包含所有依赖）
hiddenimports=['oss2', 'PIL._tkinter_finder', 'PIL.Image', 'qrcode', 'reportlab']
```

## 常见问题

### Q1: 构建失败怎么办？

A: 检查GitHub Actions日志：
1. 点击失败的构建
2. 查看详细日志
3. 根据错误信息调试

常见原因：
- 依赖包版本不兼容
- 缺少隐藏导入
- 内存不足

### Q2: 可执行文件太大？

A: PyInstaller打包会包含整个Python运行时和所有依赖，文件较大是正常的。

优化方法：
- 移除不必要的依赖
- 使用UPX压缩（已在spec文件中启用）

### Q3: 打包后运行出错？

A: 检查：
1. 是否缺少数据文件（检查`datas`配置）
2. 是否缺少隐藏导入（检查`hiddenimports`配置）
3. 是否有路径相关问题

调试方法：
```python
# 临时启用控制台模式查看错误
console=True
```

### Q4: 如何添加应用图标？

A: 
1. 准备一个`.ico`文件
2. 在`main.spec`中添加：
```python
icon='icon.ico'
```
3. 重新构建

### Q5: 可以打包为macOS/Linux可执行文件吗？

A: 可以，但需要：
- 在对应系统上构建
- 或配置多平台GitHub Actions

macOS示例：
```yaml
jobs:
  build-macos:
    runs-on: macos-latest
    steps:
      # ... 类似步骤
```

### Q6: 如何自定义版本号？

A: 使用Git标签：
```bash
git tag v1.0.0
git push origin v1.0.0
```

在应用中获取版本：
```python
import sys
if getattr(sys, 'frozen', False):
    # 从标签读取
    version = "1.0.0"
```

## 版本管理建议

### 语义化版本

使用[语义化版本](https://semver.org/lang/zh-CN/)：

- **主版本号**：不兼容的API修改
- **次版本号**：向下兼容的功能性新增
- **修订号**：向下兼容的问题修正

示例：
- `v1.0.0` - 首个正式版本
- `v1.1.0` - 添加新功能
- `v1.1.1` - 修复Bug
- `v2.0.0` - 重大更新

### 发布流程

1. **开发新功能**
```bash
git checkout -b feature/new-feature
# 开发...
git commit -m "Add new feature"
```

2. **合并到主分支**
```bash
git checkout main
git merge feature/new-feature
```

3. **创建Tag并推送**
```bash
git tag v1.1.0
git push origin main
git push origin v1.1.0
```

4. **GitHub Actions自动构建**
   - 自动打包
   - 自动创建Release
   - 自动上传文件

5. **编辑Release说明**
   - 添加更新日志
   - 说明新功能
   - 列出修复的问题

## GitHub Actions配置文件

`.github/workflows/build.yml`：

```yaml
name: Build Windows Executable

on:
  push:
    tags:
      - 'v*'           # 当推送v开头的tag时触发
  workflow_dispatch:   # 支持手动触发

jobs:
  build:
    runs-on: windows-latest  # 使用Windows环境
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: pip install -r requirements.txt
    
    - name: Build with PyInstaller
      run: pyinstaller main.spec
    
    - name: Upload artifact
      uses: actions/upload-artifact@v3
      with:
        name: windows-executable
        path: dist/
```

## 自定义构建

你可以修改`.github/workflows/build.yml`来自定义构建：

### 添加测试步骤

```yaml
- name: Run tests
  run: python test.py
```

### 构建多个版本

```yaml
strategy:
  matrix:
    python-version: [3.8, 3.9, 3.10]
```

### 添加代码签名

```yaml
- name: Sign executable
  run: signtool sign /f cert.pfx dist/文档处理工具.exe
```

## 最佳实践

1. **每次重大更新打Tag**
   - 便于版本追踪
   - 自动构建发布

2. **在Release中写更新日志**
   - 让用户了解新功能
   - 说明已修复的问题

3. **保持构建可重现**
   - 锁定依赖版本
   - 使用requirements.txt

4. **测试打包后的程序**
   - 下载Artifact测试
   - 确认所有功能正常

5. **维护文档**
   - 更新README
   - 更新操作指南
   - 更新CHANGELOG

## 相关资源

- [GitHub Actions文档](https://docs.github.com/cn/actions)
- [PyInstaller文档](https://pyinstaller.org/)
- [语义化版本规范](https://semver.org/lang/zh-CN/)
- [GitHub Releases](https://docs.github.com/cn/repositories/releasing-projects-on-github)

## 故障排除

### 构建超时

增加超时时间：
```yaml
jobs:
  build:
    timeout-minutes: 60
```

### 磁盘空间不足

清理不需要的文件：
```yaml
- name: Free disk space
  run: |
    rm -rf /opt/hostedtoolcache
```

### 网络问题

使用镜像源：
```yaml
- name: Install dependencies
  run: |
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
```

## 持续改进

定期检查和更新：
1. Python版本
2. 依赖包版本
3. GitHub Actions版本
4. PyInstaller版本

保持最新可以获得：
- 更好的性能
- 安全更新
- 新功能支持
