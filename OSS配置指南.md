# OSS配置指南

## 什么是阿里云OSS？

阿里云对象存储服务（Object Storage Service，简称OSS）是一种海量、安全、低成本、高可靠的云存储服务。本工具使用OSS来存储图片文件，并通过二维码提供访问。

## 配置步骤

### 1. 获取阿里云Access Key

1. 登录[阿里云控制台](https://home.console.aliyun.com/)
2. 鼠标悬停在右上角头像上，点击"AccessKey管理"
3. 如果是首次使用，系统会提示创建AccessKey
4. 点击"创建AccessKey"，系统会生成：
   - **Access Key ID**
   - **Access Key Secret**（仅显示一次，请妥善保存）

⚠️ **安全提示**：
- AccessKey拥有账户完整权限，请妥善保管
- 建议使用RAM子账户的AccessKey
- 不要将AccessKey提交到代码仓库

### 2. 创建OSS Bucket

1. 进入[OSS控制台](https://oss.console.aliyun.com/)
2. 点击"创建Bucket"
3. 配置：
   - **Bucket名称**：自定义，如`my-documents`
   - **区域**：选择离你最近的区域，如`华北2（北京）`
   - **存储类型**：选择"标准存储"
   - **读写权限**：选择"公共读"（允许他人通过URL访问）
   - **其他配置**：使用默认值即可
4. 点击"确定"创建

### 3. 在应用中配置OSS

启动应用后，点击"配置OSS"按钮，填入以下信息：

#### Access Key ID
从步骤1获取的Access Key ID

#### Access Key Secret
从步骤1获取的Access Key Secret

#### Endpoint
格式：`oss-cn-<region>.aliyuncs.com`

常用区域对应的Endpoint：
- 华北2（北京）：`oss-cn-beijing.aliyuncs.com`
- 华东1（杭州）：`oss-cn-hangzhou.aliyuncs.com`
- 华东2（上海）：`oss-cn-shanghai.aliyuncs.com`
- 华南1（深圳）：`oss-cn-shenzhen.aliyuncs.com`

完整区域列表请参考：https://help.aliyun.com/document_detail/31837.html

#### Bucket Name
在步骤2中创建的Bucket名称

#### 基础路径（可选）
在Bucket中的目录前缀，例如：`documents/xigou`

如果不填，文件将直接上传到Bucket根目录。

### 4. 测试连接

填写完配置后，点击"测试连接"按钮，验证配置是否正确。

### 5. 保存配置

测试成功后，点击"保存"按钮。配置将保存在本地文件`oss_config.json`中。

## 配置示例

### 示例1：基本配置
```
Access Key ID: LTAI5t**************
Access Key Secret: 5wY8**************************
Endpoint: oss-cn-beijing.aliyuncs.com
Bucket Name: my-documents
基础路径: （留空）
```

生成的URL格式：
```
https://my-documents.oss-cn-beijing.aliyuncs.com/何皂皂/image1.jpg
```

### 示例2：带路径前缀
```
Access Key ID: LTAI5t**************
Access Key Secret: 5wY8**************************
Endpoint: oss-cn-beijing.aliyuncs.com
Bucket Name: my-documents
基础路径: xigou/madgou
```

生成的URL格式：
```
https://my-documents.oss-cn-beijing.aliyuncs.com/xigou/madgou/何皂皂/image1.jpg
```

## 使用流程

### 方式1：自动上传

1. 配置好OSS
2. 勾选"生成二维码后自动上传图片到OSS"
3. 点击"开始生成"
4. 程序会：
   - 上传所有图片到OSS
   - 生成包含实际OSS URL的二维码
   - 创建PDF

### 方式2：先生成后上传

1. 配置好OSS
2. 不勾选自动上传
3. 点击"开始生成"（先生成二维码和PDF）
4. 点击"仅上传到OSS"（批量上传所有图片）

### 方式3：仅上传

如果已经生成了二维码和PDF，只需要上传图片：

1. 配置好OSS
2. 选择根目录
3. 点击"仅上传到OSS"

## 常见问题

### Q1: 如何设置Bucket为公共读？

A: 在OSS控制台：
1. 进入Bucket列表
2. 点击Bucket名称
3. 左侧菜单选择"权限管理" > "读写权限"
4. 设置为"公共读"

### Q2: 上传失败，提示权限错误？

A: 检查：
1. Access Key是否正确
2. RAM用户是否有OSS权限
3. Bucket读写权限设置

### Q3: 二维码扫描后无法访问？

A: 检查：
1. 图片是否已成功上传到OSS
2. Bucket是否设置为公共读
3. URL是否正确
4. 防火墙/网络是否正常

### Q4: 如何批量上传已有图片？

A: 
1. 确保OSS已配置
2. 选择包含图片的根目录
3. 点击"仅上传到OSS"按钮
4. 程序会自动扫描并上传所有图片

### Q5: 配置信息保存在哪里？

A: 配置保存在应用同目录下的`oss_config.json`文件中。

⚠️ **安全警告**：该文件包含敏感信息，不要分享给他人！

### Q6: 如何修改配置？

A: 再次点击"配置OSS"按钮，修改后保存即可。

### Q7: 上传的文件可以删除吗？

A: 可以。在OSS控制台中手动删除，或使用ossutil工具批量删除。

### Q8: 上传需要多长时间？

A: 取决于：
- 图片数量和大小
- 网络速度
- OSS区域距离

通常每张图片（1-2MB）需要1-3秒。

## 成本说明

### OSS收费项目

1. **存储费用**：按存储量计费
   - 标准存储：约 ¥0.12/GB/月
   
2. **流量费用**：
   - 外网流出流量：约 ¥0.5/GB
   - 内网流量：免费
   
3. **请求费用**：
   - PUT请求：约 ¥0.01/万次
   - GET请求：约 ¥0.01/万次

### 成本估算示例

假设：
- 1000个目录，每个目录10张照片
- 每张照片2MB
- 总大小：20GB

**月成本估算**：
- 存储费用：20GB × ¥0.12 = ¥2.4
- 上传流量：免费（上传不计费）
- 请求费用：10000次PUT ≈ ¥0.01

**总计**：约 ¥2.5/月

注意：如果有大量人通过二维码访问，会产生外网流出流量费用。

## 安全建议

1. **使用RAM子账户**
   - 不要使用主账户的AccessKey
   - 为子账户分配最小必要权限
   
2. **定期更换AccessKey**
   - 建议每3-6个月更换一次
   
3. **配置防盗链**
   - 在OSS控制台配置Referer白名单
   - 防止他人盗用你的流量
   
4. **监控费用**
   - 在阿里云控制台设置费用预警
   - 定期检查费用账单

## 进阶功能

### 使用CDN加速

如果需要更快的访问速度：

1. 开通阿里云CDN服务
2. 为Bucket配置CDN加速域名
3. 在应用配置中使用CDN域名

### 图片处理

阿里云OSS支持图片处理功能：
- 缩略图
- 水印
- 格式转换

可以在URL中添加处理参数。

## 相关链接

- [阿里云OSS官网](https://www.aliyun.com/product/oss)
- [OSS快速入门](https://help.aliyun.com/document_detail/31883.html)
- [OSS Python SDK文档](https://help.aliyun.com/document_detail/32026.html)
- [ossutil工具下载](https://help.aliyun.com/document_detail/120075.html)

## 技术支持

如遇到问题，请：
1. 查看应用日志窗口的错误信息
2. 检查OSS控制台的监控信息
3. 参考阿里云官方文档
