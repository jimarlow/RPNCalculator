# RPN Calculator

A desktop reverse Polish notation (RPN) calculator built with Python and CustomTkinter.

## Features

- Editable, multiline expression input
- Live stack and variable displays
- Calculator keypad grouped by function
- Variable assignment and reuse

## Requirements

- Python with Tk/Tcl support
- Dependencies listed in `requirements.txt`

## Run

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python NewRPNCalculatorUI.py
```

## Tests

```sh
python -m unittest discover -s tests -v
```

The previous Tkinter interface is retained in `old/`.
