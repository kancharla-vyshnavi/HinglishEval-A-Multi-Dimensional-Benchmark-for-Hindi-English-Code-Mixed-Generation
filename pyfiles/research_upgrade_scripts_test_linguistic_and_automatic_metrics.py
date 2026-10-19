import sys
import os
import unittest
import math
import re

sys.stdout.reconfigure(encoding="utf-8")

# 1. Unit Test for Das & Gamback CMI
def calculate_das_gamback_cmi(n_hi, n_en):
    total = n_hi + n_en
    if total == 0:
        return 0.0
    return 100.0 * (min(n_hi, n_en) / total)

def calculate_gamback_total_cmi(n_hi, n_en, n_univ):
    total = n_hi + n_en + n_univ
    if total == 0:
        return 0.0
    return 100.0 * (min(n_hi, n_en) / total)

# 2. Unit Test for Equal-Length Distinct-n
def compute_distinct_n(text, k=25):
    tokens = re.findall(r"[A-Za-z0-9\u0900-\u097F]+", str(text).lower())
    n = len(tokens)
    if n == 0:
        return 0.0, 0.0, 0.0
    sub = tokens[:k] if n >= k else tokens
    sub_len = len(sub)
    d1 = len(set(sub)) / sub_len
    rep = 1.0 - d1
    bigrams = [tuple(sub[i:i+2]) for i in range(sub_len - 1)]
    d2 = (len(set(bigrams)) / len(bigrams)) if bigrams else 1.0
    return d1, d2, rep

# 3. Unit Test for Bits-Per-Character (BPC)
def calculate_bpc(perplexity, chars_per_token):
    # loss_in_nats = ln(PPL)
    # loss_in_bits = ln(PPL) / ln(2)
    # BPC = loss_in_bits / chars_per_token
    loss_nats = math.log(perplexity)
    loss_bits = loss_nats / math.log(2)
    return loss_bits / chars_per_token

# 4. Unit Test for E1-E10 Heuristic Rules
def detect_e1(r_en, r_hi, r_roman_hi):
    return (r_en >= 0.45) and (r_hi < 0.10) and (r_roman_hi < 0.10)

def detect_e5(text):
    tokens = re.findall(r"\w+", text.lower())
    if not tokens:
        return False
    adj_rep = sum(1 for i in range(len(tokens) - 1) if tokens[i] == tokens[i+1])
    return (adj_rep / len(tokens)) >= 0.18

def detect_e8(text):
    # Character elongation >= 4 or consonant clusters >= 8 with 0 vowels
    if re.search(r"(.)\1{4,}", text):
        return True
    words = text.split()
    vowels = set("aeiou")
    for w in words:
        clean_w = re.sub(r"[^a-zA-Z]", "", w.lower())
        if len(clean_w) >= 8 and not any(c in vowels for c in clean_w):
            return True
    return False

class TestTask2Metrics(unittest.TestCase):
    def test_cmi_pure_english(self):
        cmi = calculate_das_gamback_cmi(0, 10)
        self.assertEqual(cmi, 0.0, "Pure English should have CMI = 0.0")

    def test_cmi_pure_hindi(self):
        cmi = calculate_das_gamback_cmi(10, 0)
        self.assertEqual(cmi, 0.0, "Pure Hindi should have CMI = 0.0")

    def test_cmi_balanced_50_50(self):
        cmi = calculate_das_gamback_cmi(5, 5)
        self.assertEqual(cmi, 50.0, "50-50 mix should have CMI = 50.0%")

    def test_cmi_with_universal_tokens(self):
        cmi_total = calculate_gamback_total_cmi(5, 5, 10)
        self.assertEqual(cmi_total, 25.0, "5 HI, 5 EN, 10 UNIV should have Total CMI = 25.0%")

    def test_distinct_n_all_unique(self):
        text = "a b c d e f g h i j k l m n o p q r s t u v w x y"
        d1, d2, rep = compute_distinct_n(text, k=25)
        self.assertEqual(d1, 1.0, "All unique tokens should give Distinct-1 = 1.0")
        self.assertEqual(rep, 0.0, "All unique tokens should give Repetition Rate = 0.0")

    def test_distinct_n_repetitive_loop(self):
        text = "ha ha ha ha ha ha ha ha ha ha ha ha ha ha ha ha ha ha ha ha ha ha ha ha ha"
        d1, d2, rep = compute_distinct_n(text, k=25)
        self.assertAlmostEqual(d1, 1.0 / 25, places=3)
        self.assertAlmostEqual(rep, 24.0 / 25, places=3)

    def test_bpc_calculation(self):
        # PPL = 4.0, chars_per_token = 2.0
        # loss_bits = log2(4) = 2.0
        # BPC = 2.0 / 2.0 = 1.0
        bpc = calculate_bpc(4.0, 2.0)
        self.assertAlmostEqual(bpc, 1.0, places=4)

    def test_e1_english_dominance(self):
        self.assertTrue(detect_e1(0.80, 0.02, 0.01))
        self.assertFalse(detect_e1(0.30, 0.40, 0.20))

    def test_e5_repetition_loop(self):
        self.assertTrue(detect_e5("bhai bhai bhai bhai bhai sun sun sun"))
        self.assertFalse(detect_e5("main kal shaam ko aane wala hoon"))

    def test_e8_elongation_and_consonant_cluster(self):
        self.assertTrue(detect_e8("areeeeee yaar ye kya hai"))
        self.assertTrue(detect_e8("kuch smjhnbcdfg nahi aaya"))
        self.assertFalse(detect_e8("theek hai sab kuch normal hai"))

if __name__ == "__main__":
    unittest.main()
