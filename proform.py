import csv
import plotly.graph_objects as go

picks = []
lt6r_picks = []
jlt2_picks = []
pnj_picks = []
accas_picks = []
bsp_picks = []
bsp9_picks = []


class Pick:

    # EP BOG
    SYSTEM_TN2 = "TN2"
    SYSTEM_DTR = "DTR"
    SYSTEM_MR3 = "MR3"
    SYSTEM_LT6R = "LT6R"
    SYSTEM_JLT2 = "JLT2"
    SYSTEM_ACCAS = "ACCAS"
    SYSTEM_PnJ = "PnJ"  # Also a BSP system

    # BSP
    SYSTEM_6LTO = "6LTO"
    SYSTEM_ALLOUT = "ALLOUT"

    # BSP9 (with PnJ, above)
    SYSTEM_PACE = "PACE"
    SYSTEM_EASED = "EASED"
    SYSTEM_TOP_OF_POWER = "TOP"
    SYSTEM_TOP_SPEED_AND_JOCKEY = "SnJ"
    SYSTEM_NTF_CHELTENHAM_1 = "NTF1"
    SYSTEM_NTF_CHELTENHAM_2 = "NTF2"
    SYSTEM_DTR_HURDLES_ONLY = "DTRH"
    SYSTEM_UK_TRAVELLERS = "UKT"

    SYSTEMS_BSP8 = (SYSTEM_PACE, SYSTEM_EASED, SYSTEM_TOP_OF_POWER, SYSTEM_TOP_SPEED_AND_JOCKEY,
                    SYSTEM_NTF_CHELTENHAM_1, SYSTEM_NTF_CHELTENHAM_2, SYSTEM_DTR_HURDLES_ONLY, SYSTEM_UK_TRAVELLERS)

    @classmethod
    def standardised_system(cls, system_name):
        """Get the standardised name of the system with the given system_name."""
        try:
            return {
                "JR-TN2": cls.SYSTEM_TN2,
                "JR-DTR": cls.SYSTEM_DTR,
                "JR-MR3.2": cls.SYSTEM_MR3,
                "JR - LT6R": cls.SYSTEM_LT6R,
                "JR-JLT2": cls.SYSTEM_JLT2,
                "jockey+pace": cls.SYSTEM_PnJ,
                "JR - ACCAS": cls.SYSTEM_ACCAS,
                "JR >=6 + jockey": cls.SYSTEM_6LTO,
                "JR-ALLOUT": cls.SYSTEM_ALLOUT,
                "jr-pace1": cls.SYSTEM_PACE,
                "JR-EASED": cls.SYSTEM_EASED,
                "Top of Power": cls.SYSTEM_TOP_OF_POWER,
                "Top Speed and Jockey": cls.SYSTEM_TOP_SPEED_AND_JOCKEY,
                "NTF Cheltenham": cls.SYSTEM_NTF_CHELTENHAM_1,
                "cheltsLTOstiff": cls.SYSTEM_NTF_CHELTENHAM_2,
                "DTR Hurdles Only": cls.SYSTEM_DTR_HURDLES_ONLY,
                "UK Travellers": cls.SYSTEM_UK_TRAVELLERS,
            }[system_name]
        except KeyError:
            raise ValueError(f"Unknown system: {system_name}")

    def __init__(self, pick_list):
        offset = 0
        if pick_list[0] == "Active":
            offset = 1

        system = pick_list[0+offset]
        self.system = self.standardised_system(system)

        self.horse = pick_list[1+offset]
        self.course = pick_list[2+offset]
        self.time = pick_list[3+offset]
        self.date = pick_list[4+offset]

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

        pick = Pick(line)
        if pick.system == Pick.SYSTEM_LT6R:
            lt6r_picks.append(pick)
        elif pick.system == Pick.SYSTEM_JLT2:
            jlt2_picks.append(pick)
        elif pick.system == Pick.SYSTEM_PnJ:
            pnj_picks.append(pick)
            bsp9_picks.append(pick)
        elif pick.system == Pick.SYSTEM_ACCAS:
            accas_picks.append(pick)
        elif pick.system in (Pick.SYSTEM_6LTO, Pick.SYSTEM_ALLOUT):
            bsp_picks.append(pick)
        elif pick.system in Pick.SYSTEMS_BSP8:
            bsp9_picks.append(pick)
        else:
            picks.append(pick)


# Sort picks by course then time
picks.sort(key=lambda p: (p.course, p.time))
lt6r_picks.sort(key=lambda p: (p.course, p.time))
jlt2_picks.sort(key=lambda p: (p.course, p.time))
pnj_picks.sort(key=lambda p: (p.course, p.time))
accas_picks.sort(key=lambda p: (p.course, p.time))
bsp_picks.sort(key=lambda p: (p.course, p.time))


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


def get_row_fill_color(pick):
    """Return the row fill color for the given pick."""
    return "#beebed" if pick.system == Pick.SYSTEM_MR3 else "#cfe2f3"


def get_bsp_row_fill_color(pick):
    """Return the row fill color for the given pick."""
    return "#cfe2f3" if pick.system == Pick.SYSTEM_6LTO else "#ffbfb8"


def get_row_line_color(pick):
    """Return the row line color for the given pick."""
    index = picks.index(pick)
    if index == 0:
        return "#bbbbbb"

    previous_pick = picks[index - 1]
    if pick.course != previous_pick.course:
        return "#000000"

    return "#bbbbbb"


def get_lt6r_row_line_color(pick):
    """Return the row line color for the given lt6r pick."""
    index = lt6r_picks.index(pick)
    if index == 0:
        return "#bbbbbb"

    previous_pick = lt6r_picks[index - 1]
    if pick.course != previous_pick.course:
        return "#000000"

    return "#bbbbbb"


def get_bsp_row_line_color(pick):
    """Return the row line color for the given lt6r pick."""
    index = bsp_picks.index(pick)
    if index == 0:
        return "#bbbbbb"

    previous_pick = bsp_picks[index - 1]
    if pick.course != previous_pick.course:
        return "#000000"

    return "#bbbbbb"


fig = go.Figure(data=[go.Table(
    columnwidth=[11, 40, 15, 50, 7],
    columnorder=[1, 2, 3, 4, 5],
    header=dict(
        values=["<b>Sys</b>", "<b>Course</b>", "<b>Time</b>",
                f"<b>Horse ({len(picks)} total + {num_doubles} doubles)</b>", "<b>x</b>"],
        line_color="#bbbbbb", fill_color="#cfe2f3",
        align="center", font=dict(color="black", size=12)
    ),
    cells=dict(
        values=[[pick.system for pick in picks], [pick.course for pick in picks],
                [pick.time for pick in picks], [pick.horse for pick in picks],
                ["x2" if pick.is_double else "" for pick in picks]],
        line_color=[[get_row_line_color(pick) for pick in picks]],
        fill_color=[[get_row_fill_color(pick) for pick in picks]],
        align=["center", "left", "center", "left", "center"], font=dict(color="black", size=14),
        height=22
        ))
])

fig.update_layout(width=700)
fig.show()

# fig = go.Figure(data=[go.Table(
#     columnwidth=[11, 40, 15, 50, 7],
#     columnorder=[1, 2, 3, 4, 5],
#     header=dict(
#         values=["<b>Sys</b>", "<b>Course</b>", "<b>Time</b>",
#                 f"<b>Horse ({len(lt6r_picks)} total)"],
#         line_color="#bbbbbb", fill_color="#cfe2f3",
#         align="center", font=dict(color="black", size=12)
#     ),
#     cells=dict(
#         values=[[pick.system for pick in lt6r_picks], [pick.course for pick in lt6r_picks],
#                 [pick.time for pick in lt6r_picks], [pick.horse for pick in lt6r_picks],
#                 ["x2" if pick.is_double else "" for pick in lt6r_picks]],
#         line_color=[[get_lt6r_row_line_color(pick) for pick in lt6r_picks]],
#         fill_color="#cfe2f3",
#         align=["center", "left", "center", "left", "center"], font=dict(color="black", size=14),
#         height=22
#         ))
# ])
#
# fig.update_layout(width=700)
# fig.show()

fig = go.Figure(data=[go.Table(
    columnwidth=[11, 40, 15, 50, 7],
    columnorder=[1, 2, 3, 4, 5],
    header=dict(
        values=["<b>Sys</b>", "<b>Course</b>", "<b>Time</b>",
                f"<b>Horse ({len(bsp_picks)} total)"],
        line_color="#bbbbbb", fill_color="#cfe2f3",
        align="center", font=dict(color="black", size=12)
    ),
    cells=dict(
        values=[[pick.system for pick in bsp_picks], [pick.course for pick in bsp_picks],
                [pick.time for pick in bsp_picks], [pick.horse for pick in bsp_picks],
                ["x2" if pick.is_double else "" for pick in bsp_picks]],
        line_color=[[get_bsp_row_line_color(pick) for pick in bsp_picks]],
        fill_color=[[get_bsp_row_fill_color(pick) for pick in bsp_picks]],
        align=["center", "left", "center", "left", "center"], font=dict(color="black", size=14),
        height=22
        ))
])

fig.update_layout(width=700)
fig.show()
