from kaggle_environments.envs.hungry_geese.hungry_geese import Observation, Configuration, Action, row_col
import numpy as np
from math import sqrt
import heapq

class Node:
    """
    A node class for A* Pathfinding
    """

    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position
    
    def __repr__(self):
      return f"{self.position} - g: {self.g} h: {self.h} f: {self.f}"

    # defining less than for purposes of heap queue
    def __lt__(self, other):
      return self.f < other.f
    
    # defining greater than for purposes of heap queue
    def __gt__(self, other):
      return self.f > other.f

def return_path(current_node):
    path = []
    current = current_node
    while current is not None:
        path.append(current.position)
        current = current.parent
    return path[::-1]  # Return reversed path


def astar(maze, start, end, allow_diagonal_movement = False):
    """
    Returns a list of tuples as a path from the given start to the given end in the given maze
    :param maze:
    :param start:
    :param end:
    :return:
    """

    # Create start and end node
    start_node = Node(None, start)
    start_node.g = start_node.h = start_node.f = 0
    end_node = Node(None, end)
    end_node.g = end_node.h = end_node.f = 0

    # Initialize both open and closed list
    open_list = []
    closed_list = []

    # Heapify the open_list and Add the start node
    heapq.heapify(open_list) 
    heapq.heappush(open_list, start_node)

    # Adding a stop condition
    outer_iterations = 0
    max_iterations = (len(maze[0]) * len(maze) // 2)

    # what squares do we search
    adjacent_squares = ((0, -1), (0, 1), (-1, 0), (1, 0),)
    if allow_diagonal_movement:
        adjacent_squares = ((0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1),)

    # Loop until you find the end
    while len(open_list) > 0:
        outer_iterations += 1

        if outer_iterations > max_iterations:
          # if we hit this point return the path such as it is
          # it will not contain the destination
          #warn("giving up on pathfinding too many iterations")
          return return_path(current_node)       
        
        # Get the current node
        current_node = heapq.heappop(open_list)
        closed_list.append(current_node)

        # Found the goal
        if current_node == end_node:
            return return_path(current_node)

        # Generate children
        children = []
        
        for new_position in adjacent_squares: # Adjacent squares

            # Get node position
            node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

            # Make sure within range
            if node_position[0] > (len(maze) - 1) or node_position[0] < 0 or node_position[1] > (len(maze[len(maze)-1]) -1) or node_position[1] < 0:
                continue

            # Make sure walkable terrain
            if maze[node_position[0]][node_position[1]] != 0:
                continue

            # Create new node
            new_node = Node(current_node, node_position)

            # Append
            children.append(new_node)

        # Loop through children
        for child in children:
            # Child is on the closed list
            if len([closed_child for closed_child in closed_list if closed_child == child]) > 0:
                continue

            # Create the f, g, and h values
            child.g = current_node.g + 1
            child.h = ((child.position[0] - end_node.position[0]) ** 2) + ((child.position[1] - end_node.position[1]) ** 2)
            child.f = child.g + child.h

            # Child is already in the open list
            if len([open_node for open_node in open_list if child.position == open_node.position and child.g > open_node.g]) > 0:
                continue

            # Add the child to the open list
            heapq.heappush(open_list, child)

    #warn("Couldn't get a path to destination")
    return None
class Goose:
    def __init__(self,goose,config):
        self._goose = goose
        self._configuration = config
        if(len(self._goose)>0):
            self._r, self._c = row_col(self._goose[0], self._configuration.columns)
        else:
            self._r = -1
            self._c = -1

        self._possible_moves = [
            'SOUTH',
            'NORTH',
            'WEST',
            'EAST'
        ]


def agent(obs_dict, config_dict):
    """This agent always moves toward observation.food[0] but does not take advantage of board wrapping"""
    observation = Observation(obs_dict)
    configuration = Configuration(config_dict)
    maze_col = configuration.columns
    maze_rows = configuration.rows
    maze = np.zeros([maze_rows, maze_col])
 
    print("Player")
    # Define my player
    
    player_index = observation.index
    player_goose = observation.geese[player_index]
    player_head = player_goose[0]
    player_row, player_column = row_col(player_head, configuration.columns)
    start = (player_row, player_column)
    print(start)
    #Define Food

    hipotenuse_low = 14
    closest_food = observation.food[0]
    for food in observation.food:
        food_row, food_column = row_col(food, configuration.columns)
        hipotenuse = sqrt((player_row - food_row)**2 + (player_column - food_column)**2)
        if hipotenuse < hipotenuse_low:
            hipotenuse_low = hipotenuse
            closest_food = food

    end = row_col(closest_food, configuration.columns)

    # Define the enemies players
    enemies_indexes = observation.geese
    del enemies_indexes[player_index]

    for enemies in enemies_indexes:
        for enemies_pos in enemies:
            enemie_row, enemie_col = row_col(enemies_pos, configuration.columns)
            maze[enemie_row, enemie_col] = 1

    for player_pos in player_goose[1:]:
        player_rw, player_col = row_col(player_pos, configuration.columns)
        maze[player_rw, player_col] = 1

    path = astar(maze, start, end, False)
    next_move = path[1]
    print(next_move)
    print(player_column)
    print(player_row)
    x =  int(next_move[1]) - int(player_column)
    y =  int(next_move[0]) - int(player_row)
    print(x, y)
    print(maze)
    if x == -1 and y == 0:
        print("WEST")
        return Action.WEST.name
    if x == 1 and y == 0:
        print("EAST")
        return Action.EAST.name
    if x == 0 and y == -1:
        print("NORTH")
        return Action.NORTH.name
    if x == 0 and y == 1:
        print("SOUTH")
        return Action.SOUTH.name