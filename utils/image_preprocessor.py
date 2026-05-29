import os
import logging
logger = logging.getLogger(__name__)

_cv2 = None
def _cv():
    global _cv2
    if _cv2 is None:
        try:
            import cv2
            _cv2 = cv2
        except ImportError:
            _cv2 = False
    return _cv2

class ImagePreprocessor:
    @staticmethod
    def load_image(path):
        cv = _cv()
        if not cv: raise ImportError("OpenCV未安装")
        img = cv.imread(path)
        if img is None: raise ValueError(f"无法加载图像: {path}")
        return img

    @staticmethod
    def to_grayscale(img):
        cv = _cv()
        return cv.cvtColor(img, cv.COLOR_BGR2GRAY) if cv else img

    @staticmethod
    def to_binary(img, thresh=128):
        cv = _cv()
        if not cv: return img
        _, bin_img = cv.threshold(img, thresh, 255, cv.THRESH_BINARY)
        return bin_img

    @staticmethod
    def denoise(img):
        cv = _cv()
        return cv.medianBlur(img, 5) if cv else img

    @staticmethod
    def sharpen(img):
        cv = _cv()
        if not cv: return img
        kernel = cv.getStructuringElement(cv.MORPH_RECT, (3,3))
        return cv.dilate(img, kernel)

    @staticmethod
    def resize(img, w, h):
        cv = _cv()
        return cv.resize(img, (w, h)) if cv else img

    @staticmethod
    def preprocess_for_ocr(path, cfg=None):
        cv = _cv()
        if not cv: raise ImportError("OpenCV未安装")
        if cfg is None:
            cfg = {'grayscale':True, 'binary':False, 'threshold':128,
                   'denoise':False, 'sharpen':False, 'width':1200, 'height':None}
        img = cv.imread(path)
        if img is None: raise ValueError(f"无法加载: {path}")
        if cfg.get('grayscale'):
            img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        if cfg.get('denoise'):
            img = cv.medianBlur(img, 5)
        if cfg.get('sharpen'):
            kernel = cv.getStructuringElement(cv.MORPH_RECT, (3,3))
            img = cv.dilate(img, kernel)
        if cfg.get('binary'):
            _, img = cv.threshold(img, cfg['threshold'], 255, cv.THRESH_BINARY)
        w = cfg['width']
        h = cfg['height']
        if h:
            img = cv.resize(img, (w, h))
        else:
            hh, ww = img.shape[:2]
            img = cv.resize(img, (w, int(w * hh / ww)))
        out = path.rsplit('.', 1)[0] + '_processed.png'
        cv.imwrite(out, img)
        return out