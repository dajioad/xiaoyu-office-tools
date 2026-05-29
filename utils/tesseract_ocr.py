import os
import tempfile
import subprocess
from typing import Union, List, Dict, Tuple
from PIL import Image
import pytesseract

from utils.ocr_config import get_tesseract_exe_path, get_tessdata_dir, check_language_packs


class TesseractOCR:
    def __init__(self, lang='eng+chi_sim', tesseract_cmd=None, tessdata_dir=None):
        self.lang = lang
        self.tesseract_cmd = tesseract_cmd or get_tesseract_exe_path() or 'tesseract'
        self.tessdata_dir = tessdata_dir or get_tessdata_dir()
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd
        if self.tessdata_dir:
            os.environ['TESSDATA_PREFIX'] = self.tessdata_dir
    
    def recognize(self, image: Union[str, Image.Image], preprocess=True, oem=1, psm=6) -> str:
        try:
            if isinstance(image, str):
                img = Image.open(image)
            else:
                img = image
            
            if preprocess:
                import cv2
                import numpy as np
                arr = np.array(img)
                if len(arr.shape) == 3:
                    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
                else:
                    gray = arr
                # 简单预处理：去噪 + 二值化
                gray = cv2.medianBlur(gray, 3)
                _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                img = Image.fromarray(binary)
            
            config = f'--oem {oem} --psm {psm}'
            text = pytesseract.image_to_string(img, lang=self.lang, config=config)
            return text.strip()
        except Exception as e:
            return f"[OCR 失败: {str(e)}]"
    
    def recognize_to_dict(self, image: Union[str, Image.Image]) -> Dict:
        if isinstance(image, str):
            img = Image.open(image)
        else:
            img = image
        data = pytesseract.image_to_data(img, lang=self.lang, output_type=pytesseract.Output.DICT)
        words = []
        for i in range(len(data['text'])):
            txt = data['text'][i].strip()
            if txt and int(data['conf'][i]) > 0:
                words.append({
                    'text': txt,
                    'confidence': float(data['conf'][i]),
                    'bbox': {'x': data['left'][i], 'y': data['top'][i], 'w': data['width'][i], 'h': data['height'][i]}
                })
        return {'full_text': ' '.join([w['text'] for w in words]), 'words': words, 'language': self.lang}
    
    def batch_recognize(self, images: List[str], preprocess=True) -> List[str]:
        return [self.recognize(p, preprocess=preprocess) for p in images]
    
    @staticmethod
    def check_installation() -> Tuple[bool, str]:
        try:
            ver = pytesseract.get_tesseract_version()
            return True, f"Tesseract {ver}"
        except:
            return False, "Tesseract 未安装或未配置"

def quick_ocr(img_path: str, lang='eng+chi_sim') -> str:
    return TesseractOCR(lang=lang).recognize(img_path)