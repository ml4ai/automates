from copy import deepcopy

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Point({self.x}, {self.y})"


class AABB:
    def __init__(self, xmin, ymin, xmax, ymax):
        # Position
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax
        self.width = self.xmax - self.xmin
        self.height = self.ymax - self.ymin
        self.area = self.width * self.height
        self.id = None

        # Content
        self.value = None
        self.font = None
        self.font_size = None

        # The corresponding token from pdfminer lines
        self.token = None
        self.tokenid = None

        # Synctex
        self.synctex = None

    def __repr__(self):
        return f"AABB({self.xmin}, {self.ymin}, {self.xmax}, {self.ymax})"

    def __hash__(self):
        return hash((self.xmin, self.ymin, self.xmax, self.ymax))

    def __eq__(self, other):
        return (
            self.xmin == other.xmin
            and self.ymin == other.ymin
            and self.xmax == other.xmax
            and self.ymax == other.ymax
        )

    # @property
    # def width(self):
    #     return self.xmax - self.xmin
    #
    # @property
    # def height(self):
    #     return self.ymax - self.ymin
    #
    # @property
    # def perimeter(self):
    #     return 2 * (self.width + self.height)

    def contains(self, point):
        return (
            self.xmin < point.x < self.xmax and self.ymin < point.y < self.ymax
        )

    def intersects(self, aabb):
        return (
            self.xmax > aabb.xmin
            and self.xmin < aabb.xmax
            and self.ymax > aabb.ymin
            and self.ymin < aabb.ymax
        )

    def character_click(self):
        return Point((self.xmax + self.xmin) / 2, (self.ymax - 0.01))

    @classmethod
    def merge(cls, aabb1, aabb2):
        xmin = min(aabb1.xmin, aabb2.xmin)
        ymin = min(aabb1.ymin, aabb2.ymin)
        xmax = max(aabb1.xmax, aabb2.xmax)
        ymax = max(aabb1.ymax, aabb2.ymax)
        return cls(xmin, ymin, xmax, ymax)

    def serialize_box(self):
        return dict(
            xmin=self.xmin,
            ymin=self.ymin,
            xmax=self.xmax,
            ymax=self.ymax,
            value=self.value,
            font=self.font,
            font_size=self.font_size,
            token=self.token,
            tokenid=self.tokenid,
            id=self.id,
            page=self.page,
            synctex=self.synctex,
        )

    @classmethod
    def deserialize_box(cls, box_dict):
        xmin = float(box_dict["xmin"])
        ymin = float(box_dict["ymin"])
        xmax = float(box_dict["xmax"])
        ymax = float(box_dict["ymax"])
        box = AABB(xmin=xmin, ymin=ymin, xmax=xmax, ymax=ymax)
        box.id = box_dict["id"]
        box.page = box_dict["page"]
        box.value = box_dict["value"]
        box.font = box_dict["font"]
        box.font_size = box_dict["font_size"]
        box.token = box_dict["token"]
        box.tokenid = box_dict["tokenid"]
        box.synctex = box_dict["synctex"]
        return box


class AABBTree:
    def __init__(self, aabb=None, left=None, right=None):
        self.aabb = aabb
        self.left = left
        self.right = right

    @classmethod
    def from_boxes(cls, boxes):
        tree = cls()
        for box in sorted(boxes, key=lambda box: box.area):
            tree.add(box)
        return tree

    # @property
    def is_empty(self):
        return self.aabb is None
    #
    # @property
    def is_leaf(self):
        return self.left is None and self.right is None
    #
    # @property
    # def depth(self):
    #     """Returns the tree depth"""
    #     # FIXME this is inefficient, don't compute it on-the-fly
    #     return (
    #         0 if self.is_leaf else 1 + max(self.left.depth, self.right.depth)
    #     )
    #
    # @property
    # def is_balanced(self):
    #     return self.is_leaf or abs(self.left.depth - self.right.depth) <= 1

    def add(self, aabb):
        """Add AABB leaf to the tree"""
        if self.is_empty():
            self.aabb = aabb
        elif self.is_leaf():
            # Set children
            self.left = deepcopy(self)
            self.right = AABBTree(aabb)
            # Set fat aabb
            self.aabb = AABB.merge(self.left.aabb, self.right.aabb)
        else:
            # Merged AABBs
            # Hypothetical area instead
            merged_self = AABB.merge(aabb, self.aabb)
            merged_left = AABB.merge(aabb, self.left.aabb)
            merged_right = AABB.merge(aabb, self.right.aabb)
            # Cost of creating a new parent for this node and the new leaf
            self_cost = 2 * merged_self.area
            # Minimum cost of pushing the leaf further down the tree
            inheritance_cost = 2 * (merged_self.area - self.aabb.area)
            # Cost of descending left
            left_cost = (
                merged_left.area - self.left.aabb.area + inheritance_cost
            )
            # Cost of descending right
            right_cost = (
                merged_right.area - self.right.aabb.area + inheritance_cost
            )
            # Descend
            if self_cost < left_cost and self_cost < right_cost:
                # Set children
                self.left = deepcopy(self)
                self.right = AABBTree(aabb)
            elif left_cost < right_cost:
                self.left.add(aabb)
            else:
                self.right.add(aabb)
            # Set fat aabb
            self.aabb = AABB.merge(self.left.aabb, self.right.aabb)

    def get_collisions(self, detect_collision):
        """Return collisions according to provided function"""
        collisions = []
        stack = [self]
        while stack:
            node = stack.pop()
            if node.is_empty():
                continue
            elif detect_collision(node):
                if node.is_leaf():
                    collisions.append(node.aabb)
                else:
                    if node.left is not None:
                        stack.append(node.left)
                    if node.right is not None:
                        stack.append(node.right)
        return collisions

    def contains(self, point):
        """Return AABBs that contain a given point"""

        def detect_collision(node):
            return node.aabb.contains(point)

        return self.get_collisions(detect_collision)

    def intersects(self, aabb):
        """Return AABBs that intersect a given AABB"""

        def detect_collision(node):
            return node.aabb.intersects(aabb)

        return self.get_collisions(detect_collision)
