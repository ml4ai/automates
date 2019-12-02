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
from ... util.utils import remove_bad_chars

class PdfAlign():
    def __init__(self):
        self.dpi = 200
        # bounding boxes
        self.charid = 0
        self.page_boxes = dict(token=[], char=[])
        self.aabb_trees = None
        # The bounding box around the equation to be annotated
        self.annotation_aabb = None
        # The lookup for the token that corresponds to the bounding box
        self.all_tokens = []
        self.char_token_lut = dict()
        self.token_char_lut = defaultdict(list)

    def process(self, bytes=None):
        print("Converting PDF pages to images...")

        self.saved_annotations = []

        # We actually shouldnt have to convert pdf to images on backend ?
        # self.pages = convert_from_bytes(bytes, dpi=self.dpi)

        self.populate_bboxes(bytes)
        self.aabb_trees = dict(
            token=self.make_trees_from_boxes(self.page_boxes, "token"),
            char=self.make_trees_from_boxes(self.page_boxes, "char"),
        )

        # TODO resolve what we need to do for equation to annotate aabb creation
        # but for now, ignore this
        self.annotation_aabb = {}
        # Add the box around the equation to annotate
        # paper_dir, _ = os.path.split(self.filename)
        # aabb_file = os.path.join(paper_dir, "aabb.tsv")
        # with open(aabb_file) as aabb:
        #     line = aabb.readline()
        #     _, _, eqn_page, xmin, ymin, xmax, ymax = line.strip().split(
        #         "\t"
        #     )
        #     annotation_aabb = AABB(
        #         float(xmin), float(ymin), float(xmax), float(ymax)
        #     )
        #     annotation_aabb.page = int(eqn_page)
        #     self.annotation_aabb = annotation_aabb
        # self.num_page = self.annotation_aabb.page

    # ---------------------------------------
    #         Bounding Box Methods
    # ---------------------------------------
    # NOTE pdftotext -bbox-layout returns the bounding boxes of the first page only
    # so we need to split the paper into pages and call this for each page

    def retrieve_pdf_text(self, files_bytes):
        dpi = 72  # educated guess

        # This is a poor solution. Someday, call pdf2text directly from code
        # using bytes rather than writing to a a file and using that
        filename = "./temp-pdf.pdf"
        file = open(filename, 'wb')
        # files_bytes.save(file)
        file.write(files_bytes)
        file.close()

        command = ["pdf2txt.py", "-t", "xml", filename]
        result = subprocess.run(command, capture_output=True)

        # Remove the file that temporarily holds file bytes
        os.remove(filename)

        x = remove_bad_chars(result.stdout)
        tree = etree.fromstring(x)

        # For each page in XML, retrieve its page node
        max_page = 0
        pages = defaultdict()
        for node in tree.findall(".//page"):
            cur_page_height = float(node.attrib["bbox"].split(",")[3])
            max_page = int(node.attrib["id"])
            pages[max_page] = (node, cur_page_height)

        for i in range(1, max_page + 1):

            cur_page_meta = pages[i]
            cur_page_tree = cur_page_meta[0]
            page_height = cur_page_meta[1]
            curr_token_aabb = None
            char_boxes = []
            token_boxes = []

            # .//text
            # Create an annotation per text node in XML
            for node in cur_page_tree.findall(".//text"):
                text = node.text
                if text is not None:
                    if len(text.strip()) == 0 and curr_token_aabb is not None:
                        # The current token ended
                        curr_token_aabb.page = i
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
                            aabb.page = i
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
        self.retrieve_pdf_text(filename)
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

# def main():
#     file = open("../resources/temp.pdf", 'rb')
#     temp = PdfAlign()
#     temp.open(file.read())
#
# main()
