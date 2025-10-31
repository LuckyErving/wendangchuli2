# OSS访问配置说明

## 问题描述

扫描二维码后无法看到图片列表页面，可能的原因：
1. OSS Bucket 没有设置为公共读
2. 防盗链配置限制访问
3. CORS 配置不正确

## 解决方案

### 方案1：设置Bucket为公共读（推荐，最简单）

#### 步骤：

1. **登录阿里云OSS控制台**
   - 访问：https://oss.console.aliyun.com/

2. **选择Bucket**
   - 找到您配置的bucket（例如：您的bucket名称）

3. **设置读写权限**
   - 点击左侧 "权限管理" → "读写权限"
   - 将权限改为 **"公共读"**
   - 保存

#### 优点：
- ✅ 最简单，无需额外配置
- ✅ 任何人都能通过URL访问
- ✅ 适合公开的文档图片

#### 缺点：
- ⚠️ 任何人都能访问，不适合机密文件
- ⚠️ 流量费用由您承担

---

### 方案2：配置CORS（如果bucket是私有的）

如果不想设置为公共读，可以配置CORS：

#### 步骤：

1. **进入CORS设置**
   - OSS控制台 → 选择bucket → 权限管理 → 跨域设置

2. **添加CORS规则**
   ```
   来源（AllowedOrigin）: *
   允许Methods: GET, HEAD
   允许Headers: *
   暴露Headers: 
   缓存时间（秒）: 3600
   ```

3. **保存规则**

---

### 方案3：使用自定义域名（最专业）

#### 为什么需要域名？
- 更短、更好记的URL
- 品牌化的访问地址
- 可以配置HTTPS
- 不暴露OSS的原始域名

#### 步骤：

1. **购买域名**
   - 阿里云：https://wanwang.aliyun.com/
   - 推荐：.com / .cn / .top 等
   - 费用：约50-100元/年

2. **域名备案**（大陆节点必需）
   - 如果OSS在大陆节点，域名必须备案
   - 如果OSS在香港/海外节点，无需备案

3. **绑定域名到OSS**
   - OSS控制台 → 选择bucket → 传输管理 → 域名管理
   - 点击 "绑定用户域名"
   - 输入域名（如：files.yourdomain.com）
   - 添加CNAME记录

4. **配置CNAME**
   - 到域名注册商（如阿里云）
   - 添加CNAME记录：
     ```
     记录类型: CNAME
     主机记录: files
     记录值: your-bucket.oss-cn-region.aliyuncs.com
     TTL: 10分钟
     ```

5. **配置HTTPS（可选）**
   - 绑定SSL证书
   - 强制HTTPS访问

6. **更新程序配置**
   - 在程序的OSS配置中，使用自定义域名
   - 例如：`files.yourdomain.com` 而不是 `bucket.oss-cn-region.aliyuncs.com`

#### 优点：
- ✅ 专业、美观的URL
- ✅ 品牌化
- ✅ 灵活控制
- ✅ 可配置HTTPS

#### 缺点：
- ⚠️ 需要购买域名（约50-100元/年）
- ⚠️ 需要配置DNS
- ⚠️ 大陆节点需要备案

---

### 方案4：生成带签名的URL（程序修改方案）

如果不想公开bucket，可以生成临时访问URL。

#### 需要修改代码：
```python
# 在 oss_helper.py 中添加
def generate_signed_url(self, object_name, expires=3600):
    """生成带签名的临时访问URL"""
    url = self.bucket.sign_url('GET', object_name, expires)
    return url
```

#### 缺点：
- URL会很长（包含签名参数）
- URL有时效性（过期后无法访问）
- 二维码会很密集

---

## 推荐方案

### 如果是公开文档（推荐）
→ **方案1：设置Bucket为公共读**
   - 最简单快速
   - 5分钟搞定
   - 无需额外费用

### 如果是敏感文档
→ **方案4：使用签名URL**
   - 需要修改代码
   - URL有时效性
   - 更安全

### 如果想要专业化
→ **方案3：购买域名**
   - 最专业的方案
   - 需要额外费用
   - 适合长期使用

---

## 快速测试方法

### 测试Bucket是否可公开访问：

1. 上传一张测试图片到OSS
2. 获取图片URL，例如：
   ```
   https://your-bucket.oss-cn-beijing.aliyuncs.com/test/image.jpg
   ```
3. 在浏览器中直接访问这个URL
4. 如果能看到图片 = 配置正确 ✅
5. 如果提示403错误 = 需要设置为公共读 ❌

---

## 当前程序的URL格式

程序会生成如下格式的URL：

```
https://{bucket_name}.{endpoint}/{base_path}/{root_name}/{dir_name}/index.html
```

例如：
```
https://mybucket.oss-cn-beijing.aliyuncs.com/test/西沟乡麻地沟村（资料扫描）/何皂皂/index.html
```

现在程序已经修复，会自动对中文进行URL编码：
```
https://mybucket.oss-cn-beijing.aliyuncs.com/test/%E8%A5%BF%E6%B2%9F%E4%B9%A1.../index.html
```

---

## 常见问题

### Q: 为什么有时候能访问，有时候不能？
A: 可能是防盗链配置限制。检查OSS的防盗链设置，添加白名单或禁用防盗链。

### Q: 图片都能访问，但index.html不能访问？
A: 检查OSS是否开启了 "静态网站托管" 功能，并设置默认首页为 `index.html`

### Q: 手机上能访问，电脑上不能？
A: 可能是网络或DNS问题，尝试清除浏览器缓存或更换DNS。

### Q: 不想公开，但又想让特定人访问？
A: 使用方案4（签名URL）或配置RAM用户权限。

---

## 立即行动

### 最快解决方案（5分钟）：

1. 登录阿里云OSS控制台
2. 选择您的bucket
3. 权限管理 → 读写权限 → 改为 **公共读**
4. 保存
5. 重新扫描二维码测试

✅ 完成！

---

**最后更新**: 2025-10-31  
**版本**: v1.1.0
