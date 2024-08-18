"""
This class is responsible for storing all the information about the current state of a chess game. It will also be responsible for determining the valid moves at the current state. It will also keep a move log.
"""

class GameState():
    def __init__(self):
        # The board is an 8x8 2d list, each element of the list has 2 characters.
        # The first character represents the color of the piece, 'b' or 'w'
        # The second character represents the type of the piece, 'K', 'Q', 'R', 'N', 'P' or 'B'
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        # self.board = [
        #     ["--", "--", "--", "--", "--", "--", "--", "--"],
        #     ["--", "--", "--", "--", "--", "--", "--", "--"],
        #     ["--", "--", "--", "--", "--", "--", "--", "--"],
        #     ["--", "wB", "--", "--", "wR", "--", "bB", "--"],
        #     ["--", "--", "--", "--", "--", "--", "--", "--"],
        #     ["--", "--", "--", "bR", "--", "--", "--", "--"],
        #     ["--", "--", "--", "--", "wP", "--", "--", "--"],
        #     ["--", "--", "--", "--", "wK", "--", "--", "--"]
        # ]
        
        self.moveFunctions = {'P': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves, 'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        
        self.whiteToMove = True
        self.movelog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.inCheck = False
        self.checks = []
        self.pins = []
        self.checkMate = False
        self.staleMate = False
        self.enPassantPossible = () # square where en-passant capture can happen
        
        # castling rights
        # self.whiteCastleKingside = True
        # self.whiteCastleQueenside = True
        # self.blackCastleKingside = True
        # self.blackCastleQueenside = True
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]
        # self.castleRightsLog.append(self.currentCastlingRight)
        
    '''
    Takes a Move as a parameter and executes it (this will not work for castling, pawn promotion and en-passant)
    '''    
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.movelog.append(move) # log the move so we can undo it later
        self.whiteToMove = not self.whiteToMove # swap players
        
        # update the king's location if moved
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)
            
        # pawn promotion
        if move.isPawnPromotion:
            promotedPiece = input("Promote to Q, R, B or N: ") # we can make this part of the ui later
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + promotedPiece
        
        # if pawn moves twice, next move can capture en-passant
        if move.pieceMoved[1] == 'P' and abs(move.startRow - move.endRow) == 2:
            self.enPassantPossible = ((move.endRow + move.startRow)//2, move.endCol)
        else:
            self.enPassantPossible = ()
        
        # if en-passant move, must update the board to capture the pawn
        if move.enPassant:
            self.board[move.startRow][move.endCol] = "--"
        
        # if pawn promotion change piece
        # if move.pawnPromotion:
        #     promotedPiece = input("Promote to Q, R, B or N: ") # we can make this part of the ui later
        #     self.board[move.endRow][move.endCol] = move.pieceMoved[0] + promotedPiece
        
        
        # castle moves
        if move.isCastleMove:
            if move.endCol - move.startCol == 2: # kingside
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1] # move rook
                self.board[move.endRow][move.endCol + 1] = "--" # empty space where rook was
            else: # queen side
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2] # move rook
                self.board[move.endRow][move.endCol - 2] = '--' # empty space where rook was
                
        # update castling rights
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                                 self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))
        
        
        
    '''
    Undo the last move
    '''
    def undoMove(self):
        if len(self.movelog) != 0: # make sure that there is a move to undo
            move = self.movelog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove # Switch turns back
            
            # update the king's position if needed
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)
            
            # undo en-passant is different
            if move.enPassant:
                self.board[move.endRow][move.endCol] = '--' # removes the pawn that was added in the wrong square
                self.board[move.startRow][move.endCol] = move.pieceCaptured # puts the pawn back on the correct square it was captured from
                self.enPassantPossible = (move.endRow, move.endCol) # allow an en-passant to happen on the next move
            
            # undo a 2 square pawn advance should make enPassantPossible = () again
            if move.pieceMoved[1] == "P" and abs(move.startRow - move.endRow) == 2:
                self.enPassantPossible = ()
                
            # give back castle rights if move took them away
            self.castleRightsLog.pop() # remove last move updates
            newRights = self.castleRightsLog[-1]
            # castleRights = self.castleRightsLog[-1]
            # self.whiteCastleKingside = castleRights.wks
            # self.blackCastleKingside = castleRights.bks
            # self.whiteCastleQueenside = castleRights.wqs
            # self.blackCastleQueenside = castleRights.bqs
            self.currentCastlingRight = CastleRights(newRights.wks, newRights.bks, newRights.wqs, newRights.bqs)
            
            # undo castle
            if move.isCastleMove:
                if move.endCol - move.startCol == 2: # kingside
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1] # move rook
                    self.board[move.endRow][move.endCol - 1] = '--' # empty space where rook was
                
                else: # queen side
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1] # move rook
                    self.board[move.endRow][move.endCol + 1] = '--' 
            
    '''
    All moves considering checks
    '''
    def getValidMoves(self):
        tempCastleRights = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                        self.currentCastlingRight.wqs, self.currentCastlingRight.bqs) # copy the current castling rights
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        self.getCastleMoves(kingRow, kingCol, moves)
        if self.inCheck:
            if len(self.checks) == 1: # only 1 check, block check or move king
                moves = self.getAllPossibleMoves()
                # to block a check you must move a piece into one of the squares between the enemy piece and king
                check = self.checks[0] # check information
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol] # enemy piece causing the check
                validSquares = [] # squares that pieces can move to
                # if knight, must capture knight or move king, other pieces can be blocked
                if pieceChecking[1] == 'N':
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i) # check[2] and check[3] are the check direction
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol: # once you get to piece and checks
                            break
                # get rid of any moves that don't block check or move king
                for i in range(len(moves) - 1, -1, -1): # go through backwards when you are removing from a list as iterating
                    if moves[i].pieceMoved[1] != 'K': # move doesn't move king so it must block or capture
                        if not (moves[i].endRow, moves[i].endCol) in validSquares: # move doesn't block checks or capture piece
                            moves.remove(moves[i])
            else: # double check, king has to move
                self.getKingMoves(kingRow, kingCol, moves)
        else: # not in check so all moves are fine
            moves = self.getAllPossibleMoves()
           
        
        if len(moves) == 0:
            if self.inCheck:
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False             
        
        # return self.getAllPossibleMoves()
        self.currentCastlingRight = tempCastleRights
        return moves
    
    
    '''
    Determine if the current player is in check
    '''
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])
    
    
    '''
    Returns if the player is in check, a list of pins, and a list of checks
    '''
    def checkForPinsAndChecks(self):
        pins = [] # squares where the allied pinned piece is and direction pinned from
        checks = [] # squares where enemy is applying a check
        inCheck = False
        if self.whiteToMove:
            enemyColor = 'b'
            allyColor = 'w'
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = 'w'
            allyColor = 'b'
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        
        # check outward from king for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = () # reset possible pins
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != 'K':
                        if possiblePin == (): # 1st allied piece could be pinned
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else: #2nd allied piece, so no pin or check possible in this direction
                            break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        # 5 possibilities here in this complex conditional
                        # 1.) orthogonally away from king and piece is a rook
                        # 2.) diagonally away from king and piece is a bishop
                        # 3.) 1 square away diagonally from king and piece is a pawn
                        # 4.) any direction and piece is a queen
                        # 5.) any direction 1 square away and piece is a king(this is necessary to prevent a king move to a square controlled by another king)
                        if (0 <= j <=3 and type == 'R') or \
                                (4 <= j <= 7 and type == 'B') or \
                                (i == 1 and type == 'P' and ((enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
                                (type == 'Q') or (i == 1 and type == 'K'):
                            if possiblePin == (): # no piece blocking, so check
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else: # piece blocking so pin
                                pins.append(possiblePin)
                                break
                        else: # enemy piece not applying check
                            break
                else: # off board
                    break
        
        # check for knight checks
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N': # enemy knight attacking king
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        return inCheck, pins, checks
                                            
    
    '''
    Determine if the enemy can attack square r, c
    '''
    def squareUnderAttack(self, r, c):
        # 4.) generating my opponent's moves
        self.whiteToMove = not self.whiteToMove # switch to opponent's turn
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove # switch turns back
        for move in oppMoves:
            if move.endRow == r and move.endCol == c: # square is under attack
                return True
        return False
    
    '''
    All moves without considering checks
    '''
    def getAllPossibleMoves(self):
        # moves = [Move((6, 0), (4, 0), self.board)]
        moves = []
        for r in range(len(self.board)): # number of rows
            for c in range(len(self.board[r])): # number of cols in given row
                turn = self.board[r][c][0]
                if (turn == "w" and self.whiteToMove) or (turn == "b" and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves) # calls the appropriate move function based on piece type
                    # print(moves)
        return moves
    
    
    '''
    Get all the pawn moves for the pawn located at row, col and add these moves to the list
    '''
    def getPawnMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        
        if self.whiteToMove:
            moveAmount = -1
            startRow = 6
            backRow = 0
            enemyColor = 'b'
        else:
            moveAmount = 1
            startRow = 1
            backRow = 7
            enemyColor = 'w'
        
        
        # if self.whiteToMove: # white pawn moves
        #     if self.board[r-1][c] == "--": # 1 square pawn advance
        #         if not piecePinned or pinDirection == (-1, 0):
        #             moves.append(Move((r, c), (r-1, c), self.board))
        #             if r == 6 and self.board[r-2][c] == "--": # 2 square pawn advance
        #                 moves.append(Move((r, c), (r-2, c), self.board))
            
        #     if c-1 >= 0: # captures to the left
        #         if not piecePinned or pinDirection == (-1,-1):
        #             if self.board[r-1][c-1][0] == 'b': # enemy piece to capture
        #                 moves.append(Move((r, c), (r-1, c-1), self.board))
        #     if c+1 <= 7: # captures to the right
        #         if not piecePinned or pinDirection == (-1, 1):
        #             if self.board[r-1][c+1][0] == 'b':
        #                 moves.append(Move((r, c), (r-1, c+1), self.board))
        # else:
        #     if self.board[r+1][c] == "--":
        #         if not piecePinned or pinDirection == (1, 0):
        #             moves.append(Move((r, c), (r+1, c), self.board))
        #             if r == 1 and self.board[r+2][c] == "--":
        #                 moves.append(Move((r, c), (r+2, c), self.board))
            
        #     if c-1 >= 0:
        #         if not piecePinned or pinDirection == (1, -1):
        #             if self.board[r+1][c-1][0] == 'w':
        #                 moves.append(Move((r,c), (r+1, c-1), self.board))
        #     if c+1 <= 7:
        #         if not piecePinned or pinDirection == (1, 1):
        #             if self.board[r+1][c+1][0] == 'w':
        #                 moves.append(Move((r, c), (r+1, c+1), self.board))
        
        
        if self.board[r+moveAmount][c] == '--': # 1 square move
            if not piecePinned or pinDirection == (moveAmount, 0):
                if r+moveAmount == backRow: # if piece gets to back rank it is a pawn promotion
                    pawnPromotion = True
                moves.append(Move((r, c), (r+moveAmount, c), self.board, pawnPromotion=True))
                if r == startRow and self.board[r+2*moveAmount][c] == '--': # 2 square moves
                    moves.append(Move((r, c), (r+2*moveAmount, c), self.board))
        
        if c-1 >= 0: # capture to left
            if not piecePinned or pinDirection == (moveAmount, -1):
                if self.board[r + moveAmount][c - 1][0] == enemyColor:
                    if r + moveAmount == backRow: # if piece gets to back rank then it is a pawn promotion
                        pawnPromotion = True
                    moves.append(Move((r, c), (r+moveAmount, c-1), self.board, pawnPromotion=True))
                if (r + moveAmount, c - 1) == self.enPassantPossible:
                    moves.append(Move((r, c), (r+moveAmount, c - 1 ), self.board, enPassant=True))
                    
        if c+1 <= 7: # capture to right
            if not piecePinned or pinDirection == (moveAmount, 1):
                if self.board[r + moveAmount][c + 1][0] == enemyColor:
                    if r + moveAmount == backRow: # if piece gets to back rank then it is a pawn promotion
                        pawnPromotion = True
                    moves.append(Move((r, c), (r+moveAmount, c + 1), self.board, pawnPromotion=True))
                if (r + moveAmount, c + 1) == self.enPassantPossible:
                    moves.append(Move((r, c), (r+moveAmount, c + 1 ), self.board, enPassant=True))
                    
    
    
    '''
    Get all the rook moves for the rook located at row, col and add these moves to the list
    '''
    def getRookMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q': # can't remove queen from pin on rook moves, only remove it on bishop moves
                    self.pins.remove(self.pins[i])
                break
            
            
        directions = ((-1, 0), (1, 0), (0, 1), (0, -1))
        if self.whiteToMove:
            enemyColor = "b"
        else:
            enemyColor = "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                # print(endRow, endCol)
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        # print(endRow, endCol)
                        if endPiece == "--": # empty space valid
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor: # enemy piece valid (capturing)
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:
                            break
                else:
                    break
                    
                
    
    '''
    Get all the knight moves for the knight located at row, col and add these moves to the list
    '''
    def getKnightMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        
        
        
        # directions = ((r-2, c+1), (r-2, c-1),
        #               (r-1, c+2), (r-1, c-2),
        #               (r+1, c+2), (r+1, c-2),
        #               (r+2, c+1), (r+2, c-1))
        directions = ((-2, -1), (-2, 1),
                      (-1, -2), (-1, 2),
                      (1, -2), (1, 2),
                      (2, -1), (2, 1))
        if self.whiteToMove:
            allyColor = "w"
        else:
            allyColor = "b"
        for d in directions:
            endRow = r + d[0]
            endCol = c + d[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
    
    
    '''
    Get all the bishop moves for the bishop located at row, col and add these moves to the list
    '''
    def getBishopMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        
        
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        if self.whiteToMove:
            enemyColor = "b"
        else:
            enemyColor = "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                # print(endRow, endCol)
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        # print(endRow, endCol)
                        if endPiece == "--": # empty space valid
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor: # enemy piece valid (capturing)
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:
                            break
                else:
                    break
    
    '''
    Get all the queen moves for the queen located at row, col and add these moves to the list
    '''
    def getQueenMoves(self, r, c, moves):
        # directions = ((-1, 0), (1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1))
        # if self.whiteToMove:
        #     enemyColor = "b"
        # else:
        #     enemyColor = "w"
        # for d in directions:
        #     for i in range(1, 8):
        #         endRow = r + d[0] * i
        #         endCol = c + d[1] * i
        #         # print(endRow, endCol)
        #         if 0 <= endRow < 8 and 0 <= endCol < 8:
        #             endPiece = self.board[endRow][endCol]
        #             # print(endRow, endCol)
        #             if endPiece == "--": # empty space valid
        #                 moves.append(Move((r, c), (endRow, endCol), self.board))
        #             elif endPiece[0] == enemyColor: # enemy piece valid (capturing)
        #                 moves.append(Move((r, c), (endRow, endCol), self.board))
        #                 break
        #             else:
        #                 break
        #         else:
        #             break
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)
    
    '''
    Get all the king moves for the king located at row, col and add these moves to the list
    '''
    def getKingMoves(self, r, c, moves):
        # directions = ((r-1, c-1), (r-1, c), (r-1, c+1),
        #               (r, c-1), (r, c+1),
        #               (r+1, c-1), (r+1, c), (r+1, c+1))
        
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        
        if self.whiteToMove:
            allyColor = "w"
        else:
            allyColor = "b"
            
        # for d in directions:
        #     endRow = d[0]
        #     endCol = d[1]
        #     if 0 <= endRow < 8 and 0 <= endCol < 8:
        #         endPiece = self.board[endRow][endCol]
        #         if endPiece[0] != allyColor:
        #             moves.append(Move((r, c), (endRow, endCol), self.board))
        
        for i in range(8):
            endRow = r + rowMoves[i]
            endCol = c + colMoves[i]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor: # not an ally piece (empty or enemy piece)
                    # place king on end square and check for checks
                    if allyColor == 'w':
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    # place king back on original location
                    if allyColor == 'w':
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)
        
        # self.getCastleMoves(r, c, moves)
    
    
    '''
    Generate castle moves for the king at (r, c) and add them to the list of moves
    '''
    def getCastleMoves(self, r, c, moves):
        inCheck = self.squareUnderAttack(r, c)
        if inCheck:
            print("oof")
            return # can't castle in check
        if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks): # can't castle if given up the rights
            self.getKingsideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs): # can't castle if given up the rights
            self.getQueensideCastleMoves(r, c, moves)
    
    
    '''
    Generate kingside castle moves for the king at (r, c). This method will only be called if player still has castle rights kingside.
    '''
    def getKingsideCastleMoves(self, r, c, moves):
        # check if two square between king and rook are clear and not under attack
        if self.board[r][c + 1] == '--' and self.board[r][c + 2] == '--' and \
            not self.squareUnderAttack(r, c + 1) and not self.squareUnderAttack(r, c + 2):
                moves.append(Move((r, c), (r, c+2), self.board, isCastleMove=True))
                
    
    '''
    Generate queenside castle moves for the king at (r, c). This method will only be called if player still has castle rights queenside.
    '''
    def getQueensideCastleMoves(self, r, c, moves):
        # check if three square between king and rook are clear and not under attack
        if self.board[r][c - 1] == '--' and self.board[r][c - 2] == '--' and self.board[r][c - 3] == '--' and \
            not self.squareUnderAttack(r, c - 1) and not self.squareUnderAttack(r, c - 2) and not self.squareUnderAttack(r, c - 3):
                moves.append(Move((r, c), (r, c-2), self.board, isCastleMove=True))
    
    
    
    
    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.whiteCastleKingside.wks = False
            self.whiteCastleQueenside.wqs = False
        elif move.pieceMoved == 'bK':
            self.blackCastleQueenside.bks = False
            self.blackCastleKingside.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 7:
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 0:
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 7:
                    self.currentCastlingRight.bks = False
                elif move.startCol == 0:
                    self.currentCastlingRight.bqs = False
    
    


class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs
    
                    
                
        
class Move():
    
    # maps keys to values
    # key : value
    ranksToRows = {"1":7, "2":6, "3":5, "4":4, "5":3, "6":2, "7":1, "8":0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a":0, "b":1, "c":2, "d":3, "e":4, "f":5, "g":6, "h":7}
    colsToFiles = {v: k for k, v in filesToCols.items()}
    
    
    def __init__(self, startSq, endSq, board, enPassant=False, pawnPromotion=False, isCastleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.enPassant = enPassant
        self.PawnPromotion = pawnPromotion
        self.isPawnPromotion = False
        if enPassant:
            self.pieceCaptured = 'bP' if self.pieceMoved == 'wP' else 'wP'
        if (self.pieceMoved == 'wP' and self.endRow == 0) or (self.pieceMoved == 'bP' and self.endRow == 7):
            self.isPawnPromotion = True
            
        # castle move
        self.isCastleMove = isCastleMove
        
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        # print(self.moveID)
        
    '''
    Overriding the equals method
    '''
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False
            
    
    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)
    
    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
    
    
    
    
    
    