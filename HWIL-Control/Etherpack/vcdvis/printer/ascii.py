from vcd_signal import SignalStore
from timestamp import Timestamp
from value import ValueArray


def draw_signal(label: str, values: ValueArray, padding: int):
    value_str = " |" + values.print_ascii() + "|"
    print("{}{}".format(label.rjust(padding), value_str))


def draw(signals: SignalStore, start: Timestamp, end: Timestamp):
    max_len = max(len(signal.get_label()) for signal in signals.combined())
    padding = max_len + 2
    for (signal, values) in signals.get_values_between(start, end):
        draw_signal(signal.get_label(), values, padding)
