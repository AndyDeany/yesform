import csv
from datetime import datetime
import statistics


class Pick:

    PRICE_EP_BOG = "ep_bog"
    PRICE_BSP = "bsp"

    def __init__(self, pick_list, price):
        self.date = datetime.strptime(pick_list[0], "%d/%m/%Y")
        self.time = pick_list[1]
        self.horse = pick_list[2]
        self.course = pick_list[3]
        self.finishing_position = pick_list[4]
        self.ep = float(pick_list[13])
        self.sp = float(pick_list[6]) + 1.0
        self.bsp = float(pick_list[7])
        self.price = price

    def __repr__(self):
        return f"{self.date} - {self.course} - {self.time} - {self.horse}"


picks = []


def add_picks_from_csv(csv_filename, price=Pick.PRICE_EP_BOG):
    with open(f"systems/{csv_filename}") as input_csv:
        picks_csv = csv.reader(input_csv)
        first_line = True
        for line in picks_csv:
            if first_line:
                first_line = False
                continue
            picks.append(Pick(line, price=price))


# EP Systems
add_picks_from_csv("TN2.csv")
add_picks_from_csv("DTR.csv")
add_picks_from_csv("MR3.csv")   # Not core
add_picks_from_csv("LT6R.csv")
add_picks_from_csv("JLT2.csv")  # Not core
add_picks_from_csv("PnJ.csv")   # Not core
#add_picks_from_csv("TJS.csv")
add_picks_from_csv("accas.csv")
#add_picks_from_csv("DDTR.csv") # Kinda bad
#add_picks_from_csv("DTR2.csv") # Kinda bad

# BSP Systems
#add_picks_from_csv("6lto.csv")
add_picks_from_csv("pacef.csv", Pick.PRICE_BSP)
add_picks_from_csv("topofpower.csv", Pick.PRICE_BSP)
add_picks_from_csv("topspeedandjockey.csv", Pick.PRICE_BSP)
add_picks_from_csv("NTFcheltenham.csv", Pick.PRICE_BSP)
add_picks_from_csv("cheltenham-stiff.csv", Pick.PRICE_BSP)
add_picks_from_csv("DTR-hurdles-only.csv", Pick.PRICE_BSP)
add_picks_from_csv("UKtravellers.csv", Pick.PRICE_BSP)
add_picks_from_csv("PnJ.csv", Pick.PRICE_BSP)
add_picks_from_csv("EASED.csv", Pick.PRICE_BSP)


picks.sort(key=lambda p: (p.date, p.time, p.horse))    # Sort picks by course then time


profit = 0.0
max_profit = 0.0
max_drawdown = 0.0

drawdowns = []


class Run:

    all = []

    def __init__(self, date):
        self.date = date
        self.profit = 0.0
        self.lowest = 0.0

    def change_profit(self, change):
        self.profit += change
        if self.profit < self.lowest:
            self.lowest = self.profit

    def __repr__(self):
        return f"{self.date.strftime('%d/%m/%Y')}: {self.profit=}, {self.lowest=}"

    @classmethod
    def start(cls, date):
        cls.all.append(cls(date))

    @classmethod
    def update_profits(cls, change):
        for run in cls.all:
            run.change_profit(change)


day_picks = [picks.pop(0)]

for pick in picks:
    if pick.date == day_picks[0].date:
        day_picks.append(pick)
        if pick != picks[-1]:
            continue

    Run.start(day_picks[0].date)
    profit -= len(day_picks)
    Run.update_profits(-len(day_picks))
    if profit - max_profit < max_drawdown:
        max_drawdown = profit - max_profit
    drawdowns.append(profit-max_profit)

    for day_pick in day_picks:
        if day_pick.finishing_position == "1":
            if day_pick.price == Pick.PRICE_EP_BOG:
                gains = max(day_pick.ep, day_pick.sp)*0.95  # Account for R4/late picks with 0.95 * odds (estimate)
            elif day_pick.price == Pick.PRICE_BSP:
                gains = day_pick.bsp
            else:
                raise ValueError(f"Unknown pricing type: {day_pick.price}")
            profit += gains
            Run.update_profits(gains)
        if profit > max_profit:
            max_profit = profit

    day_picks = [pick]

drawdowns.sort()
average_drawdown = statistics.mean(drawdowns)
print(f"{profit=}")
print(f"{max_drawdown=}")
print(f"{average_drawdown=}")
print("")


Run.all.sort(key=lambda r: r.lowest)

units = 150.0

for run_number, run in enumerate(Run.all):
    if -units < run.lowest:
        percentage_chance_of_going_bust = 100.0 * float(run_number)/len(Run.all)
        print(f"{round(percentage_chance_of_going_bust, 3)}% chance of going bust with {units}u bankroll.")
        break

lowests = [run.lowest for run in Run.all]
print("")
print(f"{statistics.mean(lowests)=}")
print(f"{statistics.stdev(lowests)=}")
