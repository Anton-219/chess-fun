# -*- coding: utf-8 -*-
"""
Created on Fri Dec  2 23:05:24 2022

@author: anton
"""

import json
from typing import Union

_c2n = {c : ord(c) - ord('a') for c in "abcdefgh"}

def c2n(c):
    return _c2n[c]

def n2c(n):
    return "abcdefgh"[n]

def chess_to_coord(c, i):
    return c2n(c), i-1

def coord_to_chess(x,y):
    return "abcdefgh"[x], y+1

def to_chess(x : Union[str, int], y: int):
    """Transforms the given coordinates to chess coordinates. This is done by checking if the x-coordinate is a string."""
    return (x,y) if isinstance(x, str) else coord_to_chess(x,y)

def to_coord(x : Union[str, int], y : int):
    """Transforms the given coordinates to normal coordinates. This is done by checking if the x-coordinate is a string."""
    return chess_to_coord(x, y) if isinstance(x, str) else (x,y)

def to_both_coord(x : Union[str, int], y : int):
    """Converts the given x and y coordinates to both coordinate systems: Chess and normal coordinates.

    Args:
        x (Union[str, int]): The x-coordinate of the position. Can be either a char or an integer. 
                If the position is a char it is assumed a chess coordinate is given (e.g. 'c', 4). 
                Otherwise it is assumed that is a normal coordinate.
        y (int): The y coordinate. The coordinate should be consistent with the choice of x.

    Returns:
        Tuple[Chess Position, Normal Position]: A tuple containing both coordinate types.
            The first part is the chess coordinate, the other the normal coordinat.
    """
    if isinstance(x, str):
        px, py = chess_to_coord(x, y)
        cx, cy = x, y 
    else: 
        px, py = x, y 
        cx, cy = coord_to_chess(x, y)
    return (cx, cy), (px, py)

def ls2chess(ls):
    return [to_chess(*pos) for pos in ls]

def get_json_file():
    with open('settings.json', 'r') as f:
        cdict = json.load(f)
    return cdict