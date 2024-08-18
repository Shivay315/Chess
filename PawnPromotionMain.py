import pygame as p
import PawnPromotionEngine, ChessEngine, SmartMoveFinder, ChessMain


WIDTH = HEIGHT = 512
DIMENSION = 2 # dimensions fo a chess board are 8x8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15 # for animations later on
IMAGES = {}

def loadImages():
    pieces = ['wR', 'wN', 'wB', 'wQ', 'wK', 'bR', 'bN', 'bB','bQ', 'bK']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/"+ piece + ".png"), (SQ_SIZE, SQ_SIZE))
    # NOTE: we can access an image by saying 'IMAGES['wP']'
    
    
def main():
    p.init()
    screen1 = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen1.fill(p.Color("white"))
    ps = PawnPromotionEngine.PromotionState()
    gs = ChessEngine.GameState()
    
    loadImages()
    
    playerOne = False # If a human is playing white, then this will be True. If an AI is playing, then it will be False
    playerTwo = False # Same as above but for black
    running = True
    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        if gs.whiteToMove:
            allyColor = 'w'
        else:
            allyColor = 'b'
        
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            
            # mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if humanTurn:
                    location = p.mouse.get_pos()
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    running = False
                    return ps.whiteBoard[row][col][1]
            
        # AI move finder logic
        if not humanTurn:
            return SmartMoveFinder.pawnPromotionRandom()
        
        drawPromotionState(screen1, ps, allyColor)
        clock.tick(MAX_FPS)
        p.display.flip()
                
def drawPromotionState(screen1, ps, allyColor):
    drawBoard(screen1)
    if allyColor == 'w':
        drawPieces(screen1, ps.whiteBoard)
    else:
        drawPieces(screen1, ps.blackBoard)
    
    
def drawBoard(screen1):
    colors = [p.Color('aliceblue'), p.Color("dodgerblue4")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c) % 2)]
            p.draw.rect(screen1, color, p.Rect(c*SQ_SIZE,r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
def drawPieces(screen1, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            screen1.blit(IMAGES[piece], p.Rect(c*SQ_SIZE,r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
# if __name__ == "__main__":
#     main()