# -*- coding: utf-8 -*-
"""
Created on Thu Nov 24 20:26:50 2022

@author: anton
"""

from typing import Dict, List, Tuple, TypeVar
import copy

# import board

Position = TypeVar('Position')


RAN8 = range(8)

positions = [(c,r) for c in RAN8 for r in RAN8]
direction = dict()
def valid(poss):
    """Filters out the not valid positions in poss. That is, the positions which are not on the board."""
    return [(c,r) for c, r in poss if c in RAN8 and r in RAN8]
# Get all the possible base directions
direction['up'] = {(c,r) : valid((c, r+v) for v in RAN8[1:]) for c,r in positions}
direction['down'] = {(c,r) : valid((c, r-v) for v in RAN8[1:]) for c,r in positions}
direction['right'] = {(c,r) : valid((c+v, r) for v in RAN8[1:]) for c,r in positions}
direction['left'] = {(c,r) : valid((c-v, r) for v in RAN8[1:]) for c,r in positions}

direction['upleft'] = {(c,r) : valid((c_, r_) for (_, r_), (c_, _) in zip(direction['up'][c,r], direction['left'][c,r])) for c,r in positions}
direction['downleft'] = {(c,r) : valid((c_, r_) for (_, r_), (c_, _) in zip(direction['down'][c,r], direction['left'][c,r])) for c,r in positions}
direction['upright'] = {(c,r) : valid((c_, r_) for (_, r_), (c_, _) in zip(direction['up'][c,r], direction['right'][c,r])) for c,r in positions}
direction['downright'] = {(c,r) : valid((c_, r_) for (_, r_), (c_, _) in zip(direction['down'][c,r], direction['right'][c,r])) for c,r in positions}

MOVES = dict()
# moves of king
MOVES['K'] = {(c,r) : [[valid([(c+v, r+h)])] for v in (-1,0,1) for h in (-1,0,1) if v != 0 or h != 0] for c,r in positions}
# moves of rook
MOVES['R'] = {(c,r) : [direction['up'][c,r], direction['right'][c,r], direction['down'][c,r], direction['left'][c,r]] for c,r in positions}
# moves of bishop
MOVES['B'] = {(c,r) : [direction['upleft'][c,r], direction['upright'][c,r], direction['downright'][c,r], direction['downleft'][c,r]] for c,r in positions}
# moves of queen
MOVES['Q'] = {(c,r) : MOVES['R'][c,r] + MOVES['B'][c,r] for c,r in positions}
# moves of knight
MOVES['Kn'] = {(c,r) : [valid((r+h,c+v) for v,h in [(2,1),(2,-1),(1,2),(1,-2),(-2,1),(-2,-1),(-1,2),(-1,-2)])] for c,r in positions}
# moves of white pawn
MOVES['wP'] = {(c,r) : [valid([(c, r+1)])*(r<7), [(c,r+2)]*(r==1)] for c,r in positions}
# moves of black pawn
MOVES['bP'] = {(c,r) : [valid([(c, r-1)])*(r>0), [(c,r-2)]*(r==6)] for c,r in positions}

# moves of white pawn take
MOVES['wPtake'] = {(c,r) : valid([(c+1, r+1), (c-1, r+1)]*(r>0)) for r,c in positions}
# moves of black pawn take
MOVES['wPtake'] = {(c,r) : valid([(c+1, r-1), (c-1, r-1)]*(r<7)) for r,c in positions}

# TODO Castle

class Team: 
    def __init__(self, team): 
        assert team in ('w', 'b'), "team should be w (for white) or b (for black)."
        self.team = team

    def __eq__(self, __o: object) -> bool:
        return isinstance(__o, Team) and self.team == __o.team

    def other_team(self): 
        """Returns the other team of the given team
        """
        c = 'w' if self.team == 'b' else 'b'
        return Team(c)

    def __repr__(self) -> str:
        return f"Team('{self.team}')"
    
    def __str__(self) -> str:
        return str(self.team)

class Piece:
    """Implementation class for a chess piece.
    """
    def __init__(self, team, id, position : Position) -> None:
        self.team : Team = team 
        self.id : str = id
        self.position : Position = position
        self.move_set : Dict[Position, List[Position]] = None

    def __repr__(self) -> str:
        return f"{type(self).__name__}(team={self.team}, position={self.position})"
    
    def __str__(self) -> str:
        return f"{self.team}{self.id}"

    def _def_move_set(self, id):
        self.move_set = MOVES[id]
        return self.move_set

    def __eq__(self, __o: object) -> bool:
        """Two pieces are the same if they are on the same position, have the same id (= chess piece) and are on the same team"""
        return isinstance(__o, Piece) and (self.id == __o.id and self.position == __o.position and self.team == __o.team)

    def set_position(self, position): 
        """Sets a new position of the piece. 
        Checks if the position is valid. It should be a coordinate. That is (7,7) instead of ('h', 8)

        Args:
            position (Position): A position which the piece should take. Trows an error if the position is not valid.
        """
        if len(valid([position])) != 1:
            raise ValueError(f"position is not valid, {position=}.")
        self.position = position

    def destroy(self):
        """Removes the piece by setting the position to None"""
        self.team = None 
        self.position = None 
        

    def get_legal_moves(self, pieces): 
        """Returns all legal moves available for this piece based on the list of pieces which are given. 
        The list is not proof checked. 
        A tuple of two lists is returned. 
        First a list of all available legal moves is returned.
        Then a list of enemy pieces is returned which the current piece can take.

        Args:
            pieces (List[Piece]): The list of available pieces on the board.

        Returns:
             Tuple[List[Position], List[Piece]]: Two lists: a list of available moves and a list of enemy pieces.
        """
        legal_moves = []
        enemies = []
        # Check each direction
        for ms in self.move_set[self.position]:
            midx = len(ms)
            pot_enemy = None
            for piece in pieces: 
                # if piece == 0:
                #     continue
                if piece == self:
                    continue
                # Check for a faster way to do this (try except might be a bit slow.)
                try: 
                    idx = ms.index(piece.position)
                    if idx < midx: 
                        midx = idx
                        if piece.team != self.team:
                            pot_enemy = piece
                        else: 
                            pot_enemy = None
                except ValueError: 
                    continue
            legal_moves.append(ms[:midx])
            if pot_enemy is not None: 
                enemies.append(pot_enemy)
        return legal_moves, enemies
            
class King(Piece):
    def __init__(self, team : str, position : Tuple[int, int] = None) -> None:
        if position is None: 
            if self.team == 'w': 
                position = (0, 4)
            else: 
                position = (7, 4)
        self.position = position
        super().__init__(Team(team), 'K', position)

        self.moved = False
        self.move_set = self._def_move_set(self.id)
        
        self.icon_text = '\u2654' if team == 'w' else '\u265A'

    def move_set(self, position):
        pass

class Queen(Piece):
    def __init__(self, team : str, position : Tuple[int, int] = None) -> None:
        if position is None: 
            if self.team == 'w': 
                position = (0, 3)
            else: 
                position = (7, 3)
        super().__init__(Team(team), 'Q', position)
        self.move_set = self._def_move_set(self.id)
        
        self.icon_text = '\u2655' if team == 'w' else '\u265B'
    
class Rook(Piece):

    def __init__(self, team : str, position : Tuple[int, int]) -> None:
        super().__init__(Team(team), 'R', position)
        self.move_set = self._def_move_set(self.id)
        
        self.icon_text = '\u2656' if team == 'w' else '\u265C'

class Bishop(Piece):

    def __init__(self, team : str, position : Tuple[int, int]) -> None:
        super().__init__(Team(team), 'B', position)
        self.move_set = self._def_move_set(self.id)
        
        self.icon_text = '\u2657' if team == 'w' else '\u265D'

class Knight(Piece):

    def __init__(self, team : str, position : Tuple[int, int]) -> None:
        super().__init__(Team(team), 'Kn', position)
        self.move_set = self._def_move_set(self.id)
        
        self.icon_text = '\u2658' if team == 'w' else '\u265E'

class Pawn(Piece):

    def __init__(self, team : str, position : Tuple[int, int]) -> None:
        super().__init__(Team(team), 'P', position)
        self.move_set = self._def_move_set(f"{team}{self.id}")
        
        self.icon_text = '\u2659' if team == 'w' else '\u265F'