# -*- coding: utf-8 -*-
"""
Created on Thu Nov 24 20:10:32 2022

@author: anton
"""

from typing import List, Tuple
import json

import matplotlib.pyplot as plt
import numpy as np

import pieces


_c2n = {c : ord(c) - ord('a') for c in "abcdefgh"}
RAN8 = range(8)

def c2n(c):
    return _c2n[c]

def n2c(n):
    return "abcdefgh"[n]

def chess_to_coord(c, i):
    return c2n(c), i-1

def coord_to_chess(x,y):
    return "abcdefgh"[x], y+1

class Board:
    """Defines the board of the chess game.
    Additionally, this defines all valid directions.

    The list of valid directions is based on the idea of https://stackoverflow.com/a/65637922
    """
    def __init__(self, board = None) -> None:
        # TODO Check if board and piece_table can be combined.
        self.board = np.zeros((8,8), dtype = pieces.Piece)
        if board is not None:
            self.board[:] = board
        # self.piece_table = {(c,r) : 0 for c in RAN8 for r in RAN8}
        self.piece_table = dict()

    def __getitem__(self, pos) -> pieces.Piece:
        col, row = chess_to_coord(*pos)
        return self.board[col, row]
        # # return self.board[pos]
        # col, row = pos 
        # if not (0 <= row <= 7):
        #     raise ValueError(f"Only values in [0,1,2,3,4,5,6,7] for the row are allowed, but {pos=}.")
        # if isinstance(col, str):
        #     col = c2n(col)
        # if not (0 <= col <= 7):
        #     raise ValueError(f"Only values in [0,1,2,3,4,5,6,7] or in 'abcdefgh' for the column are allowed, but {pos=}.")
        # return self.board[col, row-1]

    def __setitem__(self, pos, val) -> pieces.Piece:
        # TODO Combine this with piece_table
        # # self.board[pos] = val
        # col, row = pos 
        # if not (1 <= row <= 8):
        #     raise ValueError(f"Only values in [1,2,3,4,5,6,7,8] for the row are allowed, but {pos=}.")
        # if isinstance(col, str):
        #     col = c2n(col)
        # if not (0 <= col <= 7):
        #     raise ValueError(f"Only values in [0,1,2,3,4,5,6,7] or in 'abcdefgh' for the column are allowed, but {pos=}.")
        col, row = chess_to_coord(*pos)
        if self.board[col, row] != 0: 
            raise ValueError(f"On {pos=} is already '{self.board[col, row]}'. Use move instead.")
        self.board[col, row] = val

    def __repr__(self) -> str:
        return f"Board({repr(self.board)})"

    def __str__(self) -> str:
        # TODO. Not hübsch.
        board = np.zeros_like(self.board, dtype=object)
        for i in RAN8: 
            for j in RAN8: 
                if self.board[i,j] != 0:
                    board[i,j] = str(self.board[i,j])
                else: 
                    board[i,j] = ""
        return str(board)

    def get_pieces(self) -> List[pieces.Piece]:
        """Returns an iterable of the present pieces on the table."""
        return self.piece_table.values()

    def get_board(self) -> str: 
        return self.board

    def is_free(self, pos) -> bool:
        return self[pos] == 0 

    def is_enemy(self, pos, team) -> bool: 
        return self[pos].team != team

    def move(self, piece : pieces.Piece, new_position : pieces.Position):
        """Moves the piece to the new position. It is not checked whether the new_position is a legal move.
        If on the new position is another piece it is removed from the list of pieces.

        The position should be given in chess coordinates. That is, e.g. ('h', 8) instead of (7,7).
        """
        # for p in self.list_of_pieces_on_board: 
        #     if p.position == new_position: 
        #         piece.position = new_position
        #         break
        npos = chess_to_coord(new_position)
        piece.set_position(new_position)
        if self.piece_table.get(npos) is not None: 
            self.piece_table[npos].destroy()
        self.piece_table[npos] = piece
        self[npos] = piece

    def plot_chessboard(self, highlighted = None):
        """Plots the chessboard with the current pieces.
        If highlighted is given then these fields are also depicted with the highlighted color.

        Args:
            highlighted (_type_, optional): A list of highlighted fields. Defaults to None.
        """
        
        # Declare color values
        with open('values.json', 'r') as f:
            cdict = json.load(f)
        cBlack = cdict['colors']['black_field']
        cWhite = cdict['colors']['white_field']
        cHighlight = cdict['colors']['highlighted']

        cBPiece = np.array(cdict['colors']['black_pieces'])/255
        cWPiece = np.array(cdict['colors']['white_pieces'])/255
        
        fig, ax = plt.subplots(1,1)
        res = np.add.outer(range(8), range(8)) %2 
        
        if highlighted is not None: 
            for h in highlighted: 
                hy, hx = h 
                hx = 7- hx
                res[hx, hy] = 2
                

        img = np.zeros((8,8,3))
        img[res == 0] = cWhite
        img[res == 1] = cBlack 
        img[res == 2] = cHighlight 
        img/= 255
        ax.imshow(img)

        ax.set_xticks([i-1 for i in range(1,9)])
        ax.set_yticks([i-2 for i in range(9,1, -1)])
        
        ax.set_xticklabels(list("abcdefgh"))
        ax.set_yticklabels([i for i in range(1,9)])

        for k in self.piece_table:
            piece = self.piece_table[k]
            x,y = piece.position
            y = 7 - y
            x -= 0.45
            y += 0.33
            ax.text(x, y, piece.icon_text, color = cBPiece if piece.team =='b' else cWPiece,
                    fontsize=26)

        fig.suptitle("Chess Board") 
        # plt.show()

    def init_board(self): 
        """Initializes the chess board by placing all the pieces on the board.
        """
        # initialize pawns
        for c in "abcdefgh":
            self[c, 2] = pieces.Pawn('w', chess_to_coord(c, 2))
            self[c, 7] = pieces.Pawn('b', chess_to_coord(c, 7))
        
        # initialize the other pieces
        for i, c in ((1, 'w'), (8, 'b')):
            self['a', i] = pieces.Rook(c, chess_to_coord('a', i))
            self['b', i] = pieces.Knight(c, chess_to_coord('b', i))
            self['c', i] = pieces.Bishop(c, chess_to_coord('c', i))
            self['d', i] = pieces.Queen(c, chess_to_coord('d', i))
            self['e', i] = pieces.King(c, chess_to_coord('e', i))
            self['f', i] = pieces.Bishop(c, chess_to_coord('f', i))
            self['g', i] = pieces.Knight(c, chess_to_coord('g', i))
            self['h', i] = pieces.Rook(c, chess_to_coord('h', i))

        # intialize the piece table dictionary.
        for ch in "abcdefgh":
            self.piece_table[chess_to_coord(ch, 1)] = self[ch, 1]
            self.piece_table[chess_to_coord(ch, 8)] = self[ch, 8]
            self.piece_table[chess_to_coord(ch, 2)] = self[ch, 2]
            self.piece_table[chess_to_coord(ch, 7)] = self[ch, 7]


        self['c', 4] = pieces.Queen('b', chess_to_coord('c', 4))
        self.piece_table[chess_to_coord('c', 4)] = self['c', 4] 
        

b = Board()
# print(b)
b.init_board()
# print(b)
r = b.piece_table[0,0]
r.get_legal_moves(b.get_pieces())
# r = b.list_of_pieces_on_board[0]
# pawn1 = pieces[1]
# pawn1.get_legal_moves(pieces)
# q1 = pieces[2]
# print(repr(q1.get_legal_moves(pieces)))

# [[coord_to_chess(*l) for l in l_] for l_ in q1.get_legal_moves(pieces)[0]]
q1 = b.piece_table[chess_to_coord('c', 4)]
_, enmy = q1.get_legal_moves(b.get_pieces())
b.plot_chessboard(highlighted=[p.position for p in enmy])