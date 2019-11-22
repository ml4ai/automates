def remove_bad_chars(text):
    # NOTE 9 (tab), 10 (line feed), and 13 (carriage return) are not bad
    bad_codes = [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        11,
        12,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23,
        24,
        25,
        26,
        27,
        28,
        29,
        30,
        31,
    ]
    bad_chars = [chr(c) for c in bad_codes]
    bad_bytes = [bytes([c]) for c in bad_codes]
    if isinstance(text, bytes):
        for byte in bad_bytes:
            text = text.replace(byte, b"")
    elif isinstance(text, str):
        for char in bad_chars:
            text = text.replace(char, "")
    return text
