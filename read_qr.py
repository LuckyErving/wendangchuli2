#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""读取二维码内容"""

import sys
from PIL import Image

# 尝试导入 pyzbar
try:
    from pyzbar.pyzbar import decode
    HAS_PYZBAR = True
except ImportError:
    print("警告: pyzbar 未安装，正在尝试安装...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyzbar"])
    from pyzbar.pyzbar import decode
    HAS_PYZBAR = True

def read_qrcode(image_path):
    """读取二维码内容"""
    try:
        img = Image.open(image_path)
        print(f"图片信息:")
        print(f"  大小: {img.size}")
        print(f"  格式: {img.format}")
        print(f"  模式: {img.mode}")
        print()
        
        # 解码二维码
        decoded_objects = decode(img)
        
        if not decoded_objects:
            print("❌ 未检测到二维码")
            return None
        
        print(f"✅ 检测到 {len(decoded_objects)} 个二维码:\n")
        
        for obj in decoded_objects:
            data = obj.data.decode('utf-8')
            print(f"类型: {obj.type}")
            print(f"内容: {data}")
            print(f"位置: {obj.rect}")
            print()
            return data
            
    except Exception as e:
        print(f"❌ 读取失败: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    qr_path = "/Users/ervin/Studio/zPlayground/part-time/wendangchuli2/西沟乡麻地沟村（资料扫描）/何皂皂/何皂皂_qr.png"
    
    print(f"正在读取二维码: {qr_path}\n")
    print("=" * 70)
    
    url = read_qrcode(qr_path)
    
    print("=" * 70)
    
    if url:
        print(f"\n✅ 二维码URL: {url}")
        
        # 检查是否包含中文
        if any('\u4e00' <= c <= '\u9fff' for c in url):
            print("\n⚠️  URL包含中文字符（未编码）")
            from urllib.parse import quote
            encoded_url = quote(url, safe=':/')
            print(f"应该编码为: {encoded_url}")
        else:
            print("\n✅ URL已正确编码或不包含中文")
    else:
        print("\n❌ 无法读取二维码内容")
