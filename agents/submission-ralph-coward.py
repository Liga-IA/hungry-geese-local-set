from kaggle_environments.envs.hungry_geese.hungry_geese import Observation, Configuration,Action, row_col
from kaggle_environments.envs.hungry_geese.hungry_geese import adjacent_positions,min_distance
from pprint import pprint
ralph_last_action = [
    'SOUTH',
    'SOUTH',
    'SOUTH',
    'SOUTH'
]
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
    def get_body_len(self):
        return len(self._goose)
    def get_head(self):
        if(len(self._goose)>0):
            return self._goose[0]
        else:
            return -1
    def get_head_pos(self):
        if(len(self._goose)>0):
            return row_col(self._goose[0], self._configuration.columns)
        else:
            return -1,-1
    def get_neck_pos(self):
        if(len(self._goose)>1):
            return row_col(self._goose[1], self._configuration.columns)
        else:
            return -1,-1
    def am_i_there(self,row,col):
        achou = False
        for i in range(0,len(self._goose)):
            m_row,m_col = row_col(self._goose[i], self._configuration.columns)
            if m_row == row and m_col == col:
                achou = True
        return achou
    def get_next_position(self,move):
        if(self._r == -1 or self._c == -1):
            return -1,-1
        move_r,move_c = to_row_col(move)
        n_r = self._r + move_r
        n_c = self._c +move_c
        if(n_r > self._configuration.rows-1):
            n_r = n_r % self._configuration.rows
        if(n_r < 0):
            n_r = self._configuration.rows - abs(n_r) % self._configuration.rows

        if(n_c > self._configuration.columns-1):
            n_c = n_c % self._configuration.columns
        if(n_c < 0):
            n_c = self._configuration.columns - abs(n_c) % self._configuration.columns
        return n_r,n_c

def to_row_col(action):
    if action == Action.NORTH.name:
        return -1,0
    if action == Action.SOUTH.name:
        return 1,0
    if action == Action.EAST.name:
        return 0,1
    if action == Action.WEST.name:
        return 0,-1
def opposite(action):
    if action == Action.NORTH.name:
        return Action.SOUTH.name
    if action == Action.SOUTH.name:
        return Action.NORTH.name
    if action == Action.EAST.name:
        return Action.WEST.name
    if action == Action.WEST.name:
        return Action.EAST.name
    
def will_be_any_enemy_there(enemies_geese,row,col):
    achou = False
    for enemy in enemies_geese:
        for move in enemy._possible_moves:
            n_r,n_c = enemy.get_next_position(move)
            if(n_r == row and col == n_c):
                achou = True
    return achou

def is_any_enemy_there(enemies_geese,row,col):
    achou = False
    for enemy in enemies_geese:
        if enemy.am_i_there(row,col):
            achou = True
    return achou

def get_distance(x,y,x1,y1):
    return abs(x - x1) + abs(y - y1)

def get_min_distance_food_pos(position, foodList,columns):
    row, column = row_col(position, columns)
     
    distances = []
    for food_position in foodList:
        food_row, food_column = row_col(food_position, columns)
        distances.append(get_distance(row,column,food_row,food_column))
    min_d = None
    for i in range(0,len(distances)):
        if min_d == None:
            min_d = i
            continue
        if(distances[min_d]>distances[i]):
            min_d = i
        
    return row_col(foodList[i], columns)
    

def agent(obs_dict, config_dict):
    global ralph_last_action
    observation = Observation(obs_dict)
    configuration = Configuration(config_dict)
    
   #print("Player")
    # Define my player
    player_index = observation.index
    my_goose = Goose(observation.geese[player_index],configuration)
    player_row, player_column = my_goose.get_head_pos()
    
   #print("Enemies")
    # Define the enemies players
    enemies_indexes = []
    for i in range (0,len(observation.geese)):
        if i != player_index:
            enemies_indexes.append(i)
    
    enemies_geese = []
    for enemy in enemies_indexes:
        enemies_geese.append(Goose(observation.geese[enemy],configuration))
    
    
   #print("Food")
    # Get the nearest food position
    food_row, food_column = get_min_distance_food_pos(my_goose.get_head(),observation.food,configuration.columns)
    
    
   #print("Possible Moves")
    # List the possible moves
    possible_moves = [
        'SOUTH',
        'NORTH',
        'WEST',
        'EAST'
    ]
    if(ralph_last_action[player_index] in possible_moves):
        possible_moves.remove(ralph_last_action[player_index])
    
    
   #print("Possible Moves and colisions")
    moves = []
    for i in range(0,len(possible_moves)):
        move = possible_moves[i]
        n_r,n_c = my_goose.get_next_position(move)
        if( not is_any_enemy_there(enemies_geese,n_r,n_c) and not my_goose.am_i_there(n_r,n_c) and not will_be_any_enemy_there(enemies_geese,n_r,n_c) ):
            moves.append(move)
            
    
   #print("Possible Moves by food")
    # From the remaining possible moves, wich one get me nearest to the food?
    min_food_move = 0
    if(len(moves)>0):
        for i in range(0,len(moves)):
            n_r1,n_c1 = my_goose.get_next_position(moves[i])
            n_r2,n_c2 = my_goose.get_next_position(moves[min_food_move])
            if(get_distance(food_row,food_column,n_r1,n_c1) < get_distance(food_row,food_column,n_r2,n_c2)):
                min_food_move = i

    
    
   #print("Select Move")
    if(len(moves)>0 and min_food_move is not None):
        return_action = moves[min_food_move]
    else:
        return_action = 'NORTH'
   
   #print("Last Move")
    # Refresh the last move
    ralph_last_action[player_index] = opposite(return_action)
   #print(return_action)
   #print()
    return return_action