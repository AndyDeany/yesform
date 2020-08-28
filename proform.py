import csv
import plotly.graph_objects as go

picks = []


class Pick:

    SYSTEM_TN2 = "TN2"
    SYSTEM_DTR = "DTR"
    SYSTEM_MR3 = "MR3"

    def __init__(self, pick_list):
        system = pick_list[0]
        if system == "JR-TN2":
            self.system = self.SYSTEM_TN2
        elif system == "JR-DTR":
            self.system = self.SYSTEM_DTR
        elif system == "JR-MR3.2":
            self.system = self.SYSTEM_MR3
        else:
            raise ValueError(f"Unknown system: {system}")

        self.horse = pick_list[1]
        self.course = pick_list[2]
        self.time = pick_list[3]
        self.date = pick_list[4]

        self.is_double = False

    def __repr__(self):
        return f"{self.system} - {self.date} - {self.course} - {self.time} - {self.horse}"


with open("ferret.csv") as input_csv:
    picks_csv = csv.reader(input_csv)
    first_line = True
    for line in picks_csv:
        if first_line:
            first_line = False
            continue    # Skip first line - column headers, not a pick

        picks.append(Pick(line))


picks.sort(key=lambda p: (p.course, p.time))    # Sort picks by course then time


def is_duplicate_of_mr3_pick(pick):
    """Return whether a pick is a duplicate of an MR3 pick. Also sets the mr3_pick.is_double attribute if so."""
    if pick.system == Pick.SYSTEM_MR3:
        return False    # An MR3 pick cannot be a duplicate of itself

    for mr3_pick in (p for p in picks if p.system == Pick.SYSTEM_MR3):
        if mr3_pick.horse == pick.horse:
            mr3_pick.is_double = True
            return True

full_length = len(picks)
picks = [pick for pick in picks if not is_duplicate_of_mr3_pick(pick)]
num_doubles = full_length - len(picks)


extras = []
for pick in picks:
    extra = ""
    if pick.system == Pick.SYSTEM_MR3:
        extra += "MR3"
    if pick.is_double:
        extra += ", x2"
    extras.append(extra)

fig = go.Figure(data=[go.Table(
    columnwidth=[40, 15, 50, 20],
    columnorder=[1, 2, 3, 4],
    header=dict(
        values=['<b>Course</b>', '<b>Time</b>', f"<b>Horse ({len(picks)} total + {num_doubles} doubles)</b>", '<b>Extra</b>'],
        line_color='#bbbbbb', fill_color='#cfe2f3',
        align='center', font=dict(color='black', size=12)
    ),
    cells=dict(
        values=[[pick.course for pick in picks], [pick.time for pick in picks], [pick.horse for pick in picks], extras],
        line_color="#bbbbbb", fill_color="#cfe2f3",
        align='left', font=dict(color='black', size=14),
        height=22
        ))
])

fig.update_layout(width=700)
fig.show()

fig = go.Figure(data=[go.Table(
    columnwidth=[40, 15, 50, 20],
    columnorder=[1, 2, 3, 4],
    header=dict(
        values=['<b>Course</b>', '<b>Time</b>', f"<b>Horse ({len(picks)} total + {num_doubles} doubles)</b>", '<b>Extra</b>'],
        line_color='#bbbbbb', fill_color='#ffb3e8',
        align='center', font=dict(color='black', size=12)
    ),
    cells=dict(
        values=[[pick.course for pick in picks], [pick.time for pick in picks], [pick.horse for pick in picks], extras],
        line_color="#bbbbbb", fill_color="#ffb3e8",
        align='left', font=dict(color='black', size=14),
        height=22
        ))
])

fig.update_layout(width=700)
fig.show()
