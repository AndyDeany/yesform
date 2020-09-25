import csv
import plotly.graph_objects as go

picks = []


class Pick:

    SYSTEM_TN2 = "TN2"
    SYSTEM_DTR = "DTR"
    SYSTEM_MR3 = "MR3"
    SYSTEM_LT6R = "LT6R"
    SYSTEM_PNJ = "PnJ"
    SYSTEM_ACCAS = "ACCAS"
    SYSTEM_TJS = "TJS"

    SYSTEMS = {
        "JR-TN2": SYSTEM_TN2,
        "JR-DTR": SYSTEM_DTR,
        "JR-MR3.2": SYSTEM_MR3,
        "JR - LT6R": SYSTEM_LT6R,
        "jockey+pace": SYSTEM_PNJ,
        "JR - ACCAS": SYSTEM_ACCAS,
        "JR - TJS": SYSTEM_TJS,
    }

    @classmethod
    def initialise_data_columns(cls, column_headers):
        cls.DATA_COLUMNS = {
            "system": column_headers.index("FUTURE_SYSTEM"),
            "horse": column_headers.index("FUTURE_HORSE"),
            "course": column_headers.index("FUTURE_VENUE"),
            "time": column_headers.index("FUTURE_TIME"),
            "date": column_headers.index("FUTURE_RACEDATE")
        }

    def __init__(self, pick_list):

        system = pick_list[self.DATA_COLUMNS["system"]]
        self.system = self.SYSTEMS[system]

        self.horse = pick_list[self.DATA_COLUMNS["horse"]]
        self.course = pick_list[self.DATA_COLUMNS["course"]]
        self.time = pick_list[self.DATA_COLUMNS["time"]]
        self.date = pick_list[self.DATA_COLUMNS["date"]]

        self.quantity = 1

    def __repr__(self):
        return f"{self.system} - {self.date} - {self.course} - {self.time} - {self.horse}"

    def __eq__(self, other):
        return (self.horse == other.horse and self.course == other.course
                and self.time == other.time and self.date == other.date)


with open("ferret.csv") as input_csv:
    picks_csv = csv.reader(input_csv)

    first_line = True
    for line in picks_csv:
        if first_line:
            Pick.initialise_data_columns(line)
            first_line = False
            continue    # Skip first line - column headers, not a pick

        picks.append(Pick(line))


picks.sort(key=lambda p: (p.course, p.time, p.horse))   # Sort picks by course then time then horse

temp = []
for pick in picks:
    if not temp or pick != temp[-1]:
        temp.append(pick)
        continue

    temp[-1].quantity += 1
    if pick.system == Pick.SYSTEM_MR3:
        temp[-1].system = Pick.SYSTEM_MR3

picks = temp

multiples = {x: len([pick for pick in picks if pick.quantity == x]) for x in range(2, 7)}


def get_row_fill_color(pick):
    """Return the row fill color for the given pick."""
    return "#beebed" if pick.system == Pick.SYSTEM_MR3 else "#cfe2f3"


def get_row_line_color(pick):
    """Return the row line color for the given pick."""
    index = picks.index(pick)
    if index == 0:
        return "#bbbbbb"

    previous_pick = picks[index - 1]
    if pick.course != previous_pick.course:
        return "#000000"

    return "#bbbbbb"


def get_multiples_text(multiplier):
    number = multiples[multiplier]
    if number == 0:
        return ""

    multiplier_in_words = {
        2: "double",
        3: "triple",
        4: "quadruple",
        5: "quintuple",
        6: "sextuple"
    }[multiplier]
    s = "" if number == 1 else "s"
    return "{} {}{}, ".format(number, multiplier_in_words, s)


fig = go.Figure(data=[go.Table(
    columnwidth=[11, 40, 15, 40, 7],
    columnorder=[1, 2, 3, 4, 5],
    header=dict(
        values=["<b>Sys</b>", "<b>Course</b>", "<b>Time</b>",
                "<b>    Horse ({} total)<br>({})</b>"
                .format(len(picks), "".join((get_multiples_text(2), get_multiples_text(3),
                        get_multiples_text(4), get_multiples_text(5), get_multiples_text(6)))[:-2]),
                "<b>x</b>"],
        line_color="#bbbbbb", fill_color="#cfe2f3",
        align="center", font=dict(color="black", size=12)
    ),
    cells=dict(
        values=[
            [pick.system for pick in picks],
            [pick.course for pick in picks],
            [pick.time for pick in picks],
            [pick.horse for pick in picks],
            [f"x{pick.quantity}" if pick.quantity > 1 else "" for pick in picks]
        ],
        line_color=[[get_row_line_color(pick) for pick in picks]],
        fill_color=[[get_row_fill_color(pick) for pick in picks]],
        align=["center", "left", "center", "left", "center"], font=dict(color="black", size=14),
        height=22
        ))
])

fig.update_layout(width=650)
fig.show()
