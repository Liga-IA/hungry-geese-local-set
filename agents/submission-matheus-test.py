from kaggle_environments.envs.hungry_geese.hungry_geese import Observation, Configuration, Action, row_col
from random import randint

# tenho que prever colisão de 1 bloco(dar preferencia)
# prever colisão por causa da borda(acho q fiz isso)
# fazer com que escolha a comida mais perto(se nao tiver alguem mais perto)

last_move = [None,
None,
None,
None]

def agent(obs_dict, config_dict):
    """This agent always moves toward observation.food[0] but does not take advantage of board wrapping"""
    global last_move
    observation = Observation(obs_dict)
    configuration = Configuration(config_dict)
    player_index = observation.index
    player_goose = observation.geese[player_index]
    player_head = player_goose[0]
    player_row, player_column = row_col(player_head, configuration.columns)
    possible_moves = [Action.SOUTH.name, Action.NORTH.name, Action.WEST.name, Action.EAST.name]
    possible_move = None
    oldFoodDistanceToMe = 9999
    
    def getFoodsIndex(): 
        foods = []
        for i in range(len(observation.food)):
            food = observation.food[i]
            foods.append(row_col(food, configuration.columns))
        return foods

    def getGoose(index):
        goose = []
        for i in range(len(observation.geese[index])):
            goose.append(row_col(observation.geese[index][i], configuration.columns))
        return goose

    def getGeesesIndex():
        geeses = []
        for geese in observation.geese:
            geeses.append(row_col(geese[0], configuration.columns))
        return geeses

    def randomMove(moves):
        if len(moves) > 1:
            return moves[randint(0, len(moves) - 1)]
        return moves[0]

    def countMoves(x1, y1, x2, y2):
        return abs((x1-x2)+(y1-y2)) 

    def willCollide(x, y, action):
        #print(f'Goose[{player_index} in player_row: {player_row}, player_column: {player_column} move to {action} and can collide with x: {x}, y: {y}')
        if action == Action.WEST.name:
            if player_column - 1 == y and x == player_row:
                return True 
            if player_column == 0 and y == 10 and x == player_row:
                return True
        if action == Action.EAST.name:
            if player_column + 1 == y and x == player_row:
                return True
            if player_column == 10 and y == 0 and x == player_row:
                return True
        if action == Action.SOUTH.name:
            if player_row + 1 == x and y == player_column:
                return True
            if player_row == 6 and x == 0 and y == player_column:
                return True
        if action == Action.NORTH.name:
            if player_row - 1 == x and y == player_column:
                return True
            if player_row == 0 and x == 6 and y == player_column:
                return True
        return False

    def opposite(action):
        if action == Action.NORTH.name:
            return Action.SOUTH.name
        if action == Action.SOUTH.name:
            return Action.NORTH.name
        if action == Action.EAST.name:
            return Action.WEST.name
        if action == Action.WEST.name:
            return Action.EAST.name

    possible_moves = [Action.SOUTH.name, Action.NORTH.name, Action.WEST.name, Action.EAST.name]

    if last_move[player_index] is not None:
        print(f'Geese {player_index} removes opposite last move: {opposite(last_move[player_index])}')
        possible_moves.remove(opposite(last_move[player_index]))

    for geese_row, geese_column in getGeesesIndex():
        for food_row, food_column in getFoodsIndex():
            foodDistanceToMe = countMoves(food_row, food_column, player_row, player_column)
            if oldFoodDistanceToMe > foodDistanceToMe:
                oldFoodDistanceToMe = foodDistanceToMe
            else:
                continue
            
            geeseDistanceToFood = countMoves(geese_row, geese_column, food_row, food_column)
            if foodDistanceToMe < geeseDistanceToFood:
                if food_row > player_row:
                    possible_move = Action.SOUTH.name

                if food_row < player_row:
                    possible_move = Action.NORTH.name

                if food_column > player_column:
                    possible_move = Action.EAST.name

                if food_column < player_column:
                    possible_move = Action.WEST.name
                
                print(f'Geese {player_index} based by food, possible move: {possible_move}')
    if possible_move not in possible_moves:
        print(f'Geese {player_index}, possible move: {possible_move} is banned.')
        possible_move = randomMove(possible_moves)

    for i in range(len(observation.geese)):
        geese_index = getGoose(i)
        j = 0
        while j < len(geese_index):
            collision = False
            x, y = geese_index[j]
            if i != player_index:
                print(f'geese {player_index} -> geese {i} part {j}')
                #print(f'goose[{player_index}] in {getGoose(player_index)[0]} with possible move: {possible_move} can colide with goose[{i}] in x: {x} and y: {y}')
                while willCollide(x, y, possible_move):
                    collision = True
                    print(f'goose[{player_index}] in {getGoose(player_index)[0]} with possible move: {possible_move} will colide with goose[{i}] in x: {x} and y: {y}')
                    possible_moves.remove(possible_move)
                    possible_move = randomMove(possible_moves)
                    print(f'now goose[{player_index}] will to {possible_move}')
                    j = 0
            if not collision:
                j += 1

    for x, y in getGoose(player_index):
        while willCollide(x, y, possible_move):
            print(f'BODY HIT!!!')
            possible_moves.remove(possible_move)
            possible_move = randomMove(possible_moves)

    if len(possible_moves) == 1:
        print(f'Geese {player_index} just remain this move: {possible_moves[0]}')
        possible_move = possible_moves[0]

    last_move[player_index] = possible_move

    print(f'Geese {player_index}: {getGoose(player_index)} move to {possible_move}')
    return possible_move
