from tkinter import *
from tkinter import Frame as TkFrame
from tkinter.ttk import *
from tkinter.filedialog import askopenfilename
from RPNCalculator import *


class RPNCalculatorApp(TkFrame):
    def __init__(self):
        """Initialize the application with an RPNCalculator object and a UI."""
        self.calc = RPNCalculator()
        self.root = Tk()
        TkFrame.__init__(self, self.root)
        self.root.bind('<Key>', self.onKey)
        self.pack(fill=BOTH, expand=True)
        self.master.title('RPN Calculator from www.clearviewtraining.com')
        self.initUI()
        self.root.geometry("1000x800")
        self.root.after_idle(self.inputText.focus_set)
        self.root.after(1000, self.reportLayout)

    def reportLayout(self):
        widgets = (self, self.inputPane, self.inputText, self.stackPane, self.stackText,
                   self.variablesPane, self.variablesText)
        print("Tk layout:", self.root.state(),
              [(widget.winfo_class(), widget.winfo_ismapped(),
                widget.winfo_width(), widget.winfo_height()) for widget in widgets])

    def start(self):
        """Start the app."""
        self.root.mainloop()

    def initUI(self):
        """Create the UI."""
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=2)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.inputPane = LabelFrame(self, text="Input")
        self.inputPane.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        self.inputPane.grid_columnconfigure(0, weight=1)
        self.inputPane.grid_rowconfigure(0, weight=1)
        self.inputText = Text(self.inputPane, height=26, width=20, wrap=WORD, font=("Helvetica", 24))
        self.inputText.grid(row=0, column=0, sticky="nsew")

        self.stackPane = LabelFrame(self, text="Stack")
        self.stackPane.grid(row=0, column=1, sticky="nsew", padx=4, pady=4)
        self.stackPane.grid_columnconfigure(0, weight=1)
        self.stackPane.grid_rowconfigure(0, weight=1)
        self.stackText = Text(self.stackPane, height=26, width=20, wrap=WORD, font=("Helvetica", 24))
        self.stackText.grid(row=0, column=0, sticky="nsew")

        self.variablesPane = LabelFrame(self, text="Variables")
        self.variablesPane.grid(row=0, column=2, sticky="nsew", padx=4, pady=4)
        self.variablesPane.grid_columnconfigure(0, weight=1)
        self.variablesPane.grid_rowconfigure(0, weight=1)
        self.variablesText = Text(self.variablesPane, height=26, width=10, wrap=WORD, font=("Helvetica", 24))
        self.variablesText.grid(row=0, column=0, sticky="nsew")

    def replaceVariables(self, inStr):
        """The RPNCalculator has a dictionary of variables as well as a stack. Replace all variables with their values."""
        for name, val in self.calc.variables.items():
            inStr = inStr.replace(name, str(val))
        return inStr

    def onKey(self, event=None):
        """Handle key presses."""

        # Clear the calculator
        self.calc.cls("")
        # Clear the stack widget
        self.stackText.delete("1.0", END)
        # Clear the variables widget
        self.variablesText.delete("1.0", END)

        # Process the input
        for line in self.inputText.get("1.0", END).splitlines():
            # line = line.strip()
            line = self.replaceVariables(line.strip())
            if line == "":
                # Deal with whitespace lines
                self.stackText.insert(END, '\n')
            else:
                try:
                    # Try to perform the calculation
                    self.calc(line)
                    self.stackText.insert(END, str(self.calc) + "\n")
                except:
                    self.stackText.insert(END, "Error\n")

        # Display the variables in lexical order
        for name, val in sorted(self.calc.variables.items()):
            self.variablesText.insert(END, name + " is ")
            self.variablesText.insert(END, str(val) + "\n")

        return None


if __name__ == '__main__':
    RPNCalculatorApp().start()
