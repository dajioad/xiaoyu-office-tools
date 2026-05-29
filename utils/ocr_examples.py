"""
Tesseract OCR 使用示例

本模块提供中英文OCR识别的完整使用示例和最佳实践

安装说明:
    1. 确保已安装Tesseract 5.x
       - Windows: 从 https://github.com/UB-Mannheim/tesseract/wiki 下载
       - Linux: sudo apt-get install tesseract-ocr
       - macOS: brew install tesseract
    
    2. 下载语言包（英文+简体中文）:
       - eng.traineddata
       - chi_sim.traineddata
       
       从 https://github.com/tesseract-ocr/tessdata 获取
    
    3. 设置环境变量:
       - TESSDATA_PREFIX = <tessdata目录路径>
"""

import os
import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.tesseract_ocr import TesseractOCR, quick_ocr
from utils.ocr_config import (
    initialize_tesseract_config,
    validate_tesseract_installation,
    check_language_packs,
    download_language_packs
)
from utils.image_preprocessor import ImagePreprocessor
import cv2
import numpy as np


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_basic_usage():
    """
    示例1: 基本使用方法
    """
    print("\n" + "="*60)
    print("示例1: 基本使用方法")
    print("="*60)
    
    initialize_tesseract_config()
    
    ocr = TesseractOCR(lang='eng+chi_sim')
    
    image_path = "test_image.png"
    
    if os.path.exists(image_path):
        text = ocr.recognize(image_path)
        print(f"识别结果:\n{text}")
    else:
        print("测试图像不存在，跳过")


def example_with_preprocessing():
    """
    示例2: 带图像预处理的OCR
    """
    print("\n" + "="*60)
    print("示例2: 带图像预处理的OCR")
    print("="*60)
    
    ocr = TesseractOCR(lang='eng+chi_sim')
    
    image_path = "test_image.png"
    
    if os.path.exists(image_path):
        text = ocr.recognize(
            image_path,
            preprocess=True,
            enhance_contrast=True,
            binarize=False
        )
        print(f"预处理后识别结果:\n{text}")
    else:
        print("测试图像不存在，跳过")


def example_structured_output():
    """
    示例3: 结构化输出（包含位置信息）
    """
    print("\n" + "="*60)
    print("示例3: 结构化输出")
    print("="*60)
    
    ocr = TesseractOCR(lang='eng+chi_sim')
    
    image_path = "test_image.png"
    
    if os.path.exists(image_path):
        result = ocr.recognize_to_dict(image_path)
        
        print(f"完整文本: {result['full_text']}")
        print(f"\n文字数量: {len(result['words'])}")
        
        if result['words']:
            print("\n前5个文字块:")
            for i, word in enumerate(result['words'][:5]):
                print(f"  {i+1}. '{word['text']}' "
                      f"(置信度: {word['confidence']:.1f}%, "
                      f"位置: ({word['bbox']['x']}, {word['bbox']['y']}))")
    else:
        print("测试图像不存在，跳过")


def example_batch_processing():
    """
    示例4: 批量处理
    """
    print("\n" + "="*60)
    print("示例4: 批量处理")
    print("="*60)
    
    ocr = TesseractOCR(lang='eng+chi_sim')
    
    images = [
        "image1.png",
        "image2.png",
        "image3.png"
    ]
    
    existing_images = [img for img in images if os.path.exists(img)]
    
    if existing_images:
        results = ocr.batch_recognize(existing_images)
        
        for img, text in zip(existing_images, results):
            print(f"\n{img}:")
            print(f"  {text[:100]}..." if len(text) > 100 else f"  {text}")
    else:
        print("没有找到测试图像，跳过")


def example_image_preprocessing():
    """
    示例5: 图像预处理方法
    """
    print("\n" + "="*60)
    print("示例5: 图像预处理")
    print("="*60)
    
    image_path = "test_image.png"
    
    if not os.path.exists(image_path):
        print("测试图像不存在，跳过")
        return
    
    preprocessor = ImagePreprocessor()
    
    img = cv2.imread(image_path)
    gray = preprocessor.to_grayscale(img)
    
    denoised = preprocessor.denoise(gray, method='bilateral')
    
    enhanced = preprocessor.enhance_contrast(gray)
    
    binary = preprocessor.binarize(gray, method='otsu')
    
    print("预处理完成:")
    print(f"  - 灰度图: {gray.shape}")
    print(f"  - 去噪后: {denoised.shape}")
    print(f"  - 对比度增强: {enhanced.shape}")
    print(f"  - 二值化: {binary.shape}")


def example_troubleshooting():
    """
    示例6: 故障排除和验证
    """
    print("\n" + "="*60)
    print("示例6: 故障排除")
    print("="*60)
    
    success, msg, version = validate_tesseract_installation()
    if success:
        print(f"✅ {msg} (版本: {version})")
    else:
        print(f"❌ {msg}")
    
    has_packs, msg = check_language_packs()
    if has_packs:
        print(f"✅ 语言包: {msg}")
    else:
        print(f"❌ 语言包: {msg}")
        
        print("\n需要下载的语言包:")
        packs = download_language_packs()
        for name, url in packs.items():
            print(f"  - {name}: {url}")


def example_ocr_parameters():
    """
    示例7: OCR参数说明
    """
    print("\n" + "="*60)
    print("示例7: OCR参数说明")
    print("="*60)
    
    ocr = TesseractOCR(lang='eng+chi_sim')
    
    print("\n支持的参数组合:")
    
    params = [
        ("--oem 1 --psm 6", "LSTM神经网络模式，适合大多数文档"),
        ("--oem 1 --psm 4", "LSTM模式，假设单一文本列"),
        ("--oem 1 --psm 3", "LSTM模式，自动页面分割"),
        ("--oem 3 --psm 11", "自动选择模式，稀疏文本搜索"),
        ("--oem 1 --psm 7", "LSTM模式，单行文本"),
        ("--oem 1 --psm 8", "LSTM模式，单词识别"),
    ]
    
    for param, desc in params:
        print(f"\n  {param}")
        print(f"    说明: {desc}")
    
    print("\n参数详解:")
    print("""
    OEM (OCR Engine Mode):
        0 - 仅传统OCR引擎
        1 - 仅LSTM神经网络（推荐，准确率最高）
        2 - 传统 + LSTM
        3 - 自动选择最佳模式
    
    PSM (Page Segmentation Mode):
        0 - 方向检测和脚本检测
        1 - 自动页面分割与OSD
        3 - 全自动页面分割（默认）
        4 - 假设单一文本列
        5 - 假设统一文本块
        6 - 假设统一文本块（推荐用于文档）
        7 - 将图像视为单一文本行
        8 - 将图像视为单一单词
        9 - 将图像视为圆中的单个单词
        10 - 将图像视为单个字符
        11 - 稀疏文本搜索
        12 - 带OSD的稀疏文本
        13 - 原始线处理
    """)


def main():
    """
    主函数 - 运行所有示例
    """
    print("="*60)
    print("Tesseract OCR 使用示例")
    print("="*60)
    
    example_troubleshooting()
    
    example_basic_usage()
    
    example_with_preprocessing()
    
    example_structured_output()
    
    example_batch_processing()
    
    example_image_preprocessing()
    
    example_ocr_parameters()
    
    print("\n" + "="*60)
    print("示例完成")
    print("="*60)


if __name__ == "__main__":
    main()
