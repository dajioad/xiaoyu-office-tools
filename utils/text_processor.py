import re

class TextProcessor:
    def __init__(self):
        self.language = "zh"
        self.split_mode = 0
        self.custom_symbols = {}

    def set_language(self, lang):
        self.language = lang

    def set_custom_symbols(self, syms):
        self.custom_symbols = syms

    def get_symbol_config(self):
        if self.language == "en":
            return {
                "double_quote": ('"', '"', '""'),
                "single_quote": ("'", "'", "''"),
                "book_title": ("<<", ">>", "<<>>"),
                "bracket": ("(", ")", "()"),
                "square_bracket": ("[", "]", "[]"),
                "curly_bracket": ("{", "}", "{}"),
            }
        else:
            return {
                "double_quote": ('"', '"', '""'),
                "single_quote": ('\'', '\'', '\'\''),
                "book_title": ("《", "》", "《》"),
                "bracket": ("（", "）", "（）"),
                "square_bracket": ("【", "】", "【】"),
                "curly_bracket": ("｛", "｝", "｛｝"),
            }

    def process_text(self, text, operation, position, full_width=True, overlay_chain=None, custom_delimiter=None):
        if overlay_chain:
            result = text
            for op in overlay_chain:
                result = self._apply_op(result, op["symbol"], op["position"], full_width, custom_delimiter)
            return self._apply_op(result, operation, position, full_width, custom_delimiter)
        return self._apply_op(text, operation, position, full_width, custom_delimiter)

    def _apply_op(self, text, op, pos, full_width, custom_delimiter):
        symbol = self._get_symbol(op, full_width)
        if pos == "split":
            return self._split_and_wrap(text, symbol, custom_delimiter)
        elif pos == "head":
            return symbol[0] + text
        elif pos == "tail":
            return text + symbol[-1]
        elif pos == "both":
            if len(symbol) >= 2:
                return symbol[0] + text + symbol[1]
            else:
                return symbol + text + symbol
        return text

    def _get_symbol(self, key, full_width):
        cfg = self.get_symbol_config()
        if key in cfg:
            left, right, _ = cfg[key]
            return left + right
        elif key in self.custom_symbols:
            sym = self.custom_symbols[key]
            if isinstance(sym, dict):
                return sym.get("full", "") if full_width else sym.get("half", "")
            return sym
        else:
            return key

    def _split_and_wrap(self, text, symbol, custom_delimiter=None):
        chars = list(text)
        if len(symbol) == 1:
            wrapped = [f"{symbol}{c}{symbol}" for c in chars]
            return "".join(wrapped)
        elif len(symbol) >= 2:
            left, right = symbol[0], symbol[1]
            wrapped = [f"{left}{c}{right}" for c in chars]
            return "".join(wrapped)
        return text