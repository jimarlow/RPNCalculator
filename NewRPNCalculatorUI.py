import customtkinter as ctk

from RPNCalculator import RPNCalculator


class NewRPNCalculatorUI:
    KEYPAD_COLORS = {
        "number": {
            "fg_color": ("#E7EEF6", "#354354"),
            "hover_color": ("#D7E3F0", "#43556B"),
            "text_color": ("#26384B", "#F4F7FA"),
        },
        "operator": {
            "fg_color": ("#DCEBFA", "#284C73"),
            "hover_color": ("#CADFF5", "#35628F"),
            "text_color": ("#183C63", "#F4F8FC"),
        },
        "trigonometry": {
            "fg_color": ("#EAE3F7", "#4A3D68"),
            "hover_color": ("#DED3F1", "#5A4A7E"),
            "text_color": ("#423160", "#F8F5FC"),
        },
        "function": {
            "fg_color": ("#DFF1EA", "#28564B"),
            "hover_color": ("#CDE7DD", "#367364"),
            "text_color": ("#235246", "#F2FBF7"),
        },
        "stack": {
            "fg_color": ("#F6EBD5", "#604E2E"),
            "hover_color": ("#F0DDB8", "#745F37"),
            "text_color": ("#5B4727", "#FFF8E9"),
        },
        "variable": {
            "fg_color": ("#F4E3ED", "#614257"),
            "hover_color": ("#EBD2E1", "#755168"),
            "text_color": ("#5D3850", "#FFF5FA"),
        },
        "clear": {
            "fg_color": ("#F8E1DD", "#663B37"),
            "hover_color": ("#EFD0CB", "#7D4A45"),
            "text_color": ("#6B2F29", "#FFF4F2"),
        },
        "enter": {
            "fg_color": ("#DBEFE1", "#31583D"),
            "hover_color": ("#C5E4CE", "#3E704D"),
            "text_color": ("#255331", "#F2FFF4"),
        },
    }

    KEYPAD_GROUPS = (
        (
            "Numbers",
            (
                "7", "8", "9", "pi", "4", "5", "6", "e",
                "1", "2", "3", ".", "0", "Space",
            ),
            4,
            0,
            0,
            2,
        ),
        ("Operators", ("+", "-", "*", "/", "%", "**"), 2, 0, 2, 1),
        ("Stack / Input", ("swap", "cls", "Enter"), 1, 0, 3, 1),
        ("Create variable", ("=",), 1, 0, 4, 1),
        (
            "Trigonometry",
            ("sin", "cos", "tan", "asin", "acos", "atan", "atan2", "deg", "rad"),
            3,
            1,
            0,
            2,
        ),
        (
            "Math Functions",
            (
                "sum", "neg", "int", "ceil", "floor", "round", "fabs",
                "factorial", "sqrt", "hypot", "logN", "percent", "roundN",
                "log2", "log10",
            ),
            5,
            1,
            2,
            3,
        ),
    )

    def __init__(self):
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("RPN Calculator")
        self.root.geometry("1000x850")
        self.root.minsize(720, 600)
        self.calculator = RPNCalculator()
        self._recalculation_after_id = None

        self.root.grid_columnconfigure(0, weight=2, minsize=220)
        self.root.grid_columnconfigure(1, weight=2, minsize=220)
        self.root.grid_columnconfigure(2, weight=1, minsize=180)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=0)
        self.root.grid_rowconfigure(2, weight=0)

        self.input_text = self._create_text_pane("Input", 0)
        self.stack_text = self._create_text_pane("Stack", 1, readonly=True)
        self.variables_text = self._create_text_pane("Variables", 2, readonly=True)

        self._create_keypad()

        controls = ctk.CTkFrame(self.root, fg_color="transparent")
        controls.grid(
            row=2, column=0, columnspan=3, sticky="e", padx=8, pady=(0, 8)
        )
        ctk.CTkButton(
            controls,
            text="Clear Line",
            width=100,
            command=self._clear_current_line,
        ).grid(row=0, column=0, padx=(0, 8))
        ctk.CTkButton(
            controls,
            text="Reset All",
            width=100,
            command=self._reset_calculator,
        ).grid(row=0, column=1)

        self.input_text.bind("<<Modified>>", self._on_input_modified)
        self.input_text.bind("<Button-1>", self._focus_input, add="+")
        self.input_text.bind("<KeyPress>", self._handle_input_key, add="+")
        self.input_text.edit_modified(False)
        self.root.after(100, self._focus_input)

    def _create_keypad(self):
        keypad = ctk.CTkFrame(self.root, corner_radius=10, border_width=1)
        keypad.grid(
            row=1, column=0, columnspan=3, sticky="ew", padx=8, pady=(0, 8)
        )
        for column in range(5):
            keypad.grid_columnconfigure(column, weight=1, uniform="keypad")

        for title, keys, columns, row, column, columnspan in self.KEYPAD_GROUPS:
            group = ctk.CTkFrame(
                keypad,
                width=1,
                height=1,
                corner_radius=8,
                border_width=1,
                fg_color=("#F4F6F9", "#2A3038"),
                border_color=("#D7DDE5", "#3B434E"),
            )
            group.grid(
                row=row,
                column=column,
                columnspan=columnspan,
                sticky="nsew",
                padx=4,
                pady=4,
            )
            for group_column in range(columns):
                group.grid_columnconfigure(
                    group_column, weight=1, uniform=f"{title}-buttons"
                )

            heading = ctk.CTkLabel(
                group,
                text=title,
                font=ctk.CTkFont(size=12, weight="bold"),
                anchor="w",
            )
            heading.grid(
                row=0, column=0, columnspan=columns, sticky="ew",
                padx=8, pady=(6, 2),
            )

            for index, key in enumerate(keys):
                if key.isdigit() or key in {".", "pi", "e", "Space"}:
                    color_group = "number"
                elif key in {"+", "-", "*", "/", "**", "%"}:
                    color_group = "operator"
                elif key in {
                    "sin", "cos", "tan", "asin", "acos", "atan", "atan2",
                    "deg", "rad",
                }:
                    color_group = "trigonometry"
                elif key == "swap":
                    color_group = "stack"
                elif key == "cls":
                    color_group = "clear"
                elif key == "Enter":
                    color_group = "enter"
                elif key == "=":
                    color_group = "variable"
                else:
                    color_group = "function"
                colors = self.KEYPAD_COLORS[color_group]
                button = ctk.CTkButton(
                    group,
                    text=key,
                    height=32,
                    fg_color=colors["fg_color"],
                    hover_color=colors["hover_color"],
                    text_color=colors["text_color"],
                    font=ctk.CTkFont(size=14, weight="bold"),
                    command=lambda value=key: self._insert_key(value),
                )
                button_row = index // columns + 1
                button_column = index % columns
                button.grid(
                    row=button_row,
                    column=button_column,
                    columnspan=columns - button_column if key == "Space" else 1,
                    sticky="ew",
                    padx=3,
                    pady=3,
                )

    def _insert_key(self, key):
        self.input_text.focus_set()
        if key == "Enter":
            value = "\n"
        elif key == "Space":
            value = " "
        elif key.isdigit() or key == ".":
            value = key
        else:
            value = f" {key} "
        self.input_text.insert("insert", value)
        self.input_text.see("insert")

    def _create_text_pane(self, title, column, readonly=False):
        pane = ctk.CTkFrame(self.root, corner_radius=10, border_width=1)
        pane.grid(row=0, column=column, sticky="nsew", padx=8, pady=8)
        pane.grid_columnconfigure(0, weight=1)
        pane.grid_rowconfigure(1, weight=1)

        heading = ctk.CTkLabel(
            pane,
            text=title,
            font=ctk.CTkFont(size=17, weight="bold"),
            anchor="w",
        )
        heading.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 6))

        text = ctk.CTkTextbox(
            pane,
            width=250,
            height=200,
            wrap="none",
            font=ctk.CTkFont(family="Menlo", size=14),
            state="disabled" if readonly else "normal",
            takefocus=not readonly,
            undo=not readonly,
        )
        text.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        return text

    def _focus_input(self, event=None):
        self.input_text.focus_set()

    def _handle_input_key(self, event):
        keysym = getattr(event, "keysym", "")
        if keysym in ("Return", "KP_Enter") or event.char in ("\r", "\n"):
            self.input_text.insert("insert", "\n")
            self.input_text.see("insert")
            return "break"

        if keysym in ("BackSpace", "Backspace", "Delete"):
            selection = self.input_text.tag_ranges("sel")
            if selection:
                self.input_text.delete("sel.first", "sel.last")
            elif keysym == "Delete":
                self.input_text.delete("insert", "insert+1c")
            else:
                self.input_text.delete("insert-1c", "insert")
            return "break"

        operator = event.char
        if operator not in "+-*/%=":
            return None

        selection = self.input_text.tag_ranges("sel")
        if selection:
            self.input_text.delete("sel.first", "sel.last")

        line_prefix = self.input_text.get("insert linestart", "insert")
        if operator in "+-" and not line_prefix.strip():
            self.input_text.insert("insert", operator)
            return "break"

        if operator == "*" and line_prefix.endswith("* "):
            self.input_text.delete("insert-1c", "insert")
            self.input_text.insert("insert", "* ")
            return "break"

        prefix = " " if line_prefix and not line_prefix[-1].isspace() else ""
        self.input_text.insert("insert", f"{prefix}{operator} ")
        return "break"

    def _on_input_modified(self, event=None):
        if self.input_text.edit_modified():
            self.input_text.edit_modified(False)
            self._schedule_recalculation()

    def _schedule_recalculation(self):
        self._cancel_pending_recalculation()
        self._recalculation_after_id = self.root.after(
            200, self._run_scheduled_recalculation
        )

    def _run_scheduled_recalculation(self):
        self._recalculation_after_id = None
        self._recalculate()

    def _cancel_pending_recalculation(self):
        if self._recalculation_after_id is not None:
            self.root.after_cancel(self._recalculation_after_id)
            self._recalculation_after_id = None

    def _clear_current_line(self):
        line = self.input_text.index("insert").split(".", maxsplit=1)[0]
        self.input_text.delete(f"{line}.0", f"{line}.end")
        self.input_text.focus_set()

    def _reset_calculator(self):
        self._cancel_pending_recalculation()
        self.input_text.delete("1.0", "end")
        self.input_text.edit_modified(False)
        self.calculator.cls("")
        self._set_text(self.stack_text, "")
        self._set_text(self.variables_text, "")
        self.input_text.focus_set()

    def _recalculate(self):
        self.calculator.cls("")
        errors = []

        for line_number, line in enumerate(
            self.input_text.get("1.0", "end-1c").splitlines(), start=1
        ):
            expression = line.strip()
            if not expression:
                continue
            try:
                self.calculator(expression)
            except (ArithmeticError, IndexError, TypeError, ValueError) as error:
                errors.append(f"Line {line_number}: {error}")

        stack_lines = [
            f"TOP -> {value}" if index == 0 else f"       {value}"
            for index, value in enumerate(reversed(self.calculator.stack))
        ]
        if errors:
            if stack_lines:
                stack_lines.append("")
            stack_lines.append("Errors:")
            stack_lines.extend(errors)
        variables = [
            f"{name} is {value}"
            for name, value in sorted(self.calculator.variables.items())
        ]
        self._set_text(self.stack_text, "\n".join(stack_lines))
        self._set_text(self.variables_text, "\n".join(variables))

    @staticmethod
    def _set_text(widget, value):
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", value)
        widget.configure(state="disabled")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    NewRPNCalculatorUI().run()
