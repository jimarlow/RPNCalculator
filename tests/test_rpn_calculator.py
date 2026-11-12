import math
import unittest
from types import SimpleNamespace

from NewRPNCalculatorUI import NewRPNCalculatorUI
from RPNCalculator import RPNCalculator


class FakeText:
    def __init__(self, value="", insert_index="1.0"):
        self.value = value
        self.insert_index = insert_index
        self.modified = False
        self.focused = False
        self.delete_calls = []

    def get(self, start, end=None):
        offset = self._offset()
        if start == "insert-1c" and end == "insert":
            return self.value[max(0, offset - 1):offset]
        if start == "insert linestart" and end == "insert":
            line_start = self.value.rfind("\n", 0, offset) + 1
            return self.value[line_start:offset]
        return self.value

    def edit_modified(self, value=None):
        if value is not None:
            self.modified = value
        return self.modified

    def configure(self, **kwargs):
        self.state = kwargs.get("state", getattr(self, "state", None))

    def delete(self, start, end):
        self.delete_calls.append((start, end))
        if start == "1.0" and end == "end":
            self.value = ""
            self.insert_index = "1.0"
            self.modified = True
        elif start == "insert-1c" and end == "insert":
            offset = self._offset()
            if offset:
                self.value = self.value[:offset - 1] + self.value[offset:]
                cursor = self.value[:offset - 1]
                line = cursor.count("\n") + 1
                column = len(cursor.rsplit("\n", maxsplit=1)[-1])
                self.insert_index = f"{line}.{column}"
                self.modified = True
        elif start == "insert" and end == "insert+1c":
            offset = self._offset()
            if offset < len(self.value):
                self.value = self.value[:offset] + self.value[offset + 1:]
                self.modified = True
        elif end.endswith(".end"):
            line = int(start.split(".", maxsplit=1)[0]) - 1
            lines = self.value.split("\n")
            if line < len(lines):
                lines[line] = ""
            self.value = "\n".join(lines)
            self.insert_index = f"{line + 1}.0"
            self.modified = True

    def insert(self, index, value):
        if index == "1.0":
            offset = 0
        else:
            line, column = (int(part) for part in self.insert_index.split("."))
            lines = self.value.split("\n")
            offset = sum(len(part) + 1 for part in lines[: line - 1]) + column
        prefix = self.value[:offset]
        self.value = prefix + value + self.value[offset:]
        cursor = prefix + value
        line = cursor.count("\n") + 1
        column = len(cursor.rsplit("\n", maxsplit=1)[-1])
        self.insert_index = f"{line}.{column}"
        self.modified = True

    def index(self, _index):
        return self.insert_index

    def tag_ranges(self, _tag):
        return ()

    def focus_set(self):
        self.focused = True

    def see(self, _index):
        pass

    def _offset(self):
        line, column = (int(part) for part in self.insert_index.split("."))
        lines = self.value.split("\n")
        return sum(len(part) + 1 for part in lines[: line - 1]) + column


class FakeRoot:
    def __init__(self):
        self.after_calls = []
        self.cancelled = []

    def after(self, delay, callback):
        identifier = f"after#{len(self.after_calls) + 1}"
        self.after_calls.append((identifier, delay, callback))
        return identifier

    def after_cancel(self, identifier):
        self.cancelled.append(identifier)


class RPNCalculatorTests(unittest.TestCase):
    def test_registered_operations(self):
        cases = (
            ("2 3 **", 8),
            ("2 3 +", 5),
            ("2 3 -", -1),
            ("2 3 *", 6),
            ("2 3 /", 2 / 3),
            ("2 3 %", 2),
            ("8 2 logN", 3),
            ("100 10 percent", 10),
            ("1.234 2 roundN", 1.23),
            ("3 4 hypot", 5),
            ("5 neg", -5),
            ("5.8 int", 5),
            ("1.2 ceil", 2),
            ("1.8 floor", 1),
            ("1.4 round", 1),
            ("-5 fabs", 5),
            ("5 factorial", 120),
            ("9 sqrt", 3),
            ("8 log2", 3),
            ("100 log10", 2),
            ("pi", math.pi),
            ("e", math.e),
            ("pi deg", 180),
            ("180 rad", math.pi),
            ("0 sin", 0),
            ("0 cos", 1),
            ("0 tan", 0),
            ("0 asin", 0),
            ("1 acos", 0),
            ("0 atan", 0),
            ("1 0 atan2", math.pi / 2),
            ("1 2 3 sum", 6),
        )
        for expression, expected in cases:
            with self.subTest(expression=expression):
                self.assertAlmostEqual(RPNCalculator()(expression), expected)

    def test_stack_and_variable_operations(self):
        calculator = RPNCalculator()
        calculator("1 2 swap")
        self.assertEqual(calculator.stack, [2.0, 1.0])

        calculator("5 x =")
        self.assertEqual(calculator.variables, {"x": 5.0})
        self.assertEqual(calculator.stack, [2.0, 1.0, 5.0])

        calculator("1 cls")
        self.assertEqual(calculator.stack, [])
        self.assertEqual(calculator.variables, {})

    def test_assignment_value_remains_available_to_later_operations(self):
        calculator = RPNCalculator()

        self.assertEqual(calculator("3 test = 4 +"), 7.0)
        self.assertEqual(calculator.stack, [7.0])
        self.assertEqual(calculator.variables, {"test": 3.0})

    def test_variable_reference_after_assignment_uses_its_value(self):
        calculator = RPNCalculator()

        self.assertEqual(calculator("9 temp = temp"), 9.0)
        self.assertEqual(calculator.stack, [9.0, 9.0])
        self.assertEqual(calculator.variables, {"temp": 9.0})

    def test_existing_variable_name_remains_an_assignment_target(self):
        calculator = RPNCalculator()

        calculator("2 x = 5 x =")

        self.assertEqual(calculator.stack, [2.0, 5.0])
        self.assertEqual(calculator.variables, {"x": 5.0})

    def test_variable_resolution_uses_whole_tokens(self):
        calculator = RPNCalculator()

        self.assertEqual(calculator("2 i = pi i +"), math.pi + 2.0)

    def test_valid_expression_still_calculates(self):
        calculator = RPNCalculator()

        self.assertEqual(calculator("2 3 +"), 5.0)
        self.assertEqual(calculator.stack, [5.0])

    def test_factorial_accepts_integral_float_input(self):
        calculator = RPNCalculator()

        self.assertEqual(calculator("5 factorial"), 120)

    def test_factorial_rejects_non_integer_and_restores_stack(self):
        for value in ("5.5", "-1"):
            with self.subTest(value=value):
                calculator = RPNCalculator()
                calculator(value)

                with self.assertRaisesRegex(ValueError, "non-negative integer"):
                    calculator("factorial")

                self.assertEqual(calculator.stack, [float(value)])

    def test_atan2_uses_top_two_values_as_x_then_y(self):
        calculator = RPNCalculator()

        self.assertAlmostEqual(calculator("1 2 atan2"), math.atan2(1, 2))

    def test_unknown_token_is_rejected_without_changing_state(self):
        calculator = RPNCalculator()
        calculator("1 2")
        previous_stack = calculator.stack.copy()

        with self.assertRaisesRegex(ValueError, "Unknown token"):
            calculator("@")

        self.assertEqual(calculator.stack, previous_stack)

    def test_partial_numeric_token_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unknown token"):
            RPNCalculator()("1abc")

    def test_stack_underflow_rolls_back_partial_pops(self):
        calculator = RPNCalculator()
        calculator("1")

        with self.assertRaises(IndexError):
            calculator("+")

        self.assertEqual(calculator.stack, [1.0])

    def test_failed_assignment_rolls_back_stack_and_variables(self):
        calculator = RPNCalculator()

        with self.assertRaisesRegex(ValueError, "Unknown token"):
            calculator("5 x = @")

        self.assertEqual(calculator.stack, [])
        self.assertEqual(calculator.variables, {})


class VariableResolutionTests(unittest.TestCase):
    def setUp(self):
        self.ui = object.__new__(NewRPNCalculatorUI)
        self.ui.calculator = RPNCalculator()

    def test_input_edits_debounce_recalculation(self):
        self.ui.root = FakeRoot()
        self.ui.input_text = FakeText()
        self.ui._recalculation_after_id = None

        self.ui.input_text.modified = True
        self.ui._on_input_modified()
        first_id = self.ui._recalculation_after_id

        self.ui.input_text.modified = True
        self.ui._on_input_modified()

        self.assertEqual(self.ui.root.cancelled, [first_id])
        self.assertEqual(self.ui.root.after_calls[-1][1], 200)

    def test_keypad_has_every_command_and_number_entry(self):
        keys = {
            key
            for _, group_keys, *_ in NewRPNCalculatorUI.KEYPAD_GROUPS
            for key in group_keys
        }
        commands = {
            "swap", "cls", "**", "+", "-", "*", "/", "%", "logN",
            "percent", "roundN", "hypot", "neg", "int", "ceil", "floor",
            "round", "fabs", "factorial", "sqrt", "log2", "log10", "pi",
            "e", "deg", "rad", "sin", "cos", "tan", "asin", "acos", "atan",
            "atan2", "sum", "=",
        }

        self.assertTrue(commands.issubset(keys))
        self.assertNotIn("x", keys)
        self.assertTrue(set("0123456789").issubset(keys))
        self.assertIn(".", keys)
        self.assertIn("Enter", keys)
        self.assertIn("Space", keys)

    def test_keypad_inserts_rpn_tokens_into_input(self):
        self.ui.input_text = FakeText()

        for key in ("2", "Enter", "3", "+"):
            self.ui._insert_key(key)

        self.assertEqual(self.ui.input_text.value, "2\n3 + ")
        self.assertTrue(self.ui.input_text.focused)

    def test_space_key_inserts_a_literal_separator(self):
        self.ui.input_text = FakeText("3", insert_index="1.1")

        self.ui._insert_key("Space")
        self.ui._insert_key("4")
        self.ui._insert_key("5")

        self.assertEqual(self.ui.input_text.value, "3 45")
        self.assertTrue(self.ui.input_text.focused)

    def test_enter_key_inserts_newline_at_the_caret(self):
        self.ui.input_text = FakeText("6 3", insert_index="1.3")

        result = self.ui._handle_input_key(
            SimpleNamespace(char="\r", keysym="Return")
        )

        self.assertEqual(result, "break")
        self.assertEqual(self.ui.input_text.value, "6 3\n")
        self.assertEqual(self.ui.input_text.insert_index, "2.0")

    def test_clear_current_line(self):
        self.ui.input_text = FakeText("one\ntwo\nthree", insert_index="2.1")

        self.ui._clear_current_line()

        self.assertEqual(self.ui.input_text.value, "one\n\nthree")
        self.assertTrue(self.ui.input_text.focused)

    def test_reset_clears_input_results_and_calculator_state(self):
        self.ui.root = FakeRoot()
        self.ui._recalculation_after_id = "after#pending"
        self.ui.input_text = FakeText("5 x =")
        self.ui.stack_text = FakeText("TOP -> 5.0")
        self.ui.variables_text = FakeText("x is 5.0")
        self.ui.calculator("5 x =")

        self.ui._reset_calculator()

        self.assertEqual(self.ui.input_text.value, "")
        self.assertEqual(self.ui.stack_text.value, "")
        self.assertEqual(self.ui.variables_text.value, "")
        self.assertEqual(self.ui.calculator.stack, [])
        self.assertEqual(self.ui.calculator.variables, {})
        self.assertEqual(self.ui.root.cancelled, ["after#pending"])

    def test_failed_line_does_not_corrupt_later_lines(self):
        self.ui.input_text = FakeText("1\n+\n2")
        self.ui.stack_text = FakeText()
        self.ui.variables_text = FakeText()

        self.ui._recalculate()

        lines = self.ui.stack_text.value.splitlines()
        self.assertEqual(lines[:2], ["TOP -> 2.0", "       1.0"])
        self.assertIn("Errors:", lines)
        self.assertTrue(any(line.startswith("Line 2:") for line in lines))

    def test_assignment_value_is_used_by_the_rest_of_its_input_line(self):
        self.ui.input_text = FakeText("3 test = 4 +")
        self.ui.stack_text = FakeText()
        self.ui.variables_text = FakeText()

        self.ui._recalculate()

        self.assertEqual(self.ui.stack_text.value, "TOP -> 7.0")
        self.assertEqual(self.ui.variables_text.value, "test is 3.0")

    def test_variable_reference_after_assignment_is_resolved(self):
        self.ui.input_text = FakeText("9 temp = temp")
        self.ui.stack_text = FakeText()
        self.ui.variables_text = FakeText()

        self.ui._recalculate()

        self.assertEqual(
            self.ui.stack_text.value,
            "TOP -> 9.0\n       9.0",
        )
        self.assertEqual(self.ui.variables_text.value, "temp is 9.0")

    def test_typed_operator_is_spaced_and_power_stays_one_token(self):
        self.ui.input_text = FakeText("6", insert_index="1.1")
        result = self.ui._handle_input_key(SimpleNamespace(char="+"))
        self.assertEqual(result, "break")
        self.assertEqual(self.ui.input_text.value, "6 + ")

        self.ui.input_text = FakeText("6", insert_index="1.1")
        for char in ("*", "*"):
            result = self.ui._handle_input_key(SimpleNamespace(char=char))
        self.assertEqual(result, "break")
        self.assertEqual(self.ui.input_text.value, "6 ** ")

        self.ui.input_text = FakeText("6 3", insert_index="1.3")
        self.ui._handle_input_key(SimpleNamespace(char="+"))
        self.assertEqual(self.ui.input_text.value, "6 3 + ")
        self.assertEqual(RPNCalculator()(self.ui.input_text.value), 9.0)

    def test_operator_after_whitespace_and_unary_minus_are_unchanged(self):
        self.ui.input_text = FakeText("6 ", insert_index="1.2")
        self.ui._handle_input_key(SimpleNamespace(char="+"))
        self.assertEqual(self.ui.input_text.value, "6 + ")

        self.ui.input_text = FakeText()
        self.ui._handle_input_key(SimpleNamespace(char="-"))
        self.assertEqual(self.ui.input_text.value, "-")

    def test_backspace_deletes_the_character_before_the_caret(self):
        self.ui.input_text = FakeText("1234", insert_index="1.4")

        result = self.ui._handle_input_key(
            SimpleNamespace(char="\x08", keysym="BackSpace")
        )

        self.assertEqual(result, "break")
        self.assertEqual(self.ui.input_text.value, "123")

    def test_delete_removes_the_character_after_the_caret(self):
        self.ui.input_text = FakeText("1234", insert_index="1.1")

        result = self.ui._handle_input_key(
            SimpleNamespace(char="", keysym="Delete")
        )

        self.assertEqual(result, "break")
        self.assertEqual(self.ui.input_text.value, "134")

    def test_backspace_removes_operator_spacing_normally(self):
        self.ui.input_text = FakeText("6 3 + ", insert_index="1.6")

        result = self.ui._handle_input_key(
            SimpleNamespace(char="\x08", keysym="BackSpace")
        )

        self.assertEqual(result, "break")
        self.assertEqual(self.ui.input_text.value, "6 3 +")


if __name__ == "__main__":
    unittest.main()
