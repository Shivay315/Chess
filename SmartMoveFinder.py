import random





def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves)-1)]

def pawnPromotionRandom():
    return random.choice(['Q', 'R', 'N', 'B'])

def findBestMove():
    return