"""Digital Calculator built with Tkinter.

Run:  python calculator.py
Supports mouse clicks and keyboard input (digits, + - * /, Enter, Backspace, Esc).
"""

import ast
import operator
import tkinter as tk

# ---------- Safe expression evaluator (avoids using eval on raw input) ----------
OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
UNARY = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def _eval(node):
    if isinstance(node, ast.Expression):
        return _eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in OPS:
        return OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in UNARY:
        return UNARY[type(node.op)](_eval(node.operand))
    raise ValueError("Invalid expression")


def calculate(expression: str):
    """Evaluate a math expression string and return a number."""
    expr = expression.replace("×", "*").replace("÷", "/").replace("−", "-")
    return _eval(ast.parse(expr, mode="eval"))


def format_result(value) -> str:
    """Trim trailing zeros and avoid float noise (e.g. 0.1+0.2)."""
    if isinstance(value, float):
        value = round(value, 10)
        if value == int(value) and abs(value) < 1e15:
            return str(int(value))
        return f"{value:.10g}"
    return str(value)


# ---------- GUI ----------
class Calculator(tk.Tk):
    BG = "#1e1e2e"
    DISPLAY_BG = "#11111b"
    NUM = "#313244"
    OP = "#fab387"
    FUNC = "#585b70"
    EQ = "#a6e3a1"

    def __init__(self):
        super().__init__()
        self.title("Calculator")
        self.configure(bg=self.BG)
        self.resizable(False, False)

        self.expression = ""
        self.just_evaluated = False

        # Expression (small) + main display (large)
        self.history_var = tk.StringVar()
        self.display_var = tk.StringVar(value="0")

        tk.Label(self, textvariable=self.history_var, anchor="e", bg=self.DISPLAY_BG,
                 fg="#9399b2", font=("Segoe UI", 12), padx=12, pady=6
                 ).grid(row=0, column=0, columnspan=4, sticky="nsew")
        tk.Label(self, textvariable=self.display_var, anchor="e", bg=self.DISPLAY_BG,
                 fg="white", font=("Segoe UI", 32, "bold"), padx=12, pady=8
                 ).grid(row=1, column=0, columnspan=4, sticky="nsew")

        buttons = [
            ("C", "func"), ("⌫", "func"), ("%", "func"), ("÷", "op"),
            ("7", "num"), ("8", "num"), ("9", "num"), ("×", "op"),
            ("4", "num"), ("5", "num"), ("6", "num"), ("−", "op"),
            ("1", "num"), ("2", "num"), ("3", "num"), ("+", "op"),
            ("±", "func"), ("0", "num"), (".", "num"), ("=", "eq"),
        ]
        colors = {"num": self.NUM, "op": self.OP, "func": self.FUNC, "eq": self.EQ}

        for i, (label, kind) in enumerate(buttons):
            r, c = divmod(i, 4)
            fg = "black" if kind in ("op", "eq") else "white"
            tk.Button(self, text=label, font=("Segoe UI", 18), bg=colors[kind], fg=fg,
                      activebackground="#cdd6f4", bd=0, width=4, height=2,
                      command=lambda t=label: self.on_press(t)
                      ).grid(row=r + 2, column=c, padx=2, pady=2, sticky="nsew")

        # Keyboard bindings
        self.bind("<Key>", self.on_key)
        self.bind("<Return>", lambda e: self.on_press("="))
        self.bind("<BackSpace>", lambda e: self.on_press("⌫"))
        self.bind("<Escape>", lambda e: self.on_press("C"))

    # --- input handling ---
    def on_key(self, event):
        ch = event.char
        mapping = {"*": "×", "/": "÷", "-": "−"}
        if ch in "0123456789.+%":
            self.on_press(ch)
        elif ch in mapping:
            self.on_press(mapping[ch])

    def on_press(self, key):
        if key == "C":
            self.expression = ""
            self.history_var.set("")
            self.display_var.set("0")
            self.just_evaluated = False
        elif key == "⌫":
            self.expression = self.expression[:-1]
            self.display_var.set(self.expression or "0")
        elif key == "=":
            self.evaluate()
        elif key == "±":
            self.toggle_sign()
        elif key == "%":
            self.apply_percent()
        else:
            # After "=", typing a digit starts fresh; typing an operator continues.
            if self.just_evaluated and key not in "+−×÷":
                self.expression = ""
            self.just_evaluated = False
            self.expression += key
            self.display_var.set(self.expression)

    def evaluate(self):
        if not self.expression:
            return
        try:
            result = format_result(calculate(self.expression))
            self.history_var.set(self.expression + " =")
            self.expression = result
            self.display_var.set(result)
            self.just_evaluated = True
        except ZeroDivisionError:
            self.show_error("Cannot divide by 0")
        except Exception:
            self.show_error("Error")

    def toggle_sign(self):
        if not self.expression:
            return
        try:
            value = calculate(self.expression)
            self.expression = format_result(-value)
            self.display_var.set(self.expression)
        except Exception:
            self.show_error("Error")

    def apply_percent(self):
        if not self.expression:
            return
        try:
            value = calculate(self.expression) / 100
            self.expression = format_result(value)
            self.display_var.set(self.expression)
        except Exception:
            self.show_error("Error")

    def show_error(self, message):
        self.expression = ""
        self.history_var.set("")
        self.display_var.set(message)
        self.just_evaluated = False


if __name__ == "__main__":
    Calculator().mainloop()