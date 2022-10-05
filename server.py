import random
import socket
from _thread import *
import pickle
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


class Game:
    """Class for containing the data for one Game. This will be stored in list while the server runs"""
    # Unique identifier for the game
    game_id = 0
    # List of the two players in the game
    player_ids = []
    # The transfer object for the game
    game_dto = PongDTO()

    def __init__(self):
        """Constructor for the Game class"""
        self.game_id = 0
        self.player_ids = []
        self.game_dto = PongDTO()

    def initiate_dto(self):
        """Method to initiate the Game DTO to default values"""
        self.game_dto.player_x = [player1_start_x, player2_start_x]
        self.game_dto.player_y = [player1_start_y, player2_start_y]
        self.game_dto.ball_x = ball_start_x
        self.game_dto.ball_y = ball_start_x
        self.game_dto.ball_velocity_x = ball_start_velocity_x
        self.game_dto.ball_velocity_y = ball_start_velocity_y
        # Pick a random direction for the ball
        self.game_dto.ball_direction_x = random.choice(('positive', 'negative'))
        self.game_dto.ball_direction_y = random.choice(('positive', 'negative'))
        self.game_dto.game_id = self.game_id
        self.game_dto.start_play = False
        self.game_dto.points = [0, 0]


def get_game_dto(game_id):
    """Get the DTO of the game from the global Games list"""
    # Iterate through the game list
    for game in game_ids:
        # Return the game dto if the game id matches
        if game_id == game.game_id:
            return game.game_dto


def get_game(game_id):
    """Get the game object from the global Games list"""
    # Iterate through the game list
    for game in game_ids:
        # Return the game object if the game id matches
        if game_id == game.game_id:
            return game


def update_game_dto(dto):
    """Updates the required attributes in server DTO with the DTO passed in argument"""
    # Get the game DTO
    game_dto = get_game_dto(dto.game_id)
    # Update the player's position from DTO in argument into the DTO in server
    game_dto.player_y[dto.player_id] = dto.player_y[dto.player_id]


def update_game_state(dto):
    """This method updates the state of the game. Here, this method moves the ball and updates the ball position.
    This method also resets the position id ball hits any wall.
    This method increases players' points when ball hits a wall."""
    # Get the game DTO from the game list
    game_dto = get_game_dto(dto.game_id)
    # Update the player's position received from client into the game dto.
    game_dto.player_y[dto.player_id] = dto.player_y[dto.player_id]
    # Start checking the ball position, move the ball and update the DTO to be sent to clients
    # Check if the ball is still away from right wall of the window
    if game_dto.ball_x < (player2_start_x - (ball_diameter / 2) - game_dto.ball_velocity_x) \
            and game_dto.ball_direction_x == 'positive':
        # Move ball towards right
        game_dto.ball_x += game_dto.ball_velocity_x
    # Check if the ball is still away from left wall of the window
    elif game_dto.ball_x > (player1_start_x + bat_width + (ball_diameter / 2) + game_dto.ball_velocity_x) \
            and game_dto.ball_direction_x == 'negative':
        # Move ball towards left
        game_dto.ball_x -= game_dto.ball_velocity_x
    # Check if the ball is near the left wall
    elif game_dto.ball_x <= (player1_start_x + bat_width + (ball_diameter / 2) + game_dto.ball_velocity_x) \
            and game_dto.ball_direction_x == 'negative':
        # Check if the ball has hit the left player
        if dto.player_y[0] <= game_dto.ball_y <= (dto.player_y[0] + bat_height):
            # Based on which part of the bat (4 parts), the ball has hit, the vertical direction of ball is updated.
            if (dto.player_y[0] + (bat_height * 0.25)) > game_dto.ball_y >= dto.player_y[0]:
                game_dto.ball_velocity_y = 5
                game_dto.ball_direction_y = 'negative'
            elif (dto.player_y[0] + (bat_height * 0.5)) > game_dto.ball_y >= (dto.player_y[0] + (bat_height * 0.25)):
                game_dto.ball_velocity_y = 4
                game_dto.ball_direction_y = 'negative'
            elif (dto.player_y[0] + (bat_height * 0.75)) > game_dto.ball_y >= (dto.player_y[0] + (bat_height * 0.5)):
                game_dto.ball_velocity_y = 4
                game_dto.ball_direction_y = 'positive'
            elif (dto.player_y[0] + bat_height) >= game_dto.ball_y >= (dto.player_y[0] + (bat_height * 0.75)):
                game_dto.ball_velocity_y = 5
                game_dto.ball_direction_y = 'positive'
            # Reflect the ball
            game_dto.ball_direction_x = 'positive'
        else:
            # If ball hits left wall, start ball from center position with default speed and direction
            game_dto.ball_x = ball_start_x
            game_dto.ball_y = ball_start_y
            game_dto.ball_velocity_x = ball_start_velocity_x
            game_dto.ball_velocity_y = ball_start_velocity_y
            game_dto.ball_direction_x = random.choice(('positive', 'negative'))
            game_dto.ball_direction_y = random.choice(('positive', 'negative'))
            # Increment right player's point
            game_dto.points[1] += 1
    # Check if the ball is near the right wall
    elif game_dto.ball_x >= (player2_start_x - (ball_diameter / 2) - game_dto.ball_velocity_x) \
            and game_dto.ball_direction_x == 'positive':
        # Check if the ball has hit the right player
        if dto.player_y[1] <= game_dto.ball_y <= (dto.player_y[1] + bat_height):
            # Based on which part of the bat (4 parts), the ball has hit, the vertical direction of ball is updated.
            if (dto.player_y[1] + bat_height * 0.25) > game_dto.ball_y >= dto.player_y[1]:
                game_dto.ball_velocity_y = 5
                game_dto.ball_direction_y = 'negative'
            elif (dto.player_y[1] + bat_height * 0.5) > game_dto.ball_y >= (dto.player_y[1] + bat_height * 0.25):
                game_dto.ball_velocity_y = 4
                game_dto.ball_direction_y = 'negative'
            elif (dto.player_y[1] + bat_height * 0.75) > game_dto.ball_y >= (dto.player_y[1] + bat_height * 0.5):
                game_dto.ball_velocity_y = 4
                game_dto.ball_direction_y = 'positive'
            elif (dto.player_y[1] + bat_height) >= game_dto.ball_y >= (dto.player_y[1] + bat_height * 0.75):
                game_dto.ball_velocity_y = 5
                game_dto.ball_direction_y = 'positive'
            # Reflect the ball
            game_dto.ball_direction_x = 'negative'
        else:
            # If ball hits right wall, start ball from center position with default speed and direction
            game_dto.ball_x = ball_start_x
            game_dto.ball_y = ball_start_y
            game_dto.ball_velocity_x = ball_start_velocity_x
            game_dto.ball_velocity_y = ball_start_velocity_y
            game_dto.ball_direction_x = random.choice(('positive', 'negative'))
            game_dto.ball_direction_y = random.choice(('positive', 'negative'))
            # Increment left player's point
            game_dto.points[0] += 1

    # Check if ball is away from bottom wall
    if game_dto.ball_y < (window_height - (ball_diameter / 2) - game_dto.ball_velocity_y) \
            and game_dto.ball_direction_y == 'positive':
        # Move ball downwards
        game_dto.ball_y += game_dto.ball_velocity_y
    # Check if ball is away from top wall
    elif game_dto.ball_y > ((ball_diameter / 2) + game_dto.ball_velocity_y) \
            and game_dto.ball_direction_y == 'negative':
        # Move ball upwards
        game_dto.ball_y -= game_dto.ball_velocity_y
    # Check if ball hits top wall
    elif game_dto.ball_y <= ((ball_diameter / 2) + game_dto.ball_velocity_y) \
            and game_dto.ball_direction_y == 'negative':
        # Reflect the ball
        game_dto.ball_direction_y = 'positive'
    # Check if ball hits bottom wall
    elif game_dto.ball_y >= (window_height - (ball_diameter / 2) - game_dto.ball_velocity_y) \
            and game_dto.ball_direction_y == 'positive':
        # Reflect the ball
        game_dto.ball_direction_y = 'negative'


def get_game_player_id():
    """This method is called when a new connection is accepted to start game and needs the game id and player id.
        It provides the available game id and the player id for the new player.
        If there is any game where one player is waiting for another player, that game id and a player id is given.
        If there is no existing game with one available slot, it creates a new game and returns the ids."""
    game_id = 0
    player_id = 0
    # If the game queue is empty, create a new game
    if len(game_ids) == 0:
        game = Game()
        game.game_id = game_id
        game.player_ids.append(player_id)
        # Initiate the data transfer object for the game
        game.initiate_dto()
        # Append game to queue
        game_ids.append(game)
        return game_id, player_id
    else:
        found = False
        # Iterate through the game queue
        for game in game_ids:
            # If a game has only one player awaiting, add a new player id and break from iteration with this game
            # instance
            if len(game.player_ids) == 1:
                found = True
                # Get the remaining player id from set {0,1}
                player_id = list({0, 1} - set(game.player_ids))[0]
                game.player_ids.append(player_id)
                # Since the game now has both players, indicate start of play
                game.game_dto.start_play = True
                break

        # Create new game if there is no game awaiting one player
        if not found:
            # Increment the last game id by 1 to create the new game id
            game_id = game_ids[-1].game_id + 1
            game = Game()
            game.game_id = game_id
            player_id = 0
            game.player_ids.append(player_id)
            # Initiate the data transfer object for the game
            game.initiate_dto()
            # Append game to queue
            game_ids.append(game)

        return game_id, player_id


def threaded_client(conn, game_id, player_id):
    """This method is called to start a new parallel thread for the new player.
        It performs below actions –
        > Get the data transfer object for the game from game queue
        > Set the player id into the DTO and send the DTO to client application
        > Start the loop with below actions in each loop –
            > Set the game speed
            > Receive DTO from client
            > If game has both players and start flag is active, update the game state
            > If start flag is inactive, do not update game state
            > Send updated DTO to client
        > If connection is lost with client for any reason –
            > Release the player id
            > Reset the game state
            > If both players left, remove the game from game queue"""

    # Get the DTO from game queue
    send_dto = get_game_dto(game_id)
    # Set the current player’s id into DTO before sending to client
    send_dto.player_id = player_id
    send_dto.msg = "Welcome to game " + str(game_id) + ", Player " + str(player_id)
    # Send the DTO with help of ‘pickle’
    conn.send(pickle.dumps(send_dto))

    run = True
    clock = pygame.time.Clock()

    while run:
        # Set the game speed
        clock.tick(game_speed)
        try:
            # Receive the DTO from client
            receive_dto = pickle.loads(conn.recv(data_size))
            # If data not received (indicating lost connection), exit from loop
            if not receive_dto:
                print('DTO not received')
                run = False
            else:
                # Set the player’s id into the received DTO as the game state will be updated relative to the player
                receive_dto.player_id = player_id
                # Check if the game is active i.e. both players are on
                if receive_dto.start_play:
                    # Update game state e.g. ball movement, player’s movement and points etc.
                    update_game_state(receive_dto)
                else:
                    # Just update the DTO with player’s movement and do not update other game state
                    update_game_dto(receive_dto)
                # Get the game DTO before sending back to client
                game_dto = get_game_dto(game_id)
                # Set player’s id into the DTO
                game_dto.player_id = player_id
                # Send the game DTO to client
                conn.sendall(pickle.dumps(game_dto))
        # For any exception, break the loop
        except Exception as e:
            run = False
            print("An error occurred:", e)

    print("Lost connection")
    # When connection with player is lost, get the game object and remove player
    game = get_game(game_id)
    game.player_ids.remove(player_id)
    # If both players had left, remove the game
    if len(game.player_ids) == 0:
        game_ids.remove(game)
    else:
        # Reset the game state when a player had left
        game.initiate_dto()
    # Release the connection with this client
    conn.close()


# Server IP is where the server python file will be running and accepting connections
server = "192.168.1.170"
# Port is where server will keep listening. Better to use a higher port as that is usually not used
port = 5555

# Initiate socket for the connection
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the server and port with socket
try:
    s.bind((server, port))
except socket.error as e:
    str(e)

# Start listening for client connections
s.listen()
print("Waiting for a connection, Server Started")

# Initialize the blank game queue
game_ids = []
# Start loop for accepting incoming connections from clients (i.e. players) to this server
while True:
    # Accept client connection
    conn, addr = s.accept()
    print("Connected to:", addr)

    # Get the game id and player id
    game_id, player_id = get_game_player_id()
    print("Game id -", game_id, ", Player id -", player_id)
    print('Game length -', len(game_ids))

    # Start new threaded connection with client and call the method to handle the thread.
    start_new_thread(threaded_client, (conn, game_id, player_id))
