import tkinter as tk
from tkinter import ttk
import struct
import random
from decimal import Decimal, getcontext

getcontext().prec = 40  # precision for decimal conversion

# Track entries and correct values
entries = []
correct = []


# ===== IEEE Utility Functions =====
def bits_to_float32(s, E, F):
    word = (s & 1) << 31 | (E & 0xFF) << 23 | (F & 0x7FFFFF)
    b = struct.pack('>I', word)
    return struct.unpack('>f', b)[0]


def float32_to_bits(value):
    b = struct.pack('>f', value)
    w = struct.unpack('>I', b)[0]
    s = (w >> 31) & 1
    E = (w >> 23) & 0xFF
    F = w & 0x7FFFFF
    return s, E, F


def leftmost_bits(F, n=6):
    return f"{(F >> (23 - n)) & ((1 << n) - 1):0{n}b}"


def decimal_scientific(val):
    if val == 0:
        return 1, 0, "0", 0
    decimal_str = f"{val:.12e}"
    sign_char = "-" if decimal_str.startswith("-") else "+"
    sign = -1 if sign_char == "-" else 1
    mantissa, exp = decimal_str.replace(sign_char, "").split("e")
    first = int(mantissa[0])
    frac = mantissa[2:]  # digits after decimal point
    exp10 = int(exp)
    return sign, first, frac, exp10


def rand_exp():
    return random.randint(2, 253)


def rand_frac():
    return random.getrandbits(23)


def rand_sign():
    return random.randint(0, 1)


# ===== GUI helper =====
def add_entry(answer, width=6):
    e = ttk.Entry(text, width=width)
    entries.append(e)
    correct.append(str(answer))
    text.window_create("insert", window=e)
    text.insert("insert", " ")


# ===== Generate Quiz =====
def make_quiz():
    entries.clear()
    correct.clear()
    text.delete("1.0", "end")

    text.insert("end", "IEEE-754 Float Quiz\n\n")
    text.insert("end", "Answer format: match sign, exponent, mantissa fields.\n\n")

    # ---- Problem 1 ----
    s = rand_sign()
    E = rand_exp()
    F = rand_frac()
    val = bits_to_float32(s, E, F)
    s2, d, m, e10 = decimal_scientific(val)

    text.insert("end", "1. Convert IEEE-754 to Decimal Scientific:\n")
    text.insert("end", f"S={s}, E={E:08b}, F={F:023b}\n")

    text.insert("end", "Enter: s = ")
    add_entry(s2)
    text.insert("end", ", d = ")
    add_entry(d)
    text.insert("end", ", m(first 6 digits) = ")
    add_entry(m[:6])
    text.insert("end", ", e = ")
    add_entry(e10)
    text.insert("end", "\n\n")

    # ---- Problem 2 Multiply ----
    sA, EA, FA = rand_sign(), rand_exp(), rand_frac()
    sB, EB, FB = rand_sign(), rand_exp(), rand_frac()
    A = bits_to_float32(sA, EA, FA)
    B = bits_to_float32(sB, EB, FB)
    R = struct.unpack('>f', struct.pack('>f', A * B))[0]
    sR, ER, FR = float32_to_bits(R)

    text.insert("end", "2. Multiply (A*B):\n")
    text.insert("end", f"A: S={sA} E={EA:08b} F={FA:023b}\n")
    text.insert("end", f"B: S={sB} E={EB:08b} F={FB:023b}\n")

    text.insert("end", "R: S = ")
    add_entry(sR)
    text.insert("end", ", E(8-bit) = ")
    add_entry(f"{ER:08b}")
    text.insert("end", ", F(left 6 bits) = ")
    add_entry(leftmost_bits(FR, 6))
    text.insert("end", "\n\n")

    # ---- Problem 3 Add ----
    EA2 = rand_exp()
    EB2 = max(2, min(253, EA2 + random.choice([-1, 0, 1])))
    sA2, FA2 = rand_sign(), rand_frac()
    sB2, FB2 = rand_sign(), rand_frac()
    A2 = bits_to_float32(sA2, EA2, FA2)
    B2 = bits_to_float32(sB2, EB2, FB2)
    R2 = struct.unpack('>f', struct.pack('>f', A2 + B2))[0]
    sR2, ER2, FR2 = float32_to_bits(R2)

    text.insert("end", "3. Add (A+B):\n")
    text.insert("end", f"A: S={sA2} E={EA2:08b} F={FA2:023b}\n")
    text.insert("end", f"B: S={sB2} E={EB2:08b} F={FB2:023b}\n")

    text.insert("end", "R: S = ")
    add_entry(sR2)
    text.insert("end", ", E(8-bit) = ")
    add_entry(f"{ER2:08b}")
    text.insert("end", ", F(left 6 bits) = ")
    add_entry(leftmost_bits(FR2, 6))
    text.insert("end", "\n\n")

    result_label.config(text="")


# ===== Grading =====
def check_answers():
    score = 0
    for entry, corr in zip(entries, correct):
        if entry.get().strip() == str(corr):
            entry.config(foreground="green")
            score += 1
        else:
            entry.config(foreground="red")
    result_label.config(text=f"Score: {score}/{len(entries)}")


# ===== UI Layout =====
root = tk.Tk()
root.title("IEEE-754 Floating Point Quiz")
root.geometry("1100x850")

main = ttk.Frame(root)
main.pack(fill="both", expand=True)

canvas = tk.Canvas(main)
scrollbar = ttk.Scrollbar(main, orient="vertical", command=canvas.yview)
frame = ttk.Frame(canvas)
canvas.create_window((0, 0), window=frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

text = tk.Text(frame, wrap="word", font=("Arial", 12), width=130)
text.pack(fill="both", expand=True, padx=10, pady=10)

btn_frame = ttk.Frame(frame)
btn_frame.pack(pady=10)

ttk.Button(btn_frame, text="✅ Check Answers", command=check_answers).pack(side="left", padx=10)
ttk.Button(btn_frame, text="🔄 New Quiz", command=make_quiz).pack(side="left", padx=10)

result_label = ttk.Label(frame, font=("Arial", 14, "bold"))
result_label.pack(pady=10)

def update_scroll(event=None):
    canvas.configure(scrollregion=canvas.bbox("all"))

frame.bind("<Configure>", update_scroll)

make_quiz()
root.mainloop()
