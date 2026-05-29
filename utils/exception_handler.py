import sys
import threading
import traceback
from typing import Callable, Any
from PySide6.QtWidgets import QMessageBox, QApplication
from PySide6.QtCore import QMetaObject, Qt


class ExceptionHandler:
    """统一异常处理器"""

    @staticmethod
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        error_msg = f"""
错误类型: {exc_type.__name__}
错误信息: {str(exc_value)}

详细信息:
{''.join(traceback.format_tb(exc_traceback))}
"""
        try:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setWindowTitle("程序错误")
            msg_box.setText("程序运行过程中发生错误")
            msg_box.setDetailedText(error_msg)
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec()
        except:
            print(f"程序错误: {exc_type.__name__}: {exc_value}")

    @staticmethod
    def catch_and_show(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                ExceptionHandler.show_error("操作失败", str(e))
                return None
        return wrapper

    @staticmethod
    def show_error(title: str, message: str, detailed: str = ""):
        if QApplication.instance() and QApplication.instance().thread() != threading.current_thread():
            QMetaObject.invokeMethod(
                QApplication.instance(),
                lambda: ExceptionHandler._show_error_dialog(title, message, detailed),
                Qt.QueuedConnection
            )
        else:
            ExceptionHandler._show_error_dialog(title, message, detailed)

    @staticmethod
    def _show_error_dialog(title: str, message: str, detailed: str):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        if detailed:
            msg_box.setDetailedText(detailed)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()

    @staticmethod
    def show_warning(title: str, message: str):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()

    @staticmethod
    def show_info(title: str, message: str):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()

    @staticmethod
    def ask_question(title: str, message: str) -> bool:
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        return msg_box.exec() == QMessageBox.Yes

    @staticmethod
    def setup_global_exception_handler():
        sys.excepthook = ExceptionHandler.handle_exception


class FileOperationException(Exception):
    pass


class ConfigurationException(Exception):
    pass


class ValidationException(Exception):
    pass


class SecurityException(Exception):
    pass