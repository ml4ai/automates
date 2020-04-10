import json
import csv
import sys


def main():
    svo_data = json.load(open(sys.argv[1], "r"))
    groundings = svo_data["groundings"]

    mention_to_svo_rows = list()
    for data in groundings:
        mention = data["variable"]
        for g_dict in data["groundings"]:
            scores = g_dict["score"]
            link_score = scores[0] if len(scores) > 0 else -1
            mention_to_svo_rows.append(
                (
                    round(link_score, ndigits=4),
                    mention,
                    g_dict["searchTerm"],
                    g_dict["osvTerm"],
                    g_dict["className"],
                )
            )
    mention_to_svo_rows.sort(reverse=True)
    with open(sys.argv[2], "w", newline="") as csvfile:
        svo_writer = csv.writer(csvfile, dialect="excel")
        svo_writer.writerow(
            ["Score", "Mention", "Search term", "OSV term", "Class name"]
        )
        for row in mention_to_svo_rows:
            svo_writer.writerow(row)


if __name__ == "__main__":
    main()
