"""LaTeX math to spoken English (zero dependencies, stdlib only).

Shared converter used by the plugin's agent tool and its TTS provider.
``$v = c_1 v_1$`` -> ``v equals c sub 1 v sub 1``.

Currency is preserved: ``$5`` never opens a span, and ``$5/month`` /
``US$300`` keep reading as money.
"""

from __future__ import annotations

import re

_MATH_DISPLAY_DOLLAR_RE = re.compile(r"\$\$(.+?)\$\$", flags=re.DOTALL)
_MATH_DISPLAY_BRACKET_RE = re.compile(r"\\\[(.+?)\\\]", flags=re.DOTALL)
_MATH_PAREN_RE = re.compile(r"\\\((.+?)\\\)", flags=re.DOTALL)
_MATH_INLINE_MARKED_RE = re.compile(r"(?<!\$)\$(?!\$)([^$\n]*?[\\^_{}=][^$\n]*?)(?<!\$)\$(?!\$)")
_MATH_INLINE_PLAIN_RE = re.compile(r"(?<!\$)\$(?!\$)([^$\d\s][^$\n]*?)(?<!\$)\$(?!\$)")
_MATH_NUMERIC_RE = re.compile(r"^[\d,\.\s]+$")

_MATH_GREEK = {
    "\\alpha": "alpha", "\\beta": "beta", "\\gamma": "gamma", "\\delta": "delta",
    "\\epsilon": "epsilon", "\\zeta": "zeta", "\\eta": "eta", "\\theta": "theta",
    "\\lambda": "lambda", "\\mu": "mu", "\\nu": "nu", "\\xi": "xi", "\\pi": "pi",
    "\\rho": "rho", "\\sigma": "sigma", "\\tau": "tau", "\\phi": "phi",
    "\\chi": "chi", "\\psi": "psi", "\\omega": "omega", "\\Gamma": "Gamma",
    "\\Delta": "Delta", "\\Theta": "Theta", "\\Lambda": "Lambda", "\\Sigma": "Sigma",
    "\\Omega": "Omega",
}
_MATH_OPERATORS = {
    "\\times": "times", "\\cdot": "times", "\\pm": "plus or minus",
    "\\geq": "greater than or equal to", "\\ge": "greater than or equal to",
    "\\leq": "less than or equal to", "\\le": "less than or equal to",
    "\\approx": "approximately", "\\sim": "approximately",
    "\\neq": "not equal to", "\\ne": "not equal to",
    "\\rightarrow": "to", "\\to": "to", "\\leftarrow": "from",
    "\\infty": "infinity", "\\propto": "proportional to",
    "\\equiv": "is equivalent to", "\\gg": "much greater than", "\\ll": "much less than",
    "\\sum": "sum of", "\\int": "integral of", "\\partial": "partial",
}
_MATH_UNICODE = {
    "\u03b1": "alpha", "\u03b2": "beta", "\u03b3": "gamma", "\u03b4": "delta",
    "\u03b5": "epsilon", "\u03b8": "theta", "\u03bb": "lambda", "\u03bc": "mu",
    "\u03bd": "nu", "\u03be": "xi", "\u03c0": "pi", "\u03c1": "rho",
    "\u03c3": "sigma", "\u03c4": "tau", "\u03c6": "phi", "\u03c7": "chi",
    "\u03c8": "psi", "\u03c9": "omega", "\u0394": "Delta", "\u03a3": "Sigma", "\u03a9": "Omega",
    "\u00d7": "times", "\u00b1": "plus or minus", "\u2265": "greater than or equal to",
    "\u2264": "less than or equal to", "\u2248": "approximately", "\u223c": "approximately",
    "\u2260": "not equal to", "\u2192": "to", "\u21d2": "to", "\u221e": "infinity",
    "\u00b2": "squared", "\u00b3": "cubed", "\u221a": "square root of",
}
_MATH_FRAC_RE = re.compile(r"\\d?frac\{([^{}]*)\}\{([^{}]*)\}")
_MATH_SQRT_RE = re.compile(r"\\sqrt(?:\[([^\]]*)\])?\{([^{}]*)\}")
_MATH_SUP_BRACED_RE = re.compile(r"\^\{([^{}]*)\}")
_MATH_SUP_SINGLE_RE = re.compile(r"\^(\w)")
_MATH_SUB_BRACED_RE = re.compile(r"_\{([^{}]*)\}")
_MATH_SUB_SINGLE_RE = re.compile(r"_(\w)")
_MATH_TEXT_CMD_RE = re.compile(r"\\(?:mathrm|text|mathit|mathbf|operatorname)\{([^{}]*)\}")
_MATH_CMD_RE = re.compile(r"\\[a-zA-Z]+\*?")
_MATH_SPACING_RE = re.compile(r"\\[,;:!]")
_MATH_SUM_LIMITS_RE = re.compile(r"\\sum\s*_(\{([^{}]*)\}|(\w))\s*\^\s*(\{([^{}]*)\}|(\w))")
_MATH_INT_LIMITS_RE = re.compile(r"\\int\s*_(\{([^{}]*)\}|(\w))\s*\^\s*(\{([^{}]*)\}|(\w))")
_MATH_DOTS = ("\\cdots", "\\ldots", "\\vdots", "\\ddots")


def _limits_repl(word):
    def repl(m):
        lo = m.group(2) if m.group(2) is not None else m.group(3)
        hi = m.group(5) if m.group(5) is not None else m.group(6)
        return "%s from %s to %s" % (word, lo, hi)
    return repl


def _convert_math_expression(expr: str) -> str:
    s = expr.strip()
    s = _MATH_SPACING_RE.sub(" ", s)
    s = _MATH_SUM_LIMITS_RE.sub(_limits_repl("sum"), s)
    s = _MATH_INT_LIMITS_RE.sub(_limits_repl("integral"), s)
    for dots in _MATH_DOTS:
        s = s.replace(dots, " dot dot dot ")
    s = _MATH_FRAC_RE.sub(r"\1 over \2", s)
    s = _MATH_SQRT_RE.sub(
        lambda m: "square root of %s" % m.group(2) if not m.group(1)
        else "%s root of %s" % (m.group(1), m.group(2)), s)
    for cmd, word in _MATH_GREEK.items():
        s = s.replace(cmd, " %s " % word)
    for cmd, word in _MATH_OPERATORS.items():
        s = s.replace(cmd, " %s " % word)
    s = _MATH_SUP_BRACED_RE.sub(r" to the \1", s)
    s = _MATH_SUP_SINGLE_RE.sub(r" to the \1", s)
    s = _MATH_SUB_BRACED_RE.sub(r" sub \1", s)
    s = _MATH_SUB_SINGLE_RE.sub(r" sub \1", s)
    s = s.replace("*", " times ").replace("=", " equals ")
    s = s.replace("<", " less than ").replace(">", " greater than ")
    s = s.replace("|", " ")
    s = _MATH_TEXT_CMD_RE.sub(r"\1", s)
    s = _MATH_CMD_RE.sub("", s)
    s = s.replace("{", " ").replace("}", " ")
    return re.sub(r"\s+", " ", s).strip()


def _convert_math_marked(match) -> str:
    inner = match.group(1)
    if _MATH_NUMERIC_RE.match((inner.strip() or " ")):
        return match.group(0)
    return " %s " % _convert_math_expression(inner)


def _unwrap_math_plain(match) -> str:
    inner = match.group(1)
    if _MATH_NUMERIC_RE.match((inner.strip() or " ")):
        return match.group(0)
    return " %s " % inner.strip()


def speak_math(text: str) -> str:
    """Rewrite LaTeX math spans as spoken English.

    ``$v = c_1 v_1$`` -> ``v equals c sub 1 v sub 1``. Plain ``$v$`` unwraps
    to ``v``; ``$5``/``$5/month``/``US$300`` are left for currency handling.
    """
    if not text or ("$" not in text and "\\" not in text):
        return text or ""
    text = str(text)
    for char, word in _MATH_UNICODE.items():
        text = text.replace(char, " %s " % word)
    for pattern, handler in ((_MATH_DISPLAY_DOLLAR_RE, _convert_math_marked),
                             (_MATH_DISPLAY_BRACKET_RE, _convert_math_marked),
                             (_MATH_PAREN_RE, _convert_math_marked),
                             (_MATH_INLINE_MARKED_RE, _convert_math_marked),
                             (_MATH_INLINE_PLAIN_RE, _unwrap_math_plain)):
        text = pattern.sub(handler, text)
    return re.sub(r"[ \t]{2,}", " ", text)
