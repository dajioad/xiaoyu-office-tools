import os
import sys
import glob
from pathlib import Path

TESSERACT_CONFIG = {
    'tesseract_cmd': None, 'tessdata_dir': None,
    'lang': 'eng+chi_sim', 'oem': 1, 'psm': 6, 'config_vars': {}
}
TESSDATA_PREFIX = None
TESSERACT_PATH = None
_USER_CONFIGURED_PATH = None
_USER_CONFIGURED_TESSDATA = None

def get_project_root():
    return Path(__file__).parent.parent

def set_user_tesseract_path(path):
    """设置用户自定义的tesseract路径"""
    global _USER_CONFIGURED_PATH
    _USER_CONFIGURED_PATH = path

def set_user_tessdata_dir(path):
    """设置用户自定义的tessdata目录"""
    global _USER_CONFIGURED_TESSDATA
    _USER_CONFIGURED_TESSDATA = path

def get_tesseract_exe_path():
    # 1. 优先使用用户配置
    if _USER_CONFIGURED_PATH:
        if os.path.exists(_USER_CONFIGURED_PATH):
            return _USER_CONFIGURED_PATH
    
    # 2. 检查系统PATH
    try:
        import shutil
        system_path = shutil.which('tesseract')
        if system_path:
            return system_path
    except:
        pass
    
    # 3. 回退到项目内置目录
    root = get_project_root()
    dirs = [root/'tesseract', root/'tesseract-5.5.2', root/'tesseract-ocr', root/'ocr'/'tesseract']
    if sys.platform == 'win32':
        for d in dirs:
            exe = d/'tesseract.exe'
            if exe.exists(): return str(exe)
            for sub in ['x64/Release','x86/Release','bin','Debug','build']:
                exe = d/sub/'tesseract.exe'
                if exe.exists(): return str(exe)
    else:
        # macOS/Linux 常用安装路径
        common_paths = [
            '/usr/bin/tesseract',
            '/usr/local/bin/tesseract',
            '/opt/homebrew/bin/tesseract'
        ]
        for path in common_paths:
            if os.path.exists(path):
                return path
        for d in dirs:
            exe = d/'tesseract'
            if exe.exists(): return str(exe)
    return None

def get_tessdata_dir():
    # 1. 优先使用用户配置
    if _USER_CONFIGURED_TESSDATA:
        if os.path.exists(_USER_CONFIGURED_TESSDATA):
            return _USER_CONFIGURED_TESSDATA
    
    # 2. 检查环境变量
    env_tessdata = os.environ.get('TESSDATA_PREFIX')
    if env_tessdata and os.path.exists(env_tessdata):
        return env_tessdata
    
    # 3. 回退到项目内置目录
    root = get_project_root()
    for p in [root/'tesseract'/'tessdata', root/'tesseract-5.5.2'/'tessdata',
              root/'tesseract-ocr'/'tessdata', root/'ocr'/'tesseract'/'tessdata', root/'tessdata']:
        if p.exists(): return str(p)
    
    # 4. 检查常见系统路径
    common_paths = [
        '/usr/share/tessdata',
        '/usr/local/share/tessdata',
        '/opt/homebrew/share/tessdata'
    ]
    for path in common_paths:
        if os.path.exists(path):
            return path
    return None

def check_language_packs():
    td = get_tessdata_dir()
    if not td: return False, "tessdata目录不存在"
    missing = [p for p in ['eng.traineddata', 'chi_sim.traineddata'] if not os.path.exists(os.path.join(td, p))]
    return (False, f"缺少语言包: {', '.join(missing)}") if missing else (True, "就绪")

def get_available_languages():
    td = get_tessdata_dir()
    return [os.path.basename(f) for f in glob.glob(os.path.join(td, '*.traineddata'))] if td else []

def initialize_tesseract_config():
    global TESSDATA_PREFIX, TESSERACT_PATH
    TESSERACT_PATH = get_tesseract_exe_path()
    td = get_tessdata_dir()
    if td:
        TESSDATA_PREFIX = td
        os.environ['TESSDATA_PREFIX'] = td
        TESSERACT_CONFIG['tessdata_dir'] = td
    if TESSERACT_PATH:
        TESSERACT_CONFIG['tesseract_cmd'] = TESSERACT_PATH
    ok, msg = check_language_packs()
    print(f"{'✅' if ok else '⚠️'} Tesseract: {msg}")
    return ok

def get_ocr_params():
    return {'lang': TESSERACT_CONFIG['lang'], 'oem': TESSERACT_CONFIG['oem'],
            'psm': TESSERACT_CONFIG['psm'], 'tessdata_dir': TESSDATA_PREFIX}

def download_language_packs():
    base = "https://github.com/tesseract-ocr/tessdata/raw/main/"
    return {'eng.traineddata': base+'eng.traineddata', 'chi_sim.traineddata': base+'chi_sim.traineddata'}

def validate_tesseract_installation():
    try:
        import subprocess
        cmd = TESSERACT_CONFIG.get('tesseract_cmd') or 'tesseract'
        r = subprocess.run([cmd, '--version'], capture_output=True, text=True, timeout=10)
        if r.returncode == 0:
            return True, "Tesseract已安装", r.stdout.split('\n')[0]
        return False, "命令执行失败", None
    except Exception as e:
        return False, f"验证失败: {str(e)}", None