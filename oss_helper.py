#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OSS配置和上传模块
"""

import os
import json
from pathlib import Path


class OSSConfig:
    """OSS配置管理"""
    
    CONFIG_FILE = "oss_config.json"
    
    def __init__(self):
        self.access_key_id = ""
        self.access_key_secret = ""
        self.endpoint = ""
        self.bucket_name = ""
        self.base_path = ""
        self.load_config()
    
    def load_config(self):
        """从文件加载配置"""
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.access_key_id = config.get('access_key_id', '')
                    self.access_key_secret = config.get('access_key_secret', '')
                    self.endpoint = config.get('endpoint', '')
                    self.bucket_name = config.get('bucket_name', '')
                    self.base_path = config.get('base_path', '')
            except Exception as e:
                print(f"加载配置失败: {e}")
    
    def save_config(self):
        """保存配置到文件"""
        config = {
            'access_key_id': self.access_key_id,
            'access_key_secret': self.access_key_secret,
            'endpoint': self.endpoint,
            'bucket_name': self.bucket_name,
            'base_path': self.base_path
        }
        try:
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def is_valid(self):
        """检查配置是否有效"""
        return all([
            self.access_key_id,
            self.access_key_secret,
            self.endpoint,
            self.bucket_name
        ])
    
    def get_oss_url(self, object_name):
        """获取OSS对象的访问URL"""
        # 移除endpoint中的协议部分
        endpoint_without_protocol = self.endpoint.replace('http://', '').replace('https://', '')
        # 构建URL
        return f"https://{self.bucket_name}.{endpoint_without_protocol}/{object_name}"


class OSSUploader:
    """OSS上传器"""
    
    def __init__(self, config):
        """
        初始化OSS上传器
        
        Args:
            config: OSSConfig对象
        """
        self.config = config
        self.bucket = None
        self.auth = None
        
        if config.is_valid():
            try:
                import oss2
                self.auth = oss2.Auth(config.access_key_id, config.access_key_secret)
                self.bucket = oss2.Bucket(self.auth, config.endpoint, config.bucket_name)
            except Exception as e:
                print(f"初始化OSS失败: {e}")
    
    def upload_file(self, local_path, oss_path, callback=None):
        """
        上传单个文件到OSS
        
        Args:
            local_path: 本地文件路径
            oss_path: OSS对象路径
            callback: 进度回调函数
            
        Returns:
            (success, url_or_error_message)
        """
        if not self.bucket:
            return False, "OSS未配置或配置无效"
        
        try:
            # 拼接完整的OSS路径
            if self.config.base_path:
                full_oss_path = f"{self.config.base_path.strip('/')}/{oss_path}"
            else:
                full_oss_path = oss_path
            
            # 上传文件
            self.bucket.put_object_from_file(full_oss_path, local_path)
            
            # 获取URL
            url = self.config.get_oss_url(full_oss_path)
            
            if callback:
                callback(local_path, url)
            
            return True, url
        except Exception as e:
            return False, str(e)
    
    def upload_directory(self, local_dir, oss_dir_prefix, image_extensions=None, callback=None):
        """
        上传目录中的所有图片文件
        
        Args:
            local_dir: 本地目录路径
            oss_dir_prefix: OSS目录前缀
            image_extensions: 图片扩展名集合
            callback: 进度回调函数 (file_path, success, url_or_error)
            
        Returns:
            (成功数量, 失败数量, 文件列表)
        """
        if image_extensions is None:
            image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
        
        success_count = 0
        fail_count = 0
        uploaded_files = []
        
        try:
            for item in os.listdir(local_dir):
                item_path = os.path.join(local_dir, item)
                
                # 只处理文件，且是图片文件
                if not os.path.isfile(item_path):
                    continue
                
                _, ext = os.path.splitext(item)
                if ext.lower() not in image_extensions:
                    continue
                
                # 跳过生成的二维码文件
                if item.endswith('_qr.png'):
                    continue
                
                # 构建OSS路径
                oss_path = f"{oss_dir_prefix}/{item}"
                
                # 上传文件
                success, result = self.upload_file(item_path, oss_path)
                
                if success:
                    success_count += 1
                    uploaded_files.append({
                        'local_path': item_path,
                        'oss_path': oss_path,
                        'url': result
                    })
                    if callback:
                        callback(item_path, True, result)
                else:
                    fail_count += 1
                    if callback:
                        callback(item_path, False, result)
        
        except Exception as e:
            if callback:
                callback(local_dir, False, str(e))
        
        return success_count, fail_count, uploaded_files
    
    def test_connection(self):
        """测试OSS连接"""
        if not self.bucket:
            return False, "OSS未配置"
        
        try:
            # 尝试列举bucket
            self.bucket.list_objects(max_keys=1)
            return True, "连接成功"
        except Exception as e:
            return False, f"连接失败: {str(e)}"
