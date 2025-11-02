#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档处理图形界面应用（增强版）
功能：
1. 为指定目录结构下的最深一级子目录中的所有图片生成二维码
2. 将二维码插入到PDF中
3. 上传图片到阿里云OSS
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, simpledialog
import qrcode
from PIL import Image
from reportlab.lib.pagesizes import A3, A4, A5, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import threading
from urllib.parse import quote
from oss_helper import OSSConfig, OSSUploader


class OSSConfigDialog(tk.Toplevel):
    """OSS配置对话框"""
    
    def __init__(self, parent, config):
        super().__init__(parent)
        self.title("OSS配置")
        self.geometry("500x400")
        self.config = config
        self.result = False
        
        self.create_widgets()
        self.load_config()
        
        # 模态对话框
        self.transient(parent)
        self.grab_set()
        
    def create_widgets(self):
        """创建配置界面"""
        main_frame = ttk.Frame(self, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Access Key ID
        ttk.Label(main_frame, text="Access Key ID:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.access_key_id_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.access_key_id_var, width=50).grid(row=0, column=1, pady=5)
        
        # Access Key Secret
        ttk.Label(main_frame, text="Access Key Secret:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.access_key_secret_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.access_key_secret_var, width=50, show="*").grid(row=1, column=1, pady=5)
        
        # Endpoint
        ttk.Label(main_frame, text="Endpoint:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.endpoint_var = tk.StringVar()
        entry_endpoint = ttk.Entry(main_frame, textvariable=self.endpoint_var, width=50)
        entry_endpoint.grid(row=2, column=1, pady=5)
        ttk.Label(main_frame, text="例: oss-cn-beijing.aliyuncs.com", 
                 foreground="gray").grid(row=3, column=1, sticky=tk.W)
        
        # Bucket Name
        ttk.Label(main_frame, text="Bucket Name:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.bucket_name_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.bucket_name_var, width=50).grid(row=4, column=1, pady=5)
        
        # Base Path
        ttk.Label(main_frame, text="基础路径:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.base_path_var = tk.StringVar()
        entry_base_path = ttk.Entry(main_frame, textvariable=self.base_path_var, width=50)
        entry_base_path.grid(row=5, column=1, pady=5)
        ttk.Label(main_frame, text="例: documents/xigou (可选)", 
                 foreground="gray").grid(row=6, column=1, sticky=tk.W)
        
        # 按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="测试连接", command=self.test_connection).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="保存", command=self.save_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=self.cancel).pack(side=tk.LEFT, padx=5)
        
        # 说明
        info_frame = ttk.LabelFrame(main_frame, text="说明", padding="10")
        info_frame.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        info_text = """
• Access Key可在阿里云控制台获取
• Endpoint格式: oss-cn-<region>.aliyuncs.com
• 配置将保存在本地文件中
• 基础路径为OSS中的目录前缀，可以为空
        """
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack()
        
    def load_config(self):
        """加载配置"""
        self.access_key_id_var.set(self.config.access_key_id)
        self.access_key_secret_var.set(self.config.access_key_secret)
        self.endpoint_var.set(self.config.endpoint)
        self.bucket_name_var.set(self.config.bucket_name)
        self.base_path_var.set(self.config.base_path)
    
    def test_connection(self):
        """测试OSS连接"""
        # 临时保存配置
        self.save_to_config()
        
        # 测试连接
        uploader = OSSUploader(self.config)
        success, message = uploader.test_connection()
        
        if success:
            messagebox.showinfo("测试成功", "OSS连接测试成功！")
        else:
            messagebox.showerror("测试失败", f"OSS连接测试失败：\n{message}")
    
    def save_to_config(self):
        """保存到配置对象"""
        self.config.access_key_id = self.access_key_id_var.get().strip()
        self.config.access_key_secret = self.access_key_secret_var.get().strip()
        self.config.endpoint = self.endpoint_var.get().strip()
        self.config.bucket_name = self.bucket_name_var.get().strip()
        self.config.base_path = self.base_path_var.get().strip()
    
    def save_config(self):
        """保存配置"""
        self.save_to_config()
        
        if self.config.save_config():
            messagebox.showinfo("成功", "配置已保存！")
            self.result = True
            self.destroy()
        else:
            messagebox.showerror("错误", "保存配置失败！")
    
    def cancel(self):
        """取消"""
        self.destroy()


class DocumentProcessorApp:
    """文档处理应用主类"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("文档处理工具 - 二维码、PDF与OSS管理器")
        self.root.geometry("950x750")
        
        # 页面尺寸映射
        self.page_sizes = {
            "A3": A3,
            "A4": A4,
            "A5": A5,
            "自定义": None
        }
        
        # OSS配置
        self.oss_config = OSSConfig()
        self.oss_uploader = None
        if self.oss_config.is_valid():
            self.oss_uploader = OSSUploader(self.oss_config)
        
        # 创建界面
        self.create_widgets()
        
    def create_widgets(self):
        """创建GUI组件"""
        
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 目录选择
        dir_frame = ttk.LabelFrame(main_frame, text="目录设置", padding="10")
        dir_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(dir_frame, text="根目录:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.root_dir_var = tk.StringVar()
        ttk.Entry(dir_frame, textvariable=self.root_dir_var, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(dir_frame, text="浏览...", command=self.browse_directory).grid(row=0, column=2, padx=5, pady=5)
        
        # 目录结构类型
        ttk.Label(dir_frame, text="目录结构:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.dir_type_var = tk.StringVar(value="村")
        dir_type_frame = ttk.Frame(dir_frame)
        dir_type_frame.grid(row=1, column=1, sticky=tk.W, pady=5)
        ttk.Radiobutton(dir_type_frame, text="村（二级目录）", variable=self.dir_type_var, value="村").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(dir_type_frame, text="乡（三级目录）", variable=self.dir_type_var, value="乡").pack(side=tk.LEFT, padx=10)
        
        # OSS设置
        oss_frame = ttk.LabelFrame(main_frame, text="OSS设置", padding="10")
        oss_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        oss_button_frame = ttk.Frame(oss_frame)
        oss_button_frame.grid(row=0, column=0, sticky=tk.W)
        
        ttk.Button(oss_button_frame, text="配置OSS", command=self.configure_oss).pack(side=tk.LEFT, padx=5)
        
        self.oss_status_var = tk.StringVar(value="未配置")
        self.update_oss_status()
        ttk.Label(oss_button_frame, textvariable=self.oss_status_var).pack(side=tk.LEFT, padx=10)
        
        # 上传选项
        self.auto_upload_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(oss_frame, text="生成二维码后自动上传图片到OSS", 
                       variable=self.auto_upload_var).grid(row=1, column=0, sticky=tk.W, pady=5)
        
        # PDF设置
        pdf_frame = ttk.LabelFrame(main_frame, text="PDF设置", padding="10")
        pdf_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 页面尺寸
        ttk.Label(pdf_frame, text="页面尺寸:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.page_size_var = tk.StringVar(value="A4")
        page_size_combo = ttk.Combobox(pdf_frame, textvariable=self.page_size_var, 
                                       values=list(self.page_sizes.keys()), state="readonly", width=15)
        page_size_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        page_size_combo.bind("<<ComboboxSelected>>", self.on_page_size_change)
        
        # 页面方向
        ttk.Label(pdf_frame, text="页面方向:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.page_orientation_var = tk.StringVar(value="纵向")
        orientation_frame = ttk.Frame(pdf_frame)
        orientation_frame.grid(row=1, column=1, sticky=tk.W, pady=5)
        ttk.Radiobutton(orientation_frame, text="纵向", variable=self.page_orientation_var, value="纵向").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(orientation_frame, text="横向", variable=self.page_orientation_var, value="横向").pack(side=tk.LEFT, padx=5)
        
        # 自定义尺寸
        self.custom_size_frame = ttk.Frame(pdf_frame)
        self.custom_size_frame.grid(row=0, column=2, columnspan=4, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(self.custom_size_frame, text="宽度(mm):").pack(side=tk.LEFT, padx=2)
        self.custom_width_var = tk.StringVar(value="210")
        ttk.Entry(self.custom_size_frame, textvariable=self.custom_width_var, width=8).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(self.custom_size_frame, text="高度(mm):").pack(side=tk.LEFT, padx=2)
        self.custom_height_var = tk.StringVar(value="297")
        ttk.Entry(self.custom_size_frame, textvariable=self.custom_height_var, width=8).pack(side=tk.LEFT, padx=2)
        
        self.custom_size_frame.grid_remove()  # 初始隐藏
        
        # 二维码设置
        qr_frame = ttk.LabelFrame(main_frame, text="二维码设置", padding="10")
        qr_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 二维码大小
        ttk.Label(qr_frame, text="二维码大小(mm):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.qr_size_var = tk.StringVar(value="50")
        ttk.Entry(qr_frame, textvariable=self.qr_size_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 二维码位置
        ttk.Label(qr_frame, text="X坐标(mm):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.qr_x_var = tk.StringVar(value="10")
        ttk.Entry(qr_frame, textvariable=self.qr_x_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(qr_frame, text="Y坐标(mm):").grid(row=1, column=2, sticky=tk.W, pady=5, padx=(20, 0))
        self.qr_y_var = tk.StringVar(value="10")
        ttk.Entry(qr_frame, textvariable=self.qr_y_var, width=10).grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(qr_frame, text="注：坐标为二维码左上角位置，从页面左下角开始计算", 
                 foreground="blue").grid(row=2, column=0, columnspan=4, sticky=tk.W, pady=5)
        
        # 操作按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=15)
        
        self.start_button = ttk.Button(button_frame, text="开始生成", command=self.start_processing, width=15)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.upload_button = ttk.Button(button_frame, text="仅上传到OSS", command=self.upload_only, width=15)
        self.upload_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="清除日志", command=self.clear_log, width=15).pack(side=tk.LEFT, padx=5)
        
        # 进度显示
        progress_frame = ttk.LabelFrame(main_frame, text="进度", padding="10")
        progress_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.progress_var = tk.StringVar(value="就绪")
        ttk.Label(progress_frame, textvariable=self.progress_var).pack(anchor=tk.W)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # 日志显示
        log_frame = ttk.LabelFrame(main_frame, text="处理日志", padding="10")
        log_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=100)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
    def update_oss_status(self):
        """更新OSS状态显示"""
        if self.oss_config.is_valid():
            self.oss_status_var.set(f"✓ 已配置 (Bucket: {self.oss_config.bucket_name})")
        else:
            self.oss_status_var.set("✗ 未配置")
    
    def configure_oss(self):
        """配置OSS"""
        dialog = OSSConfigDialog(self.root, self.oss_config)
        self.root.wait_window(dialog)
        
        # 更新上传器
        if self.oss_config.is_valid():
            self.oss_uploader = OSSUploader(self.oss_config)
        
        self.update_oss_status()
    
    def on_page_size_change(self, event=None):
        """页面尺寸改变时的回调"""
        if self.page_size_var.get() == "自定义":
            self.custom_size_frame.grid()
        else:
            self.custom_size_frame.grid_remove()
    
    def browse_directory(self):
        """浏览并选择目录"""
        directory = filedialog.askdirectory(title="选择根目录")
        if directory:
            self.root_dir_var.set(directory)
            self.log(f"已选择目录: {directory}")
    
    def log(self, message):
        """添加日志信息"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_log(self):
        """清除日志"""
        self.log_text.delete(1.0, tk.END)
    
    def get_page_size(self):
        """获取页面尺寸"""
        page_size_name = self.page_size_var.get()
        orientation = self.page_orientation_var.get()
        
        if page_size_name == "自定义":
            try:
                width = float(self.custom_width_var.get()) * mm
                height = float(self.custom_height_var.get()) * mm
                # 应用方向
                if orientation == "横向":
                    width, height = height, width
                return (width, height)
            except ValueError:
                messagebox.showerror("错误", "自定义尺寸必须是数字")
                return None
        else:
            page_size = self.page_sizes[page_size_name]
            # 应用方向
            if orientation == "横向":
                page_size = landscape(page_size)
            return page_size
    
    def get_target_directories(self, root_dir, dir_type):
        """
        获取目标目录列表（最深一级子目录）
        
        Args:
            root_dir: 根目录路径
            dir_type: 目录类型，"村"（二级）或"乡"（三级）
            
        Returns:
            目标目录列表
        """
        target_dirs = []
        
        if dir_type == "村":
            # 二级目录结构：根目录/一级目录
            for item in os.listdir(root_dir):
                item_path = os.path.join(root_dir, item)
                if os.path.isdir(item_path) and not item.startswith('.'):
                    target_dirs.append(item_path)
        else:  # 乡
            # 三级目录结构：根目录/一级目录/二级目录
            for level1 in os.listdir(root_dir):
                level1_path = os.path.join(root_dir, level1)
                if os.path.isdir(level1_path) and not level1.startswith('.'):
                    for level2 in os.listdir(level1_path):
                        level2_path = os.path.join(level1_path, level2)
                        if os.path.isdir(level2_path) and not level2.startswith('.'):
                            target_dirs.append(level2_path)
        
        return target_dirs
    
    def get_images_in_directory(self, directory):
        """
        获取目录中的所有图片文件
        
        Args:
            directory: 目录路径
            
        Returns:
            图片文件完整路径列表
        """
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
        images = []
        
        try:
            for item in os.listdir(directory):
                full_path = os.path.join(directory, item)
                if os.path.isfile(full_path):
                    _, ext = os.path.splitext(item)
                    if ext.lower() in image_extensions:
                        images.append(full_path)  # 返回完整路径而不是文件名
        except Exception as e:
            self.log(f"读取目录 {directory} 时出错: {str(e)}")
        
        return images
    
    def merge_images_horizontally(self, image_paths, output_path):
        """
        将多张图片垂直拼接成一张大图（上下排列）
        
        Args:
            image_paths: 图片路径列表
            output_path: 输出文件路径
        
        Returns:
            bool: 是否成功
        """
        try:
            if not image_paths:
                return False
            
            # 打开所有图片
            images = [Image.open(img_path) for img_path in image_paths]
            
            # 计算拼接后的尺寸
            # 宽度取所有图片中的最大宽度
            max_width = max(img.width for img in images)
            # 高度为所有图片高度之和
            total_height = sum(img.height for img in images)
            
            # 创建新图片（使用RGB模式以支持JPEG保存）
            merged = Image.new('RGB', (max_width, total_height), (255, 255, 255))
            
            # 逐个粘贴图片（从上到下）
            y_offset = 0
            for img in images:
                # 如果图片有透明通道，转换为RGB
                if img.mode in ('RGBA', 'LA', 'P'):
                    # 创建白色背景
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 将图片居中粘贴（如果宽度不一致）
                x_offset = (max_width - img.width) // 2
                merged.paste(img, (x_offset, y_offset))
                y_offset += img.height
            
            # 保存为高质量JPEG（无损PNG太大）
            merged.save(output_path, 'JPEG', quality=95, optimize=True)
            
            # 关闭所有图片
            for img in images:
                img.close()
            
            return True
        except Exception as e:
            self.log(f"合并图片失败: {str(e)}")
            return False

    def generate_qrcode(self, url, output_path, size_mm=50):
        """
        生成二维码图片（优化后更小）
        
        Args:
            url: 二维码内容（URL）
            output_path: 输出文件路径
            size_mm: 二维码大小（毫米）
        """
        try:
            # 将毫米转换为像素（假设300 DPI）
            dpi = 300
            size_px = int(size_mm * dpi / 25.4)
            
            qr = qrcode.QRCode(
                version=1,  # 自动选择最小版本
                error_correction=qrcode.constants.ERROR_CORRECT_L,  # 最低容错级别（7%）
                box_size=5,  # 进一步减小box_size（从8改为5）
                border=1,   # 进一步减小边框（从2改为1，QR码标准最小边框）
            )
            qr.add_data(url)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            img = img.resize((size_px, size_px), Image.Resampling.LANCZOS)
            img.save(output_path)
            
            return True
        except Exception as e:
            self.log(f"生成二维码失败: {str(e)}")
            return False
    
    def create_pdf_with_qrcode(self, qr_image_path, pdf_path, page_size, qr_size_mm, x_mm, y_mm):
        """
        创建PDF并插入二维码
        
        Args:
            qr_image_path: 二维码图片路径
            pdf_path: PDF输出路径
            page_size: 页面尺寸
            qr_size_mm: 二维码大小（毫米）
            x_mm: X坐标（毫米）
            y_mm: Y坐标（毫米）
        """
        try:
            c = canvas.Canvas(pdf_path, pagesize=page_size)
            
            # 将毫米转换为点（ReportLab使用点作为单位）
            qr_size = qr_size_mm * mm
            x_pos = x_mm * mm
            y_pos = y_mm * mm
            
            # 在PDF上绘制二维码
            c.drawImage(qr_image_path, x_pos, y_pos, width=qr_size, height=qr_size)
            
            c.save()
            return True
        except Exception as e:
            self.log(f"创建PDF失败: {str(e)}")
            return False
    
    def generate_index_html(self, directory, uploaded_files, dir_name):
        """
        生成索引HTML文件，用于在浏览器中查看图片列表
        
        Args:
            directory: 本地目录路径
            uploaded_files: 已上传的文件列表
            dir_name: 目录名称
            
        Returns:
            index.html文件路径
        """
        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{dir_name} - 图片浏览</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            padding: 30px;
        }}
        h1 {{
            color: #333;
            margin-bottom: 10px;
            font-size: 28px;
        }}
        .info {{
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }}
        .gallery {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .image-item {{
            background: #fff;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            overflow: hidden;
            transition: transform 0.2s, box-shadow 0.2s;
            cursor: pointer;
        }}
        .image-item:hover {{
            transform: translateY(-4px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        .image-item img {{
            width: 100%;
            height: 200px;
            object-fit: cover;
            display: block;
        }}
        .image-name {{
            padding: 12px;
            font-size: 14px;
            color: #333;
            text-align: center;
            word-break: break-all;
        }}
        .lightbox {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.9);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }}
        .lightbox.active {{
            display: flex;
        }}
        .lightbox img {{
            max-width: 90%;
            max-height: 90%;
            object-fit: contain;
        }}
        .lightbox-close {{
            position: absolute;
            top: 20px;
            right: 30px;
            color: white;
            font-size: 40px;
            cursor: pointer;
            z-index: 1001;
        }}
        @media (max-width: 768px) {{
            .gallery {{
                grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
                gap: 10px;
            }}
            .container {{
                padding: 15px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📁 {dir_name}</h1>
        <div class="info">共 {len(uploaded_files)} 张图片</div>
        <div class="gallery">
"""
        
        # 添加每张图片
        for file_info in uploaded_files:
            filename = os.path.basename(file_info['local_path'])
            # URL编码，保留协议和域名部分的特殊字符
            url = file_info['url']
            # 对URL中的路径部分进行编码（保留协议和斜杠）
            if '://' in url:
                protocol_end = url.index('://') + 3
                domain_end = url.index('/', protocol_end)
                protocol_domain = url[:domain_end]
                path = url[domain_end:]
                # 编码路径部分，但保留斜杠
                encoded_path = quote(path, safe='/')
                encoded_url = protocol_domain + encoded_path
            else:
                encoded_url = quote(url, safe=':/')
            
            html_content += f"""
            <div class="image-item" onclick="openLightbox('{encoded_url}')">
                <img src="{encoded_url}" alt="{filename}" loading="lazy">
                <div class="image-name">{filename}</div>
            </div>
"""
        
        html_content += """
        </div>
    </div>
    
    <div class="lightbox" id="lightbox" onclick="closeLightbox()">
        <span class="lightbox-close">&times;</span>
        <img id="lightbox-img" src="" alt="">
    </div>
    
    <script>
        function openLightbox(url) {
            document.getElementById('lightbox').classList.add('active');
            document.getElementById('lightbox-img').src = url;
        }
        
        function closeLightbox() {
            document.getElementById('lightbox').classList.remove('active');
        }
        
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                closeLightbox();
            }
        });
    </script>
</body>
</html>
"""
        
        # 保存HTML文件
        index_path = os.path.join(directory, 'index.html')
        try:
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            return index_path
        except Exception as e:
            self.log(f"  生成index.html失败: {str(e)}")
            return None
    
    def upload_merged_image_to_oss(self, merged_image_path, directory, root_dir=None):
        """
        上传合并后的大图到OSS
        
        Args:
            merged_image_path: 合并后的图片路径
            directory: 原目录路径
            root_dir: 根目录路径（用于构建完整路径结构）
            
        Returns:
            (成功, 图片URL)
        """
        if not self.oss_uploader:
            self.log("  OSS未配置，跳过上传")
            return False, None
        
        # 构建OSS路径：包含根目录名称和子目录名称
        if root_dir:
            root_name = os.path.basename(root_dir)
            dir_name = os.path.basename(directory)
            oss_path = f"{root_name}/{dir_name}/{os.path.basename(merged_image_path)}"
        else:
            dir_name = os.path.basename(directory)
            oss_path = f"{dir_name}/{os.path.basename(merged_image_path)}"
        
        self.log(f"  开始上传合并图片到OSS...")
        success, result = self.oss_uploader.upload_file(merged_image_path, oss_path)
        
        if success:
            self.log(f"    ✓ 已上传: {os.path.basename(merged_image_path)}")
            return True, result
        else:
            self.log(f"    ✗ 上传失败: {result}")
            return False, None
    
    def process_directory(self, directory, page_size, qr_size_mm, x_mm, y_mm, auto_upload=False, root_dir=None):
        """
        处理单个目录：上传图片、生成二维码和PDF
        
        Args:
            directory: 目标目录路径
            page_size: PDF页面尺寸
            qr_size_mm: 二维码大小
            x_mm: 二维码X坐标
            y_mm: 二维码Y坐标
            auto_upload: 是否自动上传
            root_dir: 根目录路径（用于构建OSS路径）
        """
        dir_name = os.path.basename(directory)
        self.log(f"处理目录: {dir_name}")
        
        # 检查目录中是否有图片
        images = self.get_images_in_directory(directory)
        if not images:
            self.log(f"  跳过（无图片）: {dir_name}")
            return
        
        self.log(f"  找到 {len(images)} 张图片")
        
        # 合并图片
        merged_filename = f"{dir_name}_merged.jpg"
        merged_path = os.path.join(directory, merged_filename)
        
        self.log(f"  合并图片...")
        if not self.merge_images_horizontally(images, merged_path):
            self.log(f"  图片合并失败，跳过")
            return
        
        self.log(f"  已合并 {len(images)} 张图片")
        
        # 如果启用自动上传，上传合并后的大图到OSS
        oss_url = None
        if auto_upload:
            success, oss_url = self.upload_merged_image_to_oss(merged_path, directory, root_dir)
            if not success:
                self.log(f"  警告：上传失败，将使用默认URL生成二维码")
        
        # 如果没有OSS URL，使用默认格式
        if not oss_url:
            # 构建默认OSS URL
            if self.oss_config.is_valid():
                endpoint_without_protocol = self.oss_config.endpoint.replace('http://', '').replace('https://', '')
                
                # 构建OSS路径
                if root_dir:
                    root_name = os.path.basename(root_dir)
                    # 计算相对路径
                    if directory.startswith(root_dir):
                        rel_path = os.path.relpath(directory, root_dir)
                        if rel_path == '.':
                            oss_path = f"{root_name}/{merged_filename}"
                        else:
                            oss_path = f"{root_name}/{rel_path}/{merged_filename}"
                    else:
                        oss_path = f"{dir_name}/{merged_filename}"
                else:
                    oss_path = f"{dir_name}/{merged_filename}"
                
                # URL编码路径
                encoded_path = quote(oss_path, safe='/')
                
                # 构建完整URL
                if self.oss_config.base_path:
                    encoded_base = quote(self.oss_config.base_path.strip('/'), safe='')
                    oss_url = f"https://{self.oss_config.bucket_name}.{endpoint_without_protocol}/{encoded_base}/{encoded_path}"
                else:
                    oss_url = f"https://{self.oss_config.bucket_name}.{endpoint_without_protocol}/{encoded_path}"
            else:
                oss_url = f"https://your-bucket.oss-region.aliyuncs.com/{quote(dir_name, safe='')}/{quote(merged_filename, safe='')}"
        
        # 对URL进行编码（如果包含中文字符）
        # 注意：只编码路径部分，不编码协议和域名
        if oss_url and '://' in oss_url:
            protocol, rest = oss_url.split('://', 1)
            if '/' in rest:
                domain, path = rest.split('/', 1)
                # 对路径进行URL编码，但保留斜杠
                encoded_path = quote(path, safe='/')
                oss_url = f"{protocol}://{domain}/{encoded_path}"
        
        # 生成二维码
        qr_filename = f"{dir_name}_qr.png"
        qr_path = os.path.join(directory, qr_filename)
        
        if self.generate_qrcode(oss_url, qr_path, qr_size_mm):
            self.log(f"  二维码已生成: {qr_filename}")
            self.log(f"  二维码URL: {oss_url}")
        else:
            self.log(f"  二维码生成失败")
            return
        
        # 生成PDF
        pdf_filename = f"{dir_name}_qr.pdf"
        pdf_path = os.path.join(directory, pdf_filename)
        
        if self.create_pdf_with_qrcode(qr_path, pdf_path, page_size, qr_size_mm, x_mm, y_mm):
            self.log(f"  PDF已生成: {pdf_filename}")
        else:
            self.log(f"  PDF生成失败")
    
    def start_processing(self):
        """开始处理"""
        # 验证输入
        root_dir = self.root_dir_var.get()
        if not root_dir or not os.path.isdir(root_dir):
            messagebox.showerror("错误", "请选择有效的根目录")
            return
        
        page_size = self.get_page_size()
        if page_size is None:
            return
        
        try:
            qr_size_mm = float(self.qr_size_var.get())
            x_mm = float(self.qr_x_var.get())
            y_mm = float(self.qr_y_var.get())
        except ValueError:
            messagebox.showerror("错误", "二维码大小和坐标必须是数字")
            return
        
        auto_upload = self.auto_upload_var.get()
        
        if auto_upload and not self.oss_config.is_valid():
            result = messagebox.askyesno("OSS未配置", 
                                        "你选择了自动上传，但OSS未配置。\n是否继续（仅生成二维码和PDF）？")
            if not result:
                return
            auto_upload = False
        
        # 在新线程中处理，避免阻塞GUI
        thread = threading.Thread(target=self.process_all_directories,
                                 args=(root_dir, page_size, qr_size_mm, x_mm, y_mm, auto_upload))
        thread.daemon = True
        thread.start()
    
    def upload_only(self):
        """仅上传到OSS"""
        if not self.oss_config.is_valid():
            messagebox.showerror("错误", "请先配置OSS")
            return
        
        root_dir = self.root_dir_var.get()
        if not root_dir or not os.path.isdir(root_dir):
            messagebox.showerror("错误", "请选择有效的根目录")
            return
        
        thread = threading.Thread(target=self.upload_all_directories, args=(root_dir,))
        thread.daemon = True
        thread.start()
    
    def upload_all_directories(self, root_dir):
        """仅上传所有目录到OSS"""
        try:
            self.upload_button.config(state='disabled')
            self.start_button.config(state='disabled')
            self.progress_bar.start()
            self.progress_var.set("正在上传...")
            
            self.log("=" * 60)
            self.log("开始上传到OSS...")
            self.log(f"根目录: {root_dir}")
            self.log("=" * 60)
            
            dir_type = self.dir_type_var.get()
            target_dirs = self.get_target_directories(root_dir, dir_type)
            
            self.log(f"找到 {len(target_dirs)} 个目标目录")
            self.log("")
            
            total_success = 0
            total_fail = 0
            
            for target_dir in target_dirs:
                dir_name = os.path.basename(target_dir)
                self.log(f"上传目录: {dir_name}")
                
                images = self.get_images_in_directory(target_dir)
                if not images:
                    self.log(f"  跳过（无图片）")
                    self.log("")
                    continue
                
                # 合并图片
                merged_filename = f"{dir_name}_merged.jpg"
                merged_path = os.path.join(target_dir, merged_filename)
                
                self.log(f"  合并 {len(images)} 张图片...")
                if not self.merge_images_horizontally(images, merged_path):
                    self.log(f"  图片合并失败，跳过")
                    total_fail += 1
                    self.log("")
                    continue
                
                # 上传合并后的图片
                success, oss_url = self.upload_merged_image_to_oss(merged_path, target_dir, root_dir)
                if success:
                    total_success += 1
                else:
                    total_fail += 1
                
                self.log("")
            
            self.log("=" * 60)
            self.log(f"上传完成！成功 {total_success} 个目录，失败 {total_fail} 个")
            self.log("=" * 60)
            
            self.progress_var.set("上传完成")
            messagebox.showinfo("完成", f"上传完成！\n成功: {total_success}\n失败: {total_fail}")
            
        except Exception as e:
            self.log(f"上传过程中出错: {str(e)}")
            messagebox.showerror("错误", f"上传过程中出错: {str(e)}")
        finally:
            self.upload_button.config(state='normal')
            self.start_button.config(state='normal')
            self.progress_bar.stop()
    
    def process_all_directories(self, root_dir, page_size, qr_size_mm, x_mm, y_mm, auto_upload):
        """处理所有目录（在后台线程中运行）"""
        try:
            # 禁用按钮
            self.start_button.config(state='disabled')
            self.upload_button.config(state='disabled')
            self.progress_bar.start()
            self.progress_var.set("正在处理...")
            
            self.log("=" * 60)
            self.log("开始处理...")
            self.log(f"根目录: {root_dir}")
            self.log(f"目录类型: {self.dir_type_var.get()}")
            self.log(f"页面尺寸: {self.page_size_var.get()}")
            self.log(f"二维码大小: {qr_size_mm}mm")
            self.log(f"二维码位置: ({x_mm}mm, {y_mm}mm)")
            self.log(f"自动上传: {'是' if auto_upload else '否'}")
            self.log("=" * 60)
            
            # 获取目标目录
            dir_type = self.dir_type_var.get()
            target_dirs = self.get_target_directories(root_dir, dir_type)
            
            self.log(f"找到 {len(target_dirs)} 个目标目录")
            self.log("")
            
            # 处理每个目录
            success_count = 0
            for target_dir in target_dirs:
                self.process_directory(target_dir, page_size, qr_size_mm, x_mm, y_mm, auto_upload, root_dir)
                success_count += 1
                self.log("")
            
            self.log("=" * 60)
            self.log(f"处理完成！共处理 {success_count} 个目录")
            self.log("=" * 60)
            
            self.progress_var.set("处理完成")
            messagebox.showinfo("完成", f"处理完成！共处理 {success_count} 个目录")
            
        except Exception as e:
            self.log(f"处理过程中出错: {str(e)}")
            messagebox.showerror("错误", f"处理过程中出错: {str(e)}")
        finally:
            # 恢复按钮
            self.start_button.config(state='normal')
            self.upload_button.config(state='normal')
            self.progress_bar.stop()


def main():
    """主函数"""
    root = tk.Tk()
    app = DocumentProcessorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
