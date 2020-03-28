import requests
import json
import sys


def main():
    eqn_pic_path = sys.argv[1]
    decoded_output_path = sys.argv[2]

    res = requests.post(
        "http://localhost:8000/decode_equation/",
        files={"file": (eqn_pic_path, open(eqn_pic_path, "rb"), "image/png")},
    )

    data = res.json()
    print(data)
    json.dump(data, open(decoded_output_path, "w"))


if __name__ == "__main__":
    main()
