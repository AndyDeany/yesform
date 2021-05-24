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


class UnwantedSystemError(ValueError):
    """Exception for raising when the system of the given pick is not desired."""
