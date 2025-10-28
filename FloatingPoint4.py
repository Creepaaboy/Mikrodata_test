#!/usr/bin/env python3
"""
float_gui_quiz_final.py

Tkinter GUI quiz for IEEE-754 single-precision problems (1.1, 1.2, 1.3).
Randomized controlled difficulty, separate question sections, button-based grading, and correct IEEE-754 computation.

Author: Generated for user
"""

import tkinter as tk
from tkinter import ttk
import struct
import random
from decimal import Decimal, getcontext

getcontext().prec = 50  # High precision for decimal conversion

# ---------------- IEEE-754 helpers ----------------
def make_float_from_bits(s, E, F):
    word = ((s & 0x1) << 31) | ((E & 0xFF) << 23) | (F & 0x7FFFFF)
    packed = struct.pack(">I", word)
    return struct.unpack(">f", packed)[0]

def float_to_bits(f):
    packed = struct.pack(">f", f)
    word = struct.unpack(">I", packed)[0]
    s = (word >> 31) & 0x1
    E = (word >> 23) & 0xFF
    F = word & 0x7FFFFF
    return s, E, F

def leftmost_F_bits(F, n=6):
    return f"{(F >> (23 - n)) & ((1 << n) - 1):0{n}b}"

def E_to_8bit(E):
    return f"{E:08b}"

def decimal_scientific_components(single_float, frac_digits=6):
    """
    Return (sign_s, first_digit_d, fractional_str_m, exponent_e10, formatted_str)
    sign_s is ±1 (1 or -1), fractional_str_m is first frac_digits decimal digits (string)
    formatted_str is like +d.mmmmmm e+E
    """
    # Pack/unpack to ensure single precision representation
    packed = struct.pack(">f", single_float)
    val = struct.unpack(">f", packed)[0]
    if val == 0.0:
        return (1, 0, "0"*frac_digits, 0, f"+0.{ '0'*frac_digits }e+0")
    sign = -1 if struct.unpack('>I', struct.pack('>f', val))[0] >> 31 & 1 else 1
    sgn = "-" if sign < 0 else "+"
    d = Decimal(val)
    fmt = f"{val:.{frac_digits + 4}e}"
    mant, exp = fmt.split("e")
    exp10 = int(exp)
    if mant[0] in "+-":
        mant = mant[1:]
    if "." in mant:
        first_digit = int(mant[0])
        frac_part = mant.split(".")[1]
    else:
        first_digit = int(mant[0])
        frac_part = ""
    frac = (frac_part + "0"*frac_digits)[:frac_digits]
    formatted = f"{sgn}{first_digit}.{frac}e{exp10:+d}"
    return (1 if sign > 0 else -1, first_digit, frac, exp10, formatted)

# ---------------- Controlled random generators ----------------
def gen_1_1_bits():
    S = random.choice([0, 1])
    E = random.choice([125, 126, 127, 128])
    patterns = [
        0b11000000000000000000000,
        0b10000000000000000000000,
        0b01000000000000000000000,
        0b10100000000000000000000,
        0b01100000000000000000000,
        0b11100000000000000000000,
    ]
    F = random.choice(patterns)
    return S, E, F

def gen_simple_frac():
    choices = [
        0b10000000000000000000000,
        0b01000000000000000000000,
        0b00100000000000000000000,
        0b11000000000000000000000,
        0b10100000000000000000000,
        0b01100000000000000000000,
    ]
    return random.choice(choices)

def gen_mul_add_operands():
    s = random.choice([0, 1])
    E = random.choice([126, 127, 128, 129])
    F = gen_simple_frac()
    return s, E, F

# ---------------- Mental-friendly multiplication generator ----------------
def gen_mul_operands_easy():
    """
    Generate operands for multiplication that are simple to do by hand.
    - Significands: 1.0, 1.25, 1.5, 1.75 (easy fractions)
    - Exponents: 126, 127, 128 (small decimal exponents)
    """
    # Map simple decimal values to IEEE-754 F bits
    simple_F_map = {
        1.0: 0b00000000000000000000000,
        1.25: 0b01000000000000000000000,
        1.5: 0b10000000000000000000000,
        1.75: 0b11000000000000000000000
    }
    
    # Random choice of significand and exponent
    val = random.choice(list(simple_F_map.keys()))
    F = simple_F_map[val]
    s = random.choice([0,1])  # random sign
    E = random.choice([126,127,128])  # small exponent for easy math
    
    return s, E, F


# ---------------- GUI ----------------
LARGE_FONT = ("Arial", 14)
TITLE_FONT = ("Arial", 16, "bold")
SECTION_PADX = 12
SECTION_PADY = 12

class FloatQuizApp:
    def __init__(self, root):
        self.root = root
        root.title("IEEE-754 Floating Point Quiz — Light Academic Theme")
        root.geometry("1100x850")

        main = ttk.Frame(root)
        main.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(main, bg="white")
        scrollbar = ttk.Scrollbar(main, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.container = ttk.Frame(self.canvas)
        self.canvas.create_window((0,0), window=self.container, anchor="nw")
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.container.bind("<Configure>", self.update_scroll)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        title = ttk.Label(self.container, text="IEEE-754 Floating Point Quiz", font=TITLE_FONT, background="white")
        title.pack(pady=(16,8))

        subtitle = ttk.Label(self.container,
                             text="Randomized practice with controlled difficulty.\nUse 'New Quiz' for new numbers.",
                             font=LARGE_FONT, background="white")
        subtitle.pack(pady=(0,12))

        self.section1 = self._make_section(self.container, "1.1 Floating Point Representation")
        self.section2 = self._make_section(self.container, "1.2 Floating Point Multiplication")
        self.section3 = self._make_section(self.container, "1.3 Floating Point Addition")

        self.entries = []
        self.correct_answers = []

        self._build_section1()
        self._build_section2()
        self._build_section3()

        btn_frame = ttk.Frame(self.container)
        btn_frame.pack(fill="x", pady=(8, 20))
        ttk.Button(btn_frame, text="✅ Check Answers", command=self.check_answers).pack(side="left", padx=10, pady=6)
        ttk.Button(btn_frame, text="🔄 New Quiz", command=self.new_quiz).pack(side="left", padx=10, pady=6)
        ttk.Button(btn_frame, text="🛈 Show Correct Answers", command=self.show_answers).pack(side="left", padx=10, pady=6)


        self.result_label = ttk.Label(self.container, text="", font=("Arial", 14, "bold"), background="white")
        self.result_label.pack(pady=(6, 20))

        self.new_quiz()

    def _make_section(self, parent, title_text):
        frame = tk.Frame(parent, bd=2, relief="groove", background="white")
        frame.pack(fill="x", padx=SECTION_PADX, pady=(8, 8))
        lbl = tk.Label(frame, text=title_text, font=("Arial", 14, "bold"), background="white")
        lbl.pack(anchor="w", padx=10, pady=(10, 0))
        return frame

    def _build_section1(self):
        qtext = (
            "Translate the binary floating-point number to decimal scientific notation "
            "(normalized form ±n.nnn...10^e).\n"
            "N = (-1)^S * (1.F) * 2^(E-127)\n"
            "N = [s] * [d].[m] * 10^[e]\n"
            "s can be -1 or 1.\n"
        )
        tk.Label(self.section1, text=qtext, font=LARGE_FONT, justify="left", background="white").pack(anchor="w", padx=12, pady=(6, 6))
        self.s1_bits_label = tk.Label(self.section1, text="", font=LARGE_FONT, background="white")
        self.s1_bits_label.pack(anchor="w", padx=12)

        row = tk.Frame(self.section1, background="white")
        row.pack(anchor="w", padx=12, pady=(8,12))
        tk.Label(row, text="Enter: s =", font=LARGE_FONT, background="white").pack(side="left")
        e_s = ttk.Entry(row, width=6, font=LARGE_FONT)
        e_s.pack(side="left", padx=(6,16))
        tk.Label(row, text="d =", font=LARGE_FONT, background="white").pack(side="left")
        e_d = ttk.Entry(row, width=6, font=LARGE_FONT)
        e_d.pack(side="left", padx=(6,16))
        tk.Label(row, text="m (first 6 digits) =", font=LARGE_FONT, background="white").pack(side="left")
        e_m = ttk.Entry(row, width=12, font=LARGE_FONT)
        e_m.pack(side="left", padx=(6,16))
        tk.Label(row, text="e =", font=LARGE_FONT, background="white").pack(side="left")
        e_e = ttk.Entry(row, width=8, font=LARGE_FONT)
        e_e.pack(side="left", padx=(6,6))
        self.entries += [{'widget': e_s, 'corr': None},{'widget': e_d, 'corr': None},{'widget': e_m, 'corr': None},{'widget': e_e, 'corr': None}]
        self.s1_hint = tk.Label(self.section1, text="", font=("Arial", 12), fg="darkgreen", background="white")
        self.s1_hint.pack(anchor="w", padx=12, pady=(4,8))

    def _build_section2(self):
        qtext = (
            "Perform the floating operation R = A * B (IEEE-754 single precision).\n"
            "Give resulting S, E (8-bit), F (leftmost 6 bits).\n"
        )
        tk.Label(self.section2, text=qtext, font=LARGE_FONT, justify="left", background="white").pack(anchor="w", padx=12, pady=(6,6))
        self.s2_bits_label = tk.Label(self.section2, text="", font=LARGE_FONT, background="white")
        self.s2_bits_label.pack(anchor="w", padx=12)
        row = tk.Frame(self.section2, background="white")
        row.pack(anchor="w", padx=12, pady=(8,12))
        tk.Label(row, text="R: S =", font=LARGE_FONT, background="white").pack(side="left")
        e_S = ttk.Entry(row, width=6, font=LARGE_FONT)
        e_S.pack(side="left", padx=(6,16))
        tk.Label(row, text="E (8-bit) =", font=LARGE_FONT, background="white").pack(side="left")
        e_E = ttk.Entry(row, width=12, font=LARGE_FONT)
        e_E.pack(side="left", padx=(6,16))
        tk.Label(row, text="F (left 6 bits) =", font=LARGE_FONT, background="white").pack(side="left")
        e_F = ttk.Entry(row, width=10, font=LARGE_FONT)
        e_F.pack(side="left", padx=(6,6))
        self.entries += [{'widget': e_S, 'corr': None},{'widget': e_E, 'corr': None},{'widget': e_F, 'corr': None}]
        self.s2_hint = tk.Label(self.section2, text="", font=("Arial", 12), fg="darkgreen", background="white")
        self.s2_hint.pack(anchor="w", padx=12, pady=(4,8))

    def _build_section3(self):
        qtext = (
            "Perform the floating operation R = A + B (IEEE-754 single precision).\n"
            "Give resulting S, E (8-bit), F (leftmost 6 bits).\n"
        )
        tk.Label(self.section3, text=qtext, font=LARGE_FONT, justify="left", background="white").pack(anchor="w", padx=12, pady=(6,6))
        self.s3_bits_label = tk.Label(self.section3, text="", font=LARGE_FONT, background="white")
        self.s3_bits_label.pack(anchor="w", padx=12)
        row = tk.Frame(self.section3, background="white")
        row.pack(anchor="w", padx=12, pady=(8,12))
        tk.Label(row, text="R: S =", font=LARGE_FONT, background="white").pack(side="left")
        e_S = ttk.Entry(row, width=6, font=LARGE_FONT)
        e_S.pack(side="left", padx=(6,16))
        tk.Label(row, text="E (8-bit) =", font=LARGE_FONT, background="white").pack(side="left")
        e_E = ttk.Entry(row, width=12, font=LARGE_FONT)
        e_E.pack(side="left", padx=(6,16))
        tk.Label(row, text="F (left 6 bits) =", font=LARGE_FONT, background="white").pack(side="left")
        e_F = ttk.Entry(row, width=10, font=LARGE_FONT)
        e_F.pack(side="left", padx=(6,6))
        self.entries += [{'widget': e_S, 'corr': None},{'widget': e_E, 'corr': None},{'widget': e_F, 'corr': None}]
        self.s3_hint = tk.Label(self.section3, text="", font=("Arial", 12), fg="darkgreen", background="white")
        self.s3_hint.pack(anchor="w", padx=12, pady=(4,8))

    def show_answers(self):
        # Section 1
        s1_text = f"s = {self.entries[0]['corr']}, d = {self.entries[1]['corr']}, m = {self.entries[2]['corr']}, e = {self.entries[3]['corr']}"
        self.s1_hint.config(text=f"Correct: {s1_text}")

        # Section 2
        s2_text = f"S = {self.entries[4]['corr']}, E = {self.entries[5]['corr']}, F (left 6 bits) = {self.entries[6]['corr']}"
        self.s2_hint.config(text=f"Correct: {s2_text}")

        # Section 3
        s3_text = f"S = {self.entries[7]['corr']}, E = {self.entries[8]['corr']}, F (left 6 bits) = {self.entries[9]['corr']}"
        self.s3_hint.config(text=f"Correct: {s3_text}")

        # Also color all entries green for clarity
        for e in self.entries:
            e['widget'].config(foreground='green')


    # ---------- behavior ----------
    def update_scroll(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def new_quiz(self):
        self.result_label.config(text="")
        self.s1_hint.config(text="")
        self.s2_hint.config(text="")
        self.s3_hint.config(text="")

        for e in self.entries:
            e['widget'].delete(0, 'end')
            e['widget'].config(foreground='black')

        # 1.1
        S1, E1, F1 = gen_1_1_bits()
        val1 = make_float_from_bits(S1, E1, F1)
        s_sign, d_first, m_frac, e10, formatted = decimal_scientific_components(val1, 6)
        self.s1_bits_label.config(text=f"Given bits: S={S1}, E={E1} (dec), F={F1 >> 17:06b}...0")
        idx = 0
        self.entries[idx]['corr'] = str(s_sign)
        self.entries[idx+1]['corr'] = str(d_first)
        self.entries[idx+2]['corr'] = str(m_frac)
        self.entries[idx+3]['corr'] = str(e10)
        self.s1_hint.config(text=f"(Example correct formatting) {formatted}")

        # 1.2 multiply
        sA, EA, FA = gen_mul_operands_easy()
        sB, EB, FB = gen_mul_operands_easy()
        A = make_float_from_bits(sA, EA, FA)
        B = make_float_from_bits(sB, EB, FB)
        R = struct.unpack(">f", struct.pack(">f", A * B))[0]
        sR, ER, FR = float_to_bits(R)
        self.s2_bits_label.config(
        text=f"A: S={sA} E={EA} F={FA >> 17:06b}...0\n"
             f"B: S={sB} E={EB} F={FB >> 17:06b}...0")
        idx = 4
        self.entries[idx]['corr'] = str(sR)
        self.entries[idx+1]['corr'] = str(ER)
        self.entries[idx+2]['corr'] = leftmost_F_bits(FR,6)
        self.s2_hint.config(text=f"(Correct numeric R ≈ {R!r})")

        # 1.3 addition
        sA2, EA2, FA2 = gen_mul_add_operands()
        sB2, EB2, FB2 = gen_mul_add_operands()
        EA2 = random.choice([127,128,129])
        EB2 = max(2, min(253, EA2 + random.choice([-1,0,1])))
        A2 = make_float_from_bits(sA2, EA2, FA2)
        B2 = make_float_from_bits(sB2, EB2, FB2)
        R2 = struct.unpack(">f", struct.pack(">f", A2 + B2))[0]
        sR2, ER2, FR2 = float_to_bits(R2)
        self.s3_bits_label.config(
        text=f"A: S={sA2} E={EA2} F={FA2 >> 17:06b}...0\n"
             f"B: S={sB2} E={EB2} F={FB2 >> 17:06b}...0")
        idx = 7
        self.entries[idx]['corr'] = str(sR2)
        self.entries[idx+1]['corr'] = str(ER2)
        self.entries[idx+2]['corr'] = leftmost_F_bits(FR2,6)
        self.s3_hint.config(text=f"(Correct numeric R ≈ {R2!r})")

    def check_answers(self):
        total = len(self.entries)
        correct = 0
        for e in self.entries:
            user = e['widget'].get().strip()
            corr = str(e['corr']).strip()
            if user == corr:
                e['widget'].config(foreground='green')
                correct += 1
            else:
                e['widget'].config(foreground='red')
        self.result_label.config(text=f"Score: {correct}/{total} ({correct/total*100:.1f}%)")

if __name__ == "__main__":
    root = tk.Tk()
    app = FloatQuizApp(root)
    root.mainloop()
