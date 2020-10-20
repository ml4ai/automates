import requests
import json
import sys


def main():
    eqn_pic_path = sys.argv[1]
    filename = eqn_pic_path[
        eqn_pic_path.rfind("/") + 1 : eqn_pic_path.rfind(".png")
    ]
    decoded_output_path = f"{sys.argv[2]}/{filename}.json"

    res = requests.post(
        "http://localhost:8000/decode_equation/",
        files={"file": (eqn_pic_path, open(eqn_pic_path, "rb"), "image/png")},
    )

    data = res.json()
    print(data)
    json.dump(data, open(decoded_output_path, "w"))


if __name__ == "__main__":
    main()
