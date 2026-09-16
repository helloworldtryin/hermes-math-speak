import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mathtext import speak_math

D = "$"


def test_inline_subscripts():
    out = speak_math("Every vector " + D + "v = c_1 v_1 + c_2 v_2" + D + " here.")
    assert "$" not in out
    assert "v equals c sub 1 v sub 1" in out
    assert "c sub 2 v sub 2" in out


def test_greek_and_operators():
    out = speak_math("Angles " + D + "\\alpha \\leq \\beta" + D + " done.")
    assert "alpha less than or equal to beta" in out


def test_fraction_and_powers():
    out = speak_math("Value " + D + "\\frac{1}{2}" + D + " and " + D + "x^2" + D + ".")
    assert "1 over 2" in out
    assert "x to the 2" in out


def test_sum_and_integral_limits():
    out = speak_math("Sum " + D + "\\sum_{i=1}^{n} x_i" + D + " ok.")
    assert "sum from i equals 1 to n" in out
    assert "x sub i" in out
    out = speak_math("Eval " + D + "\\int_0^1 x^2 dx" + D + ".")
    assert "integral from 0 to 1" in out


def test_display_math():
    out = speak_math(D * 2 + "\nv = c_1 v_1 + \\cdots + c_n v_n\n" + D * 2)
    assert "v equals c sub 1 v sub 1" in out
    assert "dot dot dot" in out
    assert "$" not in out


def test_currency_untouched():
    # Currency expansion ("5 dollars") is the host pipeline's job; the
    # converter must simply not pair or mangle it as math.
    assert speak_math("It costs " + D + "5/month") == "It costs " + D + "5/month"
    assert speak_math("US" + D + "300, next") == "US" + D + "300, next"


def test_plain_prose_passthrough():
    assert speak_math("plain prose, no math.") == "plain prose, no math."
    assert speak_math("") == ""
