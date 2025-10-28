import tkinter as tk
from tkinter import ttk
import random

# --- Frågor och svar ---
questions = [
    {
        "question": "1. Assume we move the Branch logic component from the DE stage to the ALU stage "
                    "(across the synchronization border between DE and ALU). "
                    "How would this affect the branching behavior?",
        "options": [
            "One less branch delay slot (total of 0)",
            "One additional branch delay slot (total of 2)",
            "None of the alternatives.",
            "Not at all"
        ],
        "answer": 1
    },
    {
        "question": "2. In order to shorten the pipeline (removing the DM stage), we move the DataMemory component "
                    "from the DM stage to the ALU stage after ALU. "
                    "How would this affect the critical path?",
        "options": [
            "Not at all",
            "The critical path would now consider the addition of the ALU and DataMemory component.",
            "None of the alternatives.",
            "The critical path would now consider only the minimum of the ALU and DataMemory component."
        ],
        "answer": 1
    },
    {
        "question": "3. In order to simplify the pipeline, we remove all forwarding logic.\n"
                    "How would this affect read-after-write hazards for R-type instructions (like add t0, t1, t2)?\n"
                    "How many delay slots between dependent R-type instructions would be needed?",
        "options": [
            "None of the alternatives",
            "One delay slot needed",
            "Two delay slots needed",
            "No delay slots needed"
        ],
        "answer": 2
    },
    {
        "question": "5.1 In a real MIPS, what is the effect of executing the 'rfe' instruction if you are running in 'user' mode?",
        "options": [
            "None of the alternatives is correct",
            "Nothing, the program is not affected.",
            "The PC is restored to the user PC",
            "The mode stack is pop:ed",
            "An exception is raised, indicating a privilege violation."
        ],
        "answer": 4
    },
    {
        "question": "5.2 What is the effect of an interrupt arriving if the global interrupt bit is disabled?",
        "options": [
            "The kernel is entered (and the kernel code needs to check if the interrupt should be taken or ignored).",
            "None of the alternatives is correct.",
            "The CPU immediately returns to user mode.",
            "Nothing, the program execution is not affected.",
            "An exception is raised, indicating an illegal interrupt."
        ],
        "answer": 3
    },
    {
        "question": "5.3 When an exception occurs...",
        "options": [
            "The kernel is entered only if global interrupts are enabled.",
            "None of the alternatives is correct.",
            "The kernel is always entered.",
            "The CPU immediately returns to user mode.",
            "The kernel is not entered if global interrupt flag is enabled."
        ],
        "answer": 2
    },
    {
        "question": "5.4 A MIPS TLB lookup miss indicates...",
        "options": [
            "That an arithmetic error has occurred.",
            "That a page fault has occurred.",
            "That the TLB does not have a mapping for the virtual address.",
            "That the TLB has a mapping for the virtual address.",
            "None of the alternatives is correct."
        ],
        "answer": 2
    },
    {
        "question": "5.5 Which statement regarding 'syscall' is correct?",
        "options": [
            "None of the alternatives is correct.",
            "The kernel is entered only if global interrupts are enabled.",
            "All registers are pushed before the kernel is entered.",
            "The global pointer is pushed before the kernel is entered.",
            "The mode-stack is pushed and the kernel is entered."
        ],
        "answer": 4
    },
    {
        "question": "5.6 According to the MIPS ABI (used in the course) the frame pointer register refers (points) to...",
        "options": [
            "The address of the 'old' frame pointer stored on the heap.",
            "The address of the 'old' global pointer stored on the stack.",
            "The address of the 'old' stack pointer stored on the stack.",
            "The address of the 'old' stack pointer stored on the heap.",
            "None of the alternatives is correct."
        ],
        "answer": 4
    },
    {
        "question": "5.7 When switching from context A to context B, the kernel needs to:",
        "options": [
            "Store context A and restore context B.",
            "None of the alternatives is correct.",
            "Only store context A.",
            "Only restore context B.",
            "Store context B and restore context A."
        ],
        "answer": 0
    },
    {
        "question": "5.8 What is the purpose of a write buffer (to next level in the memory hierarchy)?",
        "options": [
            "Reduce hit rate.",
            "Reduce latency on writes (to next level in the memory hierarchy).",
            "Increase latency on writes (to next level in the memory hierarchy).",
            "None of the alternatives is correct.",
            "Improve hit rate."
        ],
        "answer": 1
    },
    {
        "question": "5.9 Increasing the set size while keeping the same total amount of cache data memory will...",
        "options": [
            "Increase the 'capacity' of the cache.",
            "Never lead to better hit ratio.",
            "Reduce the 'capacity' of the cache.",
            "Always lead to better hit ratio.",
            "None of the alternatives is correct."
        ],
        "answer": 4
    },
    {
        "question": "5.10 A common property of code with loops or recursion is...",
        "options": [
            "Low spatial data locality.",
            "Low temporal instruction locality.",
            "High spatial data locality.",
            "None of the alternatives is correct.",
            "High temporal instruction locality."
        ],
        "answer": 4
    }
]

# Shuffle options while keeping correct answer index
for q in questions:
    correct = q["options"][q["answer"]]
    opts = [(opt, opt == correct) for opt in q["options"]]
    random.shuffle(opts)
    q["options"] = [o for o, _ in opts]
    q["answer"] = [i for i, (_, c) in enumerate(opts) if c][0]

# --- GUI ---
root = tk.Tk()
root.title("MIPS Quiz")
root.geometry("1000x800")

main_frame = ttk.Frame(root)
main_frame.pack(fill="both", expand=True)

canvas = tk.Canvas(main_frame)
scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
scrollable_frame = ttk.Frame(canvas)

scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# ✅ Enable scrollwheel support
def _on_mouse_wheel(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

canvas.bind_all("<MouseWheel>", _on_mouse_wheel)

selected_answers = []
result_labels = []

for i, q in enumerate(questions):
    ttk.Label(scrollable_frame, text=q["question"], font=("Arial", 12, "bold"),
              wraplength=900, justify="left").pack(anchor="w", pady=(10, 0))
    var = tk.IntVar(value=-1)
    selected_answers.append(var)
    for j, opt in enumerate(q["options"]):
        ttk.Radiobutton(scrollable_frame, text=opt, variable=var,
                        value=j).pack(anchor="w", padx=20)
    result_label = ttk.Label(scrollable_frame, text="")
    result_label.pack(anchor="w")
    result_labels.append(result_label)

# ✅ Score display with format "(X/Y)"
def check_answers():
    score = 0
    for i, q in enumerate(questions):
        selected = selected_answers[i].get()
        correct = q["answer"]
        if selected == correct:
            result_labels[i].config(text="✅ Correct!", foreground="green")
            score += 1
        else:
            result_labels[i].config(
                text=f"❌ Wrong (Correct: {q['options'][correct]})",
                foreground="red"
            )
    result_label_total.config(text=f"Score: {score}/{len(questions)} ✅", font=("Arial", 16, "bold"))

ttk.Button(scrollable_frame, text="Rätta", command=check_answers).pack(pady=10)
result_label_total = ttk.Label(scrollable_frame, text="", font=("Arial", 14))
result_label_total.pack(pady=10)

root.mainloop()
