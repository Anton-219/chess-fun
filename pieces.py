# -*- coding: utf-8 -*-
"""
Created on Thu Nov 24 20:26:50 2022

@author: anton
"""

from typing import Dict, List, Tuple, TypeVar
import copy

from misc import chess_to_coord, coord_to_chess, ls2chess

Position = TypeVar('Position')


RAN8 = range(8) # evaluate this now for a little bit faster code.

# Get the list of all valid directions.
# It is based on the idea of https://stackoverflow.com/a/65637922
positions = [(c, r) for c in RAN8 for r in RAN8]
direction = dict()

def valid(poss):
    """Filters out the not valid positions in poss. That is, the positions which are not on the board."""
    return [(c, r) for c, r in poss if c in RAN8 and r in RAN8]

# Get all the possible base directions
direction['up'] = {(c, r): valid((c, r+v) for v in RAN8[1:])
                   for c, r in positions}
direction['down'] = {(c, r): valid((c, r-v) for v in RAN8[1:])
                     for c, r in positions}
direction['right'] = {(c, r): valid((c+v, r)
                                    for v in RAN8[1:]) for c, r in positions}
direction['left'] = {(c, r): valid((c-v, r) for v in RAN8[1:])
                     for c, r in positions}
direction['upleft'] = {(c, r): valid((c_, r_) for (_, r_), (c_, _) in zip(
    direction['up'][c, r], direction['left'][c, r])) for c, r in positions}
direction['downleft'] = {(c, r): valid((c_, r_) for (_, r_), (c_, _) in zip(
    direction['down'][c, r], direction['left'][c, r])) for c, r in positions}
direction['upright'] = {(c, r): valid((c_, r_) for (_, r_), (c_, _) in zip(
    direction['up'][c, r], direction['right'][c, r])) for c, r in positions}
direction['downright'] = {(c, r): valid((c_, r_) for (_, r_), (c_, _) in zip(
    direction['down'][c, r], direction['right'][c, r])) for c, r in positions}
MOVES = dict()
# moves of king
MOVES['K'] = {(c, r): [valid([(c+v, r+h)]) for v in (-1, 0, 1)
                       for h in (-1, 0, 1) if v != 0 or h != 0] for c, r in positions}
# moves of rook
MOVES['R'] = {(c, r): [direction['up'][c, r], direction['right'][c, r],
                       direction['down'][c, r], direction['left'][c, r]] for c, r in positions}
# moves of bishop
MOVES['B'] = {(c, r): [direction['upleft'][c, r], direction['upright'][c, r],
                       direction['downright'][c, r], direction['downleft'][c, r]] for c, r in positions}
# moves of queen
MOVES['Q'] = {(c, r): MOVES['R'][c, r] + MOVES['B'][c, r]
              for c, r in positions}
# moves of knight
MOVES['Kn'] = {(c, r): [valid([(c+v, r+h)]) for v, h in [(2, 1), (2, -1), (1, 2),
                                                      (1, -2), (-2, 1), (-2, -1), (-1, 2), (-1, -2)]] for c, r in positions}
# moves of white pawn
MOVES['wP'] = {(c, r): [valid([(c, r+1)])*(r < 7), [(c, r+2)]*(r == 1)]
               for c, r in positions}
# moves of black pawn
MOVES['bP'] = {(c, r): [valid([(c, r-1)])*(r > 0), [(c, r-2)]*(r == 6)]
               for c, r in positions}
# moves of white pawn take
MOVES['wPtake'] = {(c, r): valid([(c+1, r+1), (c-1, r+1)]*(r > 0))
                   for r, c in positions}
# moves of black pawn take
MOVES['bPtake'] = {(c, r): valid([(c+1, r-1), (c-1, r-1)]*(r < 7))
                   for r, c in positions}

# TODO Castle


class Team:
    def __init__(self, team):
        if not isinstance(team, Team):
            assert team in (
                'w', 'b'), "team should be w (for white) or b (for black)."
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
    
    def __hash__(self) -> int:
        return hash(self.team)
    
    def __invert__ (self):
        return Team('w') if self.team == 'b' else Team('b')


class Piece:
    """Implementation class for a chess piece.
    """

    def __init__(self, team, id, position: Position) -> None:
        self.team: Team = team
        self.id: str = id
        self.position: Position = position
        self.move_set: Dict[Position, List[Position]] = None

    def __repr__(self) -> str:
        return f"{type(self).__name__}(team={self.team}, position={self.position})"

    def __str__(self) -> str:
        return f"{self.team}{self.id}"

    def _def_move_set(self, id):
        self.move_set = MOVES[id]
        return self.move_set

    def __eq__(self, __o: object) -> bool:
        """Two pieces are the same if they are on the same position, have the same id (= chess piece) and are on the same team"""
        return isinstance(__o, self.__class__) and (self.id == __o.id and self.position == __o.position and self.team == __o.team)
    
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

    def available_moves(self, pieces):
        moves = set()
        # Check each direction
        for ms in self.move_set[self.position]:
            midx = len(ms)
            pot_enemy = None
            sms = set(ms)
            for pos in pieces:
                piece = pieces[pos]
                if piece == self:
                    continue
                if pos in sms:
                    idx = ms.index(pos)
                    if idx < midx:
                        midx = idx
                        # if piece.team != self.team:
                        #     pot_enemy = piece
                        # else:
                        #     pot_enemy = None
            # if pot_enemy is not None:
            #     midx += 1
            moves.update(ms[:midx+1])

    def danger_zone(self, pieces, calc_move = False):
        """Returns the positions to which this piece can move, that is, all positions that are threatened.
        A dictionary of pieces must be given and a set of positions is returned.
        A pin is not considered into this as this is mainly interesting for checks.
        
        Note that the enemy team king is ignored for the danger aspect as the king is not able to 
        protect anything.

        Args:
            pieces (Dict[Position, Piece]): _description_

        Returns:
            Set[Position]: The part of the board reached by the influence of the current piece. 
        """
        influence_zone = set()
        # Check each direction
        for ms in self.move_set[self.position]:
            if len(ms) == 0:
                continue
            # iidx = len(ms)
            # sms = set(ms)
            # for pos in pieces:
            #     piece = pieces[pos]
            #     if piece == self:
            #         continue
            #     # Check if the position is a move and if the current piece is an enemy king. 
            #     # If the piece is an enemy king the danger zone goes beyond it as the king should not move in this direction. 
            #     # If the moves should be calculated than the king should not be ignored.
            #     if pos in sms and not (isinstance(piece, King) and piece.team != self.team):
            #         idx = ms.index(pos)
            #         if idx < iidx:
            #             iidx = idx
            # I think this code should be faster.
            iidx = 0
            for i, m in enumerate(ms): 
                iidx = i
                piece = pieces.get(m)
                if piece is not None:
                    if calc_move:
                        break
                    if not (isinstance(piece, King) and piece.team != self.team):
                        # Ignore the enemy king when calculating the damage zone. 
                        continue 
                    
                # if not (piece is None or (isinstance(piece, King) and piece.team != self.team)): 
                #     break
            influence_zone.update(ms[:iidx+1])
        return influence_zone
    
    def get_moves(self, pieces):
        return {pos for pos in self.danger_zone(pieces) if pieces.get(pos) is None or pieces[pos].team != self.team}
    
    # def get_legal_moves(self, pieces):
    #     """Returns all legal moves available for this piece based on the pieces which are given. 
    #     The pieces should be given as a dictionary where the positions are the keys and the pieces the values.
    #     Note that this collection is not proof checked. 
    #     A tuple of two lists is returned. 
    #     The first part is a list of all available legal moves.
    #     The second is a list of enemy pieces which the current piece is available to take. 

    #     Args:
    #         pieces (Dict[Position, Piece]): The dictionary of available pieces on the board.

    #     Returns:
    #          Tuple[List[Position], List[Piece]]: Two lists: a list of available moves and a list of enemy pieces.
    #     """
    #     legal_moves = []
    #     enemies = []
    #     # Check each direction
    #     for ms in self.move_set[self.position]:
    #         midx = len(ms)
    #         pot_enemy = None
    #         sms = set(ms)
    #         # TODO Schau mal ob es andersherum geht: for m in ms statt das da unten.
    #         for pos in pieces:
    #             piece = pieces[pos]
    #             if piece == self:
    #                 continue
    #             if pos in sms:
    #                 idx = ms.index(pos)
    #                 if idx < midx:
    #                     midx = idx
    #                     if piece.team != self.team:
    #                         pot_enemy = piece
    #                     else:
    #                         pot_enemy = None
    #         legal_moves.append(ms[:midx])
    #         if pot_enemy is not None:
    #             enemies.append(pot_enemy)
    #     return legal_moves, enemies
    
    def clegal_moves(self, pieces):
        lmoves, enemies = self.get_legal_moves(pieces)
        return ls2chess(lm for lm in lmoves), enemies
    
    def sdanger_zone(self, pieces):
        dng = self.danger_zone(pieces)
        return {coord_to_chess(*pos) for pos in dng}
    
    def cpos(self):
        return coord_to_chess(*self.position)


class King(Piece):
    # TODO Castle.
    def __init__(self, team: str, position: Tuple[int, int] = None) -> None:
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

    # def move_set(self, position):
    #     pass

class Queen(Piece):
    def __init__(self, team: str, position: Tuple[int, int]) -> None:
        super().__init__(Team(team), 'Q', position)
        self.move_set = self._def_move_set(self.id)

        self.icon_text = '\u2655' if team == 'w' else '\u265B'

class Rook(Piece):

    def __init__(self, team: str, position: Tuple[int, int]) -> None:
        super().__init__(Team(team), 'R', position)
        self.move_set = self._def_move_set(self.id)

        self.icon_text = '\u2656' if team == 'w' else '\u265C'

class Bishop(Piece):

    def __init__(self, team: str, position: Tuple[int, int]) -> None:
        super().__init__(Team(team), 'B', position)
        self.move_set = self._def_move_set(self.id)

        self.icon_text = '\u2657' if team == 'w' else '\u265D'


class Knight(Piece):

    def __init__(self, team: str, position: Tuple[int, int]) -> None:
        super().__init__(Team(team), 'Kn', position)
        self.move_set = self._def_move_set(self.id)

        self.icon_text = '\u2658' if team == 'w' else '\u265E'


class Pawn(Piece):

    def __init__(self, team: str, position: Tuple[int, int]) -> None:
        super().__init__(Team(team), 'P', position)
        self.move_set = self._def_move_set(f"{team}{self.id}")

        self.icon_text = '\u2659' if team == 'w' else '\u265F'
        
    def danger_zone(self, pieces):
        """Generates the danger zone of the pawn as it has a rather unique set of movements.
        TODO En passant.

        Args:
            pieces (Dict[Position, Piece]): A dictionary containing positions and pieces

        Returns:
            Set[Position]: A set of possible positions this piece can attack.
        """
        dzone = set(MOVES[f"{self.team}{self.id}take"][self.position])
        return dzone
    
    def get_moves(self, pieces):
        dzone = self.danger_zone(pieces)
        for ms in self.move_set[self.position]:
            for m in ms: 
                piece = pieces.get(m)
                if piece is None: 
                    dzone.add(m)
        return dzone
            

