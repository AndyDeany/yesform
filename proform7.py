import csv
import plotly.graph_objects as go

picks = []


class Pick:

    SYSTEM_TN2 = "TN2"
    SYSTEM_DTR = "DTR"
    SYSTEM_MR3 = "MR3"
    SYSTEM_LT6R = "LT6R"
    SYSTEM_JLT2 = "JLT2"
    SYSTEM_PnJ = "PnJ"
    SYSTEM_ACCAS = "ACCAS"

    def __init__(self, column_headers, pick_list):

        data_columns = {
            "system": column_headers.index("FUTURE_SYSTEM"),
            "horse": column_headers.index("FUTURE_HORSE"),
            "course": column_headers.index("FUTURE_VENUE"),
            "time": column_headers.index("FUTURE_TIME"),
            "date": column_headers.index("FUTURE_RACEDATE")
        }

        self.systems = set()
        system = pick_list[data_columns["system"]]
        if system == "JR-TN2":
            self.systems.add(self.SYSTEM_TN2)
        elif system == "JR-DTR":
            self.systems.add(self.SYSTEM_DTR)
        elif system == "JR-MR3.2":
            self.systems.add(self.SYSTEM_MR3)
        elif system == "JR - LT6R":
            self.systems.add(self.SYSTEM_LT6R)
        elif system == "JR-JLT2":
            self.systems.add(self.SYSTEM_JLT2)
        elif system == "jockey+pace":
            self.systems.add(self.SYSTEM_PnJ)
        elif system == "JR - ACCAS":
            self.systems.add(self.SYSTEM_ACCAS)
        else:
            raise ValueError(f"Unknown system: {system}")

        self.horse = pick_list[data_columns["horse"]]
        self.course = pick_list[data_columns["course"]]
        self.time = pick_list[data_columns["time"]]
        self.date = pick_list[data_columns["date"]]

    @property
    def system(self):
        if self.SYSTEM_JLT2 in self.systems:
            return self.SYSTEM_JLT2
        elif self.SYSTEM_MR3 in self.systems:
            return self.SYSTEM_MR3
        return self.systems.copy().pop()

    @property
    def quantity(self):
        return len(self.systems)

    def __repr__(self):
        return f"{self.system} - {self.date} - {self.course} - {self.time} - {self.horse}"


with open("ferret.csv") as input_csv:
    picks_csv = csv.reader(input_csv)

    first_line = ""
    for line in picks_csv:
        if not first_line:
            first_line = line
            continue    # Skip first line - column headers, not a pick
        try:
            picks.append(Pick(first_line, line))
        except ValueError:
            continue    # Ignoring picks that aren't from our main EP systems.


picks.sort(key=lambda p: (p.course, p.time))    # Sort picks by course then time


picks_with_dupes = picks
picks = []

for single_pick in picks_with_dupes:
    for pick in picks:
        if single_pick.horse == pick.horse:
            pick.systems.add(single_pick.system)
            break
    else:
        picks.append(single_pick)


num_doubles = len([pick for pick in picks if pick.quantity == 2])
num_triples = len([pick for pick in picks if pick.quantity == 3])
num_quadruples = len([pick for pick in picks if pick.quantity == 4])


def get_row_fill_color(pick):
    """Return the row fill color for the given pick."""
    if {Pick.SYSTEM_MR3, Pick.SYSTEM_JLT2}.issubset(pick.systems):
        return "#afc3fa"
    elif Pick.SYSTEM_JLT2 in pick.systems:
        return "#d5cff3"
    elif Pick.SYSTEM_MR3 in pick.systems:
        return "#adf4e7"
    else:
        return "#cfe2f3"


def get_row_line_color(pick):
    """Return the row line color for the given pick."""
    index = picks.index(pick)
    if index == 0:
        return "#bbbbbb"

    previous_pick = picks[index - 1]
    if pick.course != previous_pick.course:
        return "#000000"

    return "#bbbbbb"


fig = go.Figure(data=[go.Table(
    columnwidth=[11, 40, 15, 40, 7],
    columnorder=[1, 2, 3, 4, 5],
    header=dict(
        values=["<b>Sys</b>", "<b>Course</b>", "<b>Time</b>",
                "<b>        Horse ({} total)<br>({} doub{}, {} tri{}, {} quad{})</b>"
                .format(len(picks), num_doubles, "" if num_doubles == 1 else "s",
                        num_triples, "" if num_triples == 1 else "s", num_quadruples, "" if num_quadruples == 1 else "s"),
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
