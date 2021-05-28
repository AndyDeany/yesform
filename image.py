from PIL import Image, ImageDraw, ImageFont
from pick import Pick


BACKGROUND_COLOR = "#36393f"
TEXT_COLOR = "#e8eaed"
JLT2_COLOR = "#2ad6f5"
MR3_COLOR = "#d32ce6"
JLT2_AND_MR3_COLOR = "#2a59f5"
LINE_COLOR = "#60656e"
SPLIT_LINE_COLOR = "#8c5eff"

BUFFER = 2
FONT_FILE = "arial.ttf"


def create_image(picks, name, font_size=15):
    """Create an image showing the given picks in readable format."""
    line_height = font_size + 3*BUFFER
    font = ImageFont.truetype(FONT_FILE, font_size)

    columns = [
        [pick.system for pick in picks],
        [pick.course for pick in picks],
        [pick.time for pick in picks],
        [pick.horse for pick in picks],
        [f"x{pick.quantity}" if pick.quantity > 1 else "" for pick in picks],
    ]

    column_headers = ("Sys", "Course", "Time", f"Horse ({len(picks)})", "x")

    for index, column in enumerate(columns):
        column.insert(0, column_headers[index])

    column_widths = [max((font.getlength(item) for item in column)) + 3*BUFFER for column in columns]

    image_width = int(sum(column_widths))
    image_height = line_height*(len(picks)+1)
    image = Image.new("RGB", (image_width, image_height), color=BACKGROUND_COLOR)
    draw = ImageDraw.Draw(image)

    for column_number in range(len(columns)):
        if column_number == 0:
            continue
        x = sum(column_widths[:column_number])
        draw.line([(x, 0), (x, image_height)], fill=LINE_COLOR)

    courses = columns[1]
    for row_number in range(len(columns[0])):
        if row_number == 0:
            continue
        y = line_height*row_number
        color = LINE_COLOR if courses[row_number] == courses[row_number-1] else SPLIT_LINE_COLOR
        draw.line([(0, y), (image_width, y)], fill=color)

    for column_number, column in enumerate(columns):
        x = BUFFER + sum(column_widths[:column_number])
        for row_number, item in enumerate(column):
            y = BUFFER + line_height*row_number
            coords = (x, y)
            if row_number == 0 or column_number in (0, 2, 4):
                coords = (x + (column_widths[column_number] - font.getlength(item))/2 - BUFFER, y)

            color = TEXT_COLOR
            if column_number == 0 and row_number != 0:
                systems = picks[row_number-1].systems
                if {Pick.SYSTEM_MR3, Pick.SYSTEM_JLT2}.issubset(systems):
                    color = JLT2_AND_MR3_COLOR
                elif Pick.SYSTEM_JLT2 in systems:
                    color = JLT2_COLOR
                elif Pick.SYSTEM_MR3 in systems:
                    color = MR3_COLOR

            draw.text(coords, item, font=font, fill=color)

    file_name = f"{name}.png"
    image.save(file_name)
    return file_name
