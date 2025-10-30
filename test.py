#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：验证二维码和PDF生成功能
"""

import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import DocumentProcessorApp
import tkinter as tk


def test_basic_functions():
    """测试基本功能"""
    print("=" * 60)
    print("开始测试...")
    print("=" * 60)
    
    # 创建临时测试目录
    test_dir = os.path.join(os.path.dirname(__file__), "test_output")
    os.makedirs(test_dir, exist_ok=True)
    print(f"✓ 创建测试目录: {test_dir}")
    
    # 创建应用实例（不显示GUI）
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    app = DocumentProcessorApp(root)
    
    # 测试二维码生成
    print("\n测试二维码生成...")
    test_url = "https://example.com/test"
    qr_path = os.path.join(test_dir, "test_qr.png")
    
    if app.generate_qrcode(test_url, qr_path, 50):
        if os.path.exists(qr_path):
            print(f"✓ 二维码生成成功: {qr_path}")
            file_size = os.path.getsize(qr_path)
            print(f"  文件大小: {file_size} 字节")
        else:
            print("✗ 二维码文件未找到")
            return False
    else:
        print("✗ 二维码生成失败")
        return False
    
    # 测试PDF生成
    print("\n测试PDF生成...")
    from reportlab.lib.pagesizes import A4
    
    pdf_path = os.path.join(test_dir, "test_qr.pdf")
    
    if app.create_pdf_with_qrcode(qr_path, pdf_path, A4, 50, 10, 10):
        if os.path.exists(pdf_path):
            print(f"✓ PDF生成成功: {pdf_path}")
            file_size = os.path.getsize(pdf_path)
            print(f"  文件大小: {file_size} 字节")
        else:
            print("✗ PDF文件未找到")
            return False
    else:
        print("✗ PDF生成失败")
        return False
    
    # 测试目录扫描
    print("\n测试目录扫描...")
    test_root = os.path.join(os.path.dirname(__file__), "西沟乡麻地沟村（资料扫描）")
    
    if os.path.exists(test_root):
        # 测试村（二级）结构
        target_dirs = app.get_target_directories(test_root, "村")
        print(f"✓ 扫描到 {len(target_dirs)} 个目标目录（村/二级）")
        if target_dirs:
            print(f"  示例: {os.path.basename(target_dirs[0])}")
        
        # 测试乡（三级）结构
        target_dirs_xiang = app.get_target_directories(test_root, "乡")
        print(f"✓ 扫描到 {len(target_dirs_xiang)} 个目标目录（乡/三级）")
    else:
        print(f"⚠ 测试目录不存在: {test_root}")
    
    print("\n" + "=" * 60)
    print("所有测试通过！")
    print("=" * 60)
    print(f"\n测试文件保存在: {test_dir}")
    print("你可以打开查看生成的二维码和PDF文件")
    
    root.destroy()
    return True


if __name__ == "__main__":
    try:
        test_basic_functions()
    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
