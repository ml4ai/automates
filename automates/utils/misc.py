import platform
import random
import uuid

# -------------------------------------------
# Remove this block to generate different
# UUIDs everytime you run this code.
# This block should be right below the uuid
# import.
rd = random.Random()
uuid.uuid4 = lambda: uuid.UUID(int=rd.getrandbits(128))
# -------------------------------------------


def choose_font():
    operating_system = platform.system()

    if operating_system == "Darwin":
        font = "Gill Sans"
    elif operating_system == "Windows":
        font = "Candara"
    else:
        font = "Ubuntu"

    return font
