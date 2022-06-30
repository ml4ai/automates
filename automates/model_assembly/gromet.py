from typing import List, Dict, Iterable, Set, Any, Tuple
from abc import ABC, abstractmethod 
from functools import singledispatch
from dataclasses import dataclass 
from copy import deepcopy 

import datetime 
import json 
import re
import os 


primitive_ops = {}


class GrometFN():
    pass

    @classmethod 
    def from_dict(cls, data: dict):
        return None

    def to_dict(self) -> dict:
        return {}


class GrometExpression():
    pass