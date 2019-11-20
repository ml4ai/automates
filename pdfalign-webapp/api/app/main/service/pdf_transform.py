import os
import json
import subprocess
from collections import defaultdict
from tkinter import *
from tkinter import ttk
from tkinter.ttk import Button, Frame, Scrollbar, Radiobutton
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from pdf2image import convert_from_path, convert_from_bytes
from lxml import etree
from webcolors import name_to_rgb
from tqdm import tqdm

from .aabb_tree import AABB, AABBTree

class PdfAlign():
    def __init__(self):
        # super().__init__(master)
        # self.master.title("pdfalign")
        # self.pack(expand=YES, fill=BOTH)

        self.dpi = 200
        self.scale = 1.0
        self.num_page = 0
        # bounding boxes
        self.charid = 0
        self.page_boxes = dict(token=[], char=[])
        self.aabb_trees = None
        # The bounding box around the equation to be annotated
        self.annotation_aabb = None
        # Holder to display the transparent rectangles
        self.rectangles = []
        # History
        self.history_boxes = []
        # The lookup for the token that corresponds to the bounding box
        self.all_tokens = []
        self.char_token_lut = dict()
        self.token_char_lut = defaultdict(list)

    def open(self, bytes=None):
        # if filename is None:
        #     filename = filedialog.askopenfilename(
        #         filetypes=[("pdf files", "*.pdf"), ("all files", "*.*")]
        #     )
        # if filename != "":
        self.saved_annotations = []

        filename = "/Users/daniel/Documents/dev/research/automates/pdfalign-webapp/api/app/main/resources/test"
        self.filename = os.path.abspath(filename)
        print("Converting PDF pages to images...")

        self.pages = convert_from_bytes(bytes, dpi=self.dpi)
        # self.pages = convert_from_path(filename, dpi=self.dpi)

        self.populate_bboxes(filename)
        self.aabb_trees = dict(
            token=self.make_trees_from_boxes(self.page_boxes, "token"),
            char=self.make_trees_from_boxes(self.page_boxes, "char"),
        )
        self.num_page = 0

        # Add the box around the equation to annotate
        paper_dir, _ = os.path.split(self.filename)
        aabb_file = os.path.join(paper_dir, "aabb.tsv")
        with open(aabb_file) as aabb:
            line = aabb.readline()
            _, _, eqn_page, xmin, ymin, xmax, ymax = line.strip().split(
                "\t"
            )
            annotation_aabb = AABB(
                float(xmin), float(ymin), float(xmax), float(ymax)
            )
            annotation_aabb.page = int(eqn_page)
            self.annotation_aabb = annotation_aabb
        self.num_page = self.annotation_aabb.page
            # self.redraw()

    # ---------------------------------------
    #         Bounding Box Methods
    # ---------------------------------------
    # NOTE pdftotext -bbox-layout returns the bounding boxes of the first page only
    # so we need to split the paper into pages and call this for each page

    def populate_page_bboxes(self, filename, page):
        dpi = 72  # educated guess
        command = ["pdf2txt.py", "-t", "xml", filename]
        result = subprocess.run(command, capture_output=True)
        x = remove_bad_chars(result.stdout)
        tree = etree.fromstring(x)
        page_height = None
        curr_token_aabb = None
        char_boxes = []
        token_boxes = []

        for node in tree.findall(".//page"):
            page_height = float(node.attrib["bbox"].split(",")[3])
        # .//text
        for node in tree.findall(".//text"):
            text = node.text
            if text is not None:
                if len(text.strip()) == 0 and curr_token_aabb is not None:
                    # The current token ended
                    curr_token_aabb.page = page
                    curr_token_aabb.id = len(self.all_tokens)
                    self.all_tokens.append(curr_token_aabb)
                    token_boxes.append(curr_token_aabb)
                    curr_token_aabb = None

                else:
                    # "576.926,76.722,581.357,86.733"
                    bbox = node.attrib.get("bbox")
                    if bbox is not None:
                        # The bboxes from pdf2txt are a little diff:
                        # per https://github.com/euske/pdfminer/issues/171
                        # The bbox value is (x0,y0,x1,y1).
                        # x0: the distance from the left of the page to the left edge of the box.
                        # y0: the distance from the bottom of the page to the lower edge of the box.
                        # x1: the distance from the left of the page to the right edge of the box.
                        # y1: the distance from the bottom of the page to the upper edge of the box.
                        # so here we flip the ys
                        xmin, ymax, xmax, ymin = [
                            float(x) for x in bbox.split(",")
                        ]
                        xmin /= dpi
                        ymin = (page_height - ymin) / dpi
                        xmax /= dpi
                        ymax = (page_height - ymax) / dpi
                        aabb = AABB(xmin, ymin, xmax, ymax)
                        # Store metadata
                        aabb.value = text
                        aabb.page = page
                        aabb.font = node.attrib.get("font")
                        aabb.font_size = node.attrib.get("size")
                        # Token info
                        if curr_token_aabb is None:
                            curr_token_aabb = AABB(xmin, ymin, xmax, ymax)
                            curr_token_aabb.value = text
                        else:
                            new_value = curr_token_aabb.value + text
                            curr_token_aabb = AABB.merge(curr_token_aabb, aabb)
                            curr_token_aabb.value = new_value
                        aabb.tokenid = len(self.all_tokens)
                        aabb.id = self.charid
                        self.charid += 1
                        # Update the bbox luts
                        self.char_token_lut[aabb] = aabb.tokenid
                        self.token_char_lut[aabb.tokenid].append(aabb)
                        # Add the current box
                        char_boxes.append(aabb)
        self.page_boxes["token"].append(token_boxes)
        self.page_boxes["char"].append(char_boxes)

    def populate_bboxes(self, filename):
        for i, p in enumerate(
            tqdm(
                split_pages(filename),
                desc="Populating page bboxes",
                unit="page",
                ncols=80,
            )
        ):
            self.populate_page_bboxes(p, i)
        for page in self.page_boxes["char"]:
            for box in page:
                box.token = self.all_tokens[box.tokenid].value

    def make_trees_from_boxes(self, page_boxes, box_type):
        return [
            AABBTree.from_boxes(page)
            for page in tqdm(
                page_boxes[box_type],
                desc=f"Making binary trees from {box_type} boxes",
                unit="page",
                ncols=80,
            )
        ]

def split_pages(filename):
    print(f"Separating pages for file {filename}")
    dirname = os.path.dirname(filename)
    page_pattern = os.path.join(dirname, "page-%03d.pdf")
    command = ["pdfseparate", filename, page_pattern]
    subprocess.run(command)
    pages = [
        os.path.join(dirname, f)
        for f in os.listdir(dirname)
        if re.search(r"page-\d+\.pdf$", f)
    ]
    return sorted(pages)

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


# def main():
#     file = open("../resources/temp.pdf", 'rb')
#     temp = PdfAlign()
#     temp.open(file.read())
#
# main()
