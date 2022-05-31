from shutil import move
import numpy as np
import pygame
import sys
import math
import serial, time
import threading, queue

pygame.mixer.init()
sound = pygame.mixer.Sound('colonnaSonora.mp3')
sound.set_volume(0.75)
sound.play()

BLUE = (0,0,255)
BLACK = (0,0,0)
RED = (255,0,0)
YELLOW = (255,255,0)

ROW_COUNT = 6
COLUMN_COUNT = 7

def create_board():
    board = np.zeros((ROW_COUNT,COLUMN_COUNT))
    return board

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def is_valid_location(board, col):
    return board[ROW_COUNT-1][col] == 0

def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r

def print_board(board):
    print(np.flip(board, 0))

def winning_move(board, piece):
    # Controlla le posizioni orizzontali per vincere
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True

    # Controlla le posizioni verticali per vincere
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True

    #Controllare le diaganoli a pendenza positiva
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True

    # Controllare le diaganoli con pendenza negativa
    for c in range(COLUMN_COUNT-3):
        for r in range(3, ROW_COUNT):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True

def draw_board(board):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BLACK, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)
    
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):		
            if board[r][c] == 1:
                pygame.draw.circle(screen, RED, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
            elif board[r][c] == 2: 
                pygame.draw.circle(screen, YELLOW, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
    pygame.display.update()

black = 0, 0, 0
dt = 1
gamma = 0.05
q = queue.Queue()

class Read_Microbit(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self._running = True
      
    def terminate(self):
        self._running = False
        
    def run(self):
        #serial config
        port = "COM13"
        s = serial.Serial(port)
        s.baudrate = 115200
        data = ""

        while self._running:
            data = s.readline().decode()
            temp = data.split(" ")
            q.put(temp)
            time.sleep(0.01)


board = create_board()
print_board(board)
game_over = False
turn = 0

pygame.init()

SQUARESIZE = 100

width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT+1) * SQUARESIZE

size = (width, height)

RADIUS = int(SQUARESIZE/2 - 5)

screen = pygame.display.set_mode(size)
draw_board(board)
pygame.display.update()

myfont = pygame.font.SysFont("monospace", 75)
t1 = Read_Microbit()
t1.start() 

posx = 0
turn = 0
pulsante = ""
while not game_over:
    sound.play()
    dati = q.get()

    if len(dati)==2:
        movimento = dati[0]
        pulsante = dati[1]
        if int(movimento) < -500:
            pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
            posx -= 10
        elif int(movimento) > 500:
            pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
            posx += 10

    if turn == 0:
        pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE/2)), RADIUS)
    elif turn == 1: 
        pygame.draw.circle(screen, YELLOW, (posx, int(SQUARESIZE/2)), RADIUS)
    
    pygame.display.update()

    if pulsante == "premuto\r\n":
        pulsante = "no"
        pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
        if turn == 0:
            col = int(math.floor(posx/SQUARESIZE))
            if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, 1)

                    if winning_move(board, 1):
                        label = myfont.render("Player 1 wins!!", 1, RED)
                        screen.blit(label, (40,10))
                        game_over = True
        else:				
                col = int(math.floor(posx/SQUARESIZE))
                if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, 2)

                    if winning_move(board, 2):
                        label = myfont.render("Player 2 wins!!", 1, YELLOW)
                        screen.blit(label, (40,10))
                        game_over = True

        print_board(board)
        draw_board(board)

        turn += 1
        turn = turn % 2

        if game_over:
            sound.stop()
            pygame.time.wait(3000)

    

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()


