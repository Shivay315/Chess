"""
This is our main driver file. It will be responsible for handling user input and displaying the current GameState object
"""

import pygame as p
import ChessEngine, SmartMoveFinder

WIDTH = HEIGHT = 512
DIMENSION = 8 # dimensions fo a chess board are 8x8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15 # for animations later on
IMAGES = {}

'''
Initialize a global dictionary of images. This will be called exactly once in the main.
'''

def loadImages():
    pieces = ['wP', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bP', 'bR', 'bN', 'bB', 'bQ', 'bK']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
    # NOTE: we can access an image by saying 'IMAGES['wP']'
    

'''
The main driver for our code. This will handle user input and updating the graphics
'''
def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    
    validMoves = gs.getValidMoves()
    moveMade = False # flag variable for when a move is made
    
    
    loadImages() # only do this once, before the while loop
    running = True
    sqSelected = () # no square selected initially, keep track of the last click of the user (tuple: (row, col))
    playerClicks = [] # keep track of player clicks (two tuples: [(6, 4), (4, 4)])
    gameOver = False
    playerOne = False # If a human is playing white, then this will be True. If an AI is playing, then it will be False
    playerTwo = False # Same as above but for black
    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
                
            # mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos() #(x, y) location of mouse
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sqSelected == (row, col): # the user clicked the same square twice
                        sqSelected = () # deselect
                        playerClicks = [] # clear player clicks
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected) # append both 1st and 2nd clicks?>.
                    if len(playerClicks) == 2: # after 2nd click
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                print(move.getChessNotation())
                                sqSelected = () # reset user clicks
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]
                            
            # key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: # undo when 'z' is pressed
                    gs.undoMove()
                    moveMade = True
                    
        # AI move finder logic
        if not gameOver and not humanTurn:
            AIMove = SmartMoveFinder.findRandomMove(validMoves)
            gs.makeMove(AIMove)
            moveMade = True
                
        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False
            
        drawGameState(screen, gs, validMoves, sqSelected)
        
        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, '!!Black wins by checkmate!!')
            else:
                drawText(screen, '!!White wins by checkmate!!')
        elif gs.staleMate:
            gameOver = True
            drawText(screen, 'Stalemate')
        
        
        clock.tick(MAX_FPS)
        p.display.flip()


'''
Responsible for all the graphics within a current game state.
'''
def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen) # draw squares on the board
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board) # draw pieces on top of those squares
    

'''
Highlight square selected and moves for piece selected
'''
def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'): #sqSelected is a piece that can be moved
            # highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(255) # transperancy value -> 0 transparent; 255 opaque
            t = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA, 32)
            t = t.convert_alpha()
            t.set_alpha(100)
            center = (SQ_SIZE // 2, SQ_SIZE // 2)
            radius = 10
            s.fill(p.Color('pale turquoise'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            t.fill(p.Color(0,0,0,0))
            p.draw.circle(t, 'black', center, radius)
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(t, (SQ_SIZE*move.endCol, SQ_SIZE*move.endRow))
            
        
        

'''

Draw the squares on the board. The top left square is always light.
'''
def drawBoard(screen):
    colors = [p.Color('aliceblue'), p.Color("dodgerblue4")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c) % 2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
                

'''
Draw the pieces on the board using the current GameState.board
'''
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--": # not empty square
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
                

def drawText(screen, text):
    font = p.font.SysFont("Helvitca", 45, True, False)
    textObject = font.render(text, 0 , p.Color('Black'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color('red'))
    screen.blit(textObject, textLocation.move(2,2))

'''
Calling the main function using the python prefered way
'''
if __name__ == "__main__":
    main()