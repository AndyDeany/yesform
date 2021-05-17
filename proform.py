import csv
import plotly.graph_objects as go


class UnwantedSystemError(ValueError):
    """Exception for raising when the system of the given pick is not desired."""


class Pick:
    """Class for representing a pick."""

    SYSTEM_TN2 = "TN2"
    SYSTEM_DTR = "DTR"
    SYSTEM_MR3 = "MR3"
    SYSTEM_LT6R = "LT6R"
    SYSTEM_JLT2 = "JLT2"
    SYSTEM_TJS = "TJS"
    SYSTEM_ACCAS = "ACCAS"

    SYSTEM_PACE = "PACE"
    SYSTEM_EASED = "EASED"
    SYSTEM_TOP_OF_POWER = "TOP"
    SYSTEM_TOP_SPEED_AND_JOCKEY = "SnJ"
    SYSTEM_NTF_CHELTENHAM_1 = "NTF1"
    SYSTEM_NTF_CHELTENHAM_2 = "NTF2"
    SYSTEM_DTR_HURDLES_ONLY = "DTRH"
    SYSTEM_UK_TRAVELLERS = "UKT"
    SYSTEM_SPTT = "SPTT"
    SYSTEM_SPTJ = "SPTJ"

    SYSTEMS = {     # Translating from CSV names to nice abbreviations
        "JR-TN2": SYSTEM_TN2,
        "JR-DTR": SYSTEM_DTR,
        "JR-MR3.2": SYSTEM_MR3,
        "JR - LT6R": SYSTEM_LT6R,
        "JR-JLT2": SYSTEM_JLT2,
        "JR - ACCAS": SYSTEM_ACCAS,
        "tjs": SYSTEM_TJS,

        "jr-pace1": SYSTEM_PACE,
        "JR-EASED": SYSTEM_EASED,
        "Top of Power": SYSTEM_TOP_OF_POWER,
        "Top Speed and Jockey": SYSTEM_TOP_SPEED_AND_JOCKEY,
        "NTF Cheltenham": SYSTEM_NTF_CHELTENHAM_1,
        "cheltsLTOstiff": SYSTEM_NTF_CHELTENHAM_2,
        "DTR Hurdles Only": SYSTEM_DTR_HURDLES_ONLY,
        "SPTT": SYSTEM_SPTT,
        "SPTJ": SYSTEM_SPTJ,
    }

    @classmethod
    def initialise_data_columns(cls, column_headers):
        cls.data_columns = {
            "system": column_headers.index("FUTURE_SYSTEM"),
            "horse": column_headers.index("FUTURE_HORSE"),
            "course": column_headers.index("FUTURE_VENUE"),
            "time": column_headers.index("FUTURE_TIME"),
            "date": column_headers.index("FUTURE_RACEDATE")
        }

    def __init__(self, pick_list, allowed_systems):
        """Create a Pick instance."""
        try:
            system = self.SYSTEMS[pick_list[self.data_columns["system"]]]
        except KeyError:
            print(f"WARNING: Unknown system in CSV '{pick_list[self.data_columns['system']]}'.")
            raise UnwantedSystemError(f"Unknown system '{pick_list[self.data_columns['system']]}'")

        if system not in allowed_systems:
            raise UnwantedSystemError(f"Unknown system: {system}")

        self.systems = {system}
        self.horse = pick_list[self.data_columns["horse"]]
        self.course = pick_list[self.data_columns["course"]]
        self.time = pick_list[self.data_columns["time"]]
        self.date = pick_list[self.data_columns["date"]]

    @property
    def system(self):
        if self.SYSTEM_JLT2 in self.systems:
            return self.SYSTEM_JLT2
        elif self.SYSTEM_MR3 in self.systems:
            return self.SYSTEM_MR3
        return self.systems.copy().pop()

    @property
    def quantity(self):
        """Return the amount of systems that chose this pick."""
        return len(self.systems)

    def __repr__(self):
        return f"{self.system} - {self.date} - {self.course} - {self.time} - {self.horse}"

    @property
    def row_fill_color(self):
        """Return the row fill color for this pick."""
        if {Pick.SYSTEM_MR3, Pick.SYSTEM_JLT2}.issubset(self.systems):
            return "#afc3fa"
        if Pick.SYSTEM_JLT2 in self.systems:
            return "#d5cff3"
        if Pick.SYSTEM_MR3 in self.systems:
            return "#adf4e7"
        return "#cfe2f3"

    def get_row_line_color(self, picks):
        """Return the row line color for this pick."""
        index = picks.index(self)
        if index == 0:
            return "#bbbbbb"

        previous_pick = picks[index - 1]
        if self.course != previous_pick.course:
            return "#000000"

        return "#bbbbbb"


def create_picks_table(systems):
    picks = []

    with open("ferret.csv") as input_csv:
        picks_csv = csv.reader(input_csv)

        for line_number, line in enumerate(picks_csv):
            if line_number == 0:
                Pick.initialise_data_columns(line)
                continue    # Skip first line - column headers, not a pick
            try:
                picks.append(Pick(line, systems))
            except UnwantedSystemError:
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

    create_and_show_table(picks)


def get_multiples_text(picks, multiplier):
    number = len([pick for pick in picks if pick.quantity == multiplier])
    multiplier_in_words = {
        2: "doub",
        3: "tri",
        4: "quad",
        5: "quin",
        6: "sex",
    }[multiplier]
    s = "" if number == 1 else "s"
    return "{} {}{}, ".format(number, multiplier_in_words, s)


def create_and_show_table(picks):
    multiples_text = "".join((get_multiples_text(picks, n) for n in range(2, 5)))[:-2]
    fig = go.Figure(data=[go.Table(
        columnwidth=[11, 40, 15, 40, 7],
        columnorder=[1, 2, 3, 4, 5],
        header=dict(
            values=["<b>Sys</b>", "<b>Course</b>", "<b>Time</b>",
                    "<b>        Horse ({} total)<br>({})</b>".format(len(picks), multiples_text),
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
            line_color=[[pick.get_row_line_color(picks) for pick in picks]],
            fill_color=[[pick.row_fill_color for pick in picks]],
            align=["center", "left", "center", "left", "center"], font=dict(color="black", size=14),
            height=22
            ))
    ])

    fig.update_layout(width=650)
    fig.show()


if __name__ == "__main__":
    ep_systems = [Pick.SYSTEM_DTR, Pick.SYSTEM_MR3, Pick.SYSTEM_LT6R,
                  Pick.SYSTEM_ACCAS, Pick.SYSTEM_TJS, Pick.SYSTEM_JLT2]
    create_picks_table(ep_systems)         # ep6
    ep_systems.remove(Pick.SYSTEM_JLT2)
    create_picks_table(ep_systems)         # ep5
    ep_systems.remove(Pick.SYSTEM_ACCAS)
    ep_systems.remove(Pick.SYSTEM_TJS)
    create_picks_table(ep_systems)         # ep3
    bsp_systems = [Pick.SYSTEM_PACE, Pick.SYSTEM_EASED, Pick.SYSTEM_TOP_OF_POWER,
                   Pick.SYSTEM_TOP_SPEED_AND_JOCKEY, Pick.SYSTEM_NTF_CHELTENHAM_1,
                   Pick.SYSTEM_NTF_CHELTENHAM_2, Pick.SYSTEM_DTR_HURDLES_ONLY,
                   Pick.SYSTEM_SPTT, Pick.SYSTEM_SPTJ]
    create_picks_table(bsp_systems)
