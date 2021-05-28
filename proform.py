import csv
import requests

from pick import Pick, UnwantedSystemError
from image import create_image


CSV_FILES_WEBHOOK_URL = "https://discord.com/api/webhooks/845734661485232238/HY0UsqaNs8EurUljOUzxjlubdhnbjxLtcuETsSbfbShzvxRRHaknjc_YWX7y2rXRRYMK"  # noqa
SYSTEMS_WEBHOOK_URLS = {
    "ep6": "https://discord.com/api/webhooks/846180242111856680/TJT9QJMWN0L45eKChSn-VaFGa5O-cLEd8uAP-u3LvoO6sAZzjXcm1HPsCvmdAB2K48Bq",      # noqa
    "ep5": "https://discord.com/api/webhooks/846180324114825216/fuS0wEfZwcELA2JQL2hi28pZexXbcev8Y87y1vMtgDV5n1sfIx1j9w-8ZsAnBTXHRbmc",      # noqa
    "ep3": "https://discord.com/api/webhooks/846180375821549568/o08S9GMjKw8IzriM2kA8T2D9pCdI0ImLkSnJGcPmsoSGZ2Gj3VZjtAg-9k7gfTx0dgqM",      # noqa
    "bsp9": "https://discord.com/api/webhooks/846180405132263454/yJi8Ru9qNYmFTrUFFTh7TJVjOXP3QS3qNu6VRcqKve4_SUGYpAu25IKfkuftmPKY8tmL",     # noqa
}
HORSE_NAMES_WEBHOOK_URL = "https://discord.com/api/webhooks/843804572791341066/ENdGpCbLQU-wg-wUv8pifgmMOw5JFbaKYyG8R9ECN7P-MKquchROZT7jCV662Bspb02H"    # noqa


def upload_file(webhook_url, file_path):
    """Upload the file at the given file path to the given webhook_url."""
    requests.post(webhook_url, files={"upload_file": open(file_path, "rb")})


def send_message(webhook_url, message):
    """Send the given message to the given webhook_url."""
    response = requests.post(webhook_url, json={"content": message})
    if response.status_code == 429:     # If rate limited
        send_message(webhook_url, message)  # Try again


def get_picks(systems):
    """Get the picks from the CSV from the given systems."""
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

    return picks


def create_and_upload_table(picks, name):
    """Create and upload a PNG with the given name containing a table showing the given picks."""
    upload_file(SYSTEMS_WEBHOOK_URLS[name], create_image(picks, name))


def create_picks_table(systems, name):
    """Create and upload a picks table created from the given system with the given name."""
    picks = get_picks(systems)
    create_and_upload_table(picks, name)


def upload_horse_names(picks):
    """Upload the horse names from the given picks to the #horse-names channel."""
    message = "\n".join(pick.horse for pick in picks)
    message += "\nexit"
    send_message(HORSE_NAMES_WEBHOOK_URL, message)


if __name__ == "__main__":
    upload_file(CSV_FILES_WEBHOOK_URL, "./ferret.csv")
    ep_systems = [Pick.SYSTEM_DTR, Pick.SYSTEM_MR3, Pick.SYSTEM_LT6R,
                  Pick.SYSTEM_ACCAS, Pick.SYSTEM_TJS, Pick.SYSTEM_JLT2]
    create_picks_table(ep_systems, "ep6")
    upload_horse_names(get_picks(ep_systems))
    ep_systems.remove(Pick.SYSTEM_JLT2)
    create_picks_table(ep_systems, "ep5")
    ep_systems.remove(Pick.SYSTEM_ACCAS)
    ep_systems.remove(Pick.SYSTEM_TJS)
    create_picks_table(ep_systems, "ep3")
    bsp_systems = [Pick.SYSTEM_PACE, Pick.SYSTEM_EASED, Pick.SYSTEM_TOP_OF_POWER,
                   Pick.SYSTEM_TOP_SPEED_AND_JOCKEY, Pick.SYSTEM_NTF_CHELTENHAM_1,
                   Pick.SYSTEM_NTF_CHELTENHAM_2, Pick.SYSTEM_DTR_HURDLES_ONLY,
                   Pick.SYSTEM_SPTT, Pick.SYSTEM_SPTJ]
    create_picks_table(bsp_systems, "bsp9")
