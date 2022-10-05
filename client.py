import pickle
import random
import socket
import pygame

# Game related global variables
window_width = 700
window_height = 700
player1_start_x = 10
player1_start_y = 300
player2_start_x = 670
player2_start_y = 300
ball_start_x = 350
ball_start_y = 350
ball_start_velocity_x = 3
ball_start_velocity_y = 1
bat_width = 20
bat_height = 100
bat_movement_speed = 20
ball_diameter = 20

# Packet size for sending and receiving between server and clients
data_size = 4096

# FPS speed for the game clock
game_speed = 30


class PongDTO:
    """This is a data transfer object containing the variables that will be passed between server and clients."""

    # Initiate to default values
    def __init__(self):
        self.game_id = 0
        self.player_id = 0
        self.player_x = []
        self.player_y = []
        self.ball_x = 0
        self.ball_y = 0
        self.ball_velocity_x = 0
        self.ball_velocity_y = 0
        self.ball_direction_x = ''
        self.ball_direction_y = ''
        self.start_play = False
        self.msg = ''
        self.end_play = False
        self.points = [0, 0]


class Bat:
    """This class facilitates managing the players’ bats on screen."""

    def __init__(self, x, y, color):
        """Constructor to initiate the bat"""
        self.x = x
        self.y = y
        self.color = color
        self.width = bat_width
        self.height = bat_height
        self.points = 0

    def draw(self, window):
        """This method draws the bat on screen. It takes the surface as argument."""
        pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.height))

    def move(self, direction):
        """This method takes the direction of movement as argument and updates the coordinates of the bat."""
        if direction == 'up' and self.y > (bat_movement_speed / 2):
            self.y -= bat_movement_speed
        elif direction == 'down' and self.y < (window_height - bat_height - (bat_movement_speed / 2)):
            self.y += bat_movement_speed

    def add_point(self):
        """This is a data transfer object containing the variables that will be passed between server and clients."""
        self.points += 1


class Ball:
    """This class facilitates managing the movement of the ball on screen."""

    def __init__(self, x, y, color):
        """Constructor to initiate the ball"""
        self.x = x
        self.y = y
        self.color = color
        self.width = ball_diameter
        self.velocity_x = ball_start_velocity_x
        self.velocity_y = ball_start_velocity_y
        self.direction_x = random.choice(('positive', 'negative'))
        self.direction_y = random.choice(('positive', 'negative'))

    def draw(self, window):
        """This method draws the ball on screen. It takes the surface as argument."""
        pygame.draw.circle(window, self.color, (self.x, self.y), (ball_diameter / 2))


def update_bat_ball(dto):
    """This method takes PongDTO as input and updates the positions of the bats and the ball.
    This method also sets the colours of the player and opponent differently."""

    # Set the colors of bats
    bats[player_id].color = (144, 238, 144)  # light green
    bats[opponent_id].color = (255, 185, 127)  # light orange

    # Set the initial coordinates of the bats and ball as received from server
    bats[0].x = dto.player_x[0]
    bats[0].y = dto.player_y[0]
    bats[1].x = dto.player_x[1]
    bats[1].y = dto.player_y[1]
    ball.x = dto.ball_x
    ball.y = dto.ball_y


# Create a socket for the server and client connection
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Server IP is where the server python file is running and listening for connections
server = "192.168.1.170"
# Port is where server is listening.
port = 5555
addr = (server, port)

# Initiate client and server connection
client.connect(addr)
# Receive the data transfer object from server for first time
receive_dto = pickle.loads(client.recv(data_size))
print("You are player ", receive_dto.player_id)

# Retrieve the player id from the DTO
player_id = receive_dto.player_id
# The opponent id is the other id from set {0,1}
opponent_id = list({0, 1} - {receive_dto.player_id})[0]

# Initiate the Bat objects
bats = [Bat(0, 0, (0, 0, 0)), Bat(0, 0, (0, 0, 0))]
# Initiate the Ball object
ball = Ball(0, 0, (0, 0, 0))

# Update the coordinates of the bats and ball with received DTO. This will get the initial positions from the server
update_bat_ball(receive_dto)
# Initiate font
pygame.font.init()

# Show the game title and player’s points on title bar of the window
pygame.display.set_caption(f'Ping-Pong Your score (Green):{bats[player_id].points},'
                           f' Opponent (Orange):{bats[opponent_id].points}')
# Set the surface attributes for the window
win = pygame.display.set_mode((window_width, window_height))

run = True
# Get the game clock
clock = pygame.time.Clock()

# Start the loop for the game
while run:
    # Set the game speed
    clock.tick(game_speed)
    # Fill the window color
    win.fill((255, 255, 255))
    # Draw the bats
    bats[0].draw(win)
    bats[1].draw(win)
    # Draw the ball
    ball.draw(win)
    # Render the window elements
    pygame.display.update()

    # Check for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        # Get the list of keys pressed
        keys = pygame.key.get_pressed()
        # Break the loop if player has escaped the game
        if keys[pygame.K_ESCAPE]:
            run = False
        # ‘W’ to move player’s bat upwards
        if keys[pygame.K_w]:
            bats[player_id].move('up')
        # ‘S’ to move player’s bat downwards
        if keys[pygame.K_s]:
            bats[player_id].move('down')
        # Break the loop if player has clicked on the window
        if event.type == pygame.MOUSEBUTTONDOWN:
            run = False

    # Set the DTO as per screen for both players. This is required for opponent because
    # client should reflect what is received
    receive_dto.player_y[0] = bats[0].y
    receive_dto.player_y[1] = bats[1].y

    try:
        # Send the DTO to server
        client.sendall(pickle.dumps(receive_dto))
        # Receive the DTO from server
        receive_dto = pickle.loads(client.recv(data_size))
    # Break loop for any exception
    except Exception as e:
        run = False
        print("Couldn't get game")
        print("An error occurred:", e)
        break

    # Update the coordinates of the bats and ball with received DTO.
    update_bat_ball(receive_dto)

    # Update the points as received from DTO into the title bar
    pygame.display.set_caption(
        f'Ping-Pong Your score (Green):{receive_dto.points[player_id]},'
        f' Opponent (Orange):{receive_dto.points[opponent_id]}')
