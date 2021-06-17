from kaggle_environments import make, evaluate
from kaggle_environments.envs.hungry_geese.hungry_geese import Observation, Configuration, Action, row_col
from kaggle_environments.envs.hungry_geese.hungry_geese import translate, adjacent_positions, min_distance
from tensorflow import keras

import os
import random
import numpy as np
import pandas as pd
from pprint import pprint
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ['TF_XLA_FLAGS'] = '--tf_xla_enable_xla_devices'
def get_grid_from_obs(obs,columns,rows):
        mapa = []
        for i in range(0,rows):
            mapa.append([])
            for j in range(0,columns):
                achou = False
                for food in obs['food']:
                    x,y = row_col(food,columns)
                    if(x == i and y == j):
                        mapa[i].append(3)
                        achou = True
                        break
                if(achou):
                    continue
                aux = 0
                for goose in obs['geese']:
                    gs = 2
                    if(aux == obs['index']):
                        gs = 1
                    aux = aux +1
                    for part in goose:
                        x,y = row_col(part,columns)
                        if(x == i and y == j):
                            mapa[i].append(gs)
                            achou = True
                            break
                    if(achou):
                        break
                if(achou):
                    continue
                mapa[i].append(0)
        return np.array(mapa)
def opposite(action):
    if action == Action.NORTH:
        return Action.SOUTH
    if action == Action.SOUTH:
        return Action.NORTH
    if action == Action.EAST:
        return Action.WEST
    if action == Action.WEST:
        return Action.EAST
def get_sensors_from_grid(grid,columns,obs,last,debug):
    print()
    if(len(obs['geese'][obs['index']])==0):
        return np.array([0,0,0,0,0,0,0])
    px,py = row_col(obs['geese'][obs['index']][0],columns)
    actL = []
    for action in Action:
        actL.append(action)
    frente = 0
    if(last):
        actL.remove(last)
        for i in range(0,len(actL)):
            if(actL[i] == opposite(last)):
                frente = i
                break
    else: # Diz que esta indo para o norte e remove o oposto (SUL)
        actL.remove(action.SOUTH)
        frente = 0
    

    direita = frente+1
    if(direita>3):
        direita = direita-4
    esquerda = frente + 3
    if(esquerda>3):
        esquerda = esquerda - 4

    movimentos = [
        [-1,0],     #Norte
        [0,1],     #Leste
        [1,0],      #Sul
        [0,-1],      #Oeste
    ]
    sensor_frente = [0,0] #[distancia,tipo (0:inimigo,1:food)]
    for i in range(0,11):
        px_a,py_a = (px+movimentos[frente][0]*(i+1),py+movimentos[frente][1]*(i+1))
        if(px_a>6):
            px_a = px_a - 7
        if(py_a>10):
            py_a = py_a - 11
        
        if(px_a<0):
            px_a = 7 + px_a
        if(py_a<0):
            py_a = 11 + py_a
        
        if(grid[px_a][py_a] == 2 or grid[px_a][py_a] == 1):
            break
        if(grid[px_a][py_a] == 3):
            sensor_frente[1] = 1
            break
        else:
            sensor_frente[0]+=1
    
    sensor_esquerda = [0,0] #[distancia,tipo (0:inimigo,1:food)]
    for i in range(0,11):
        px_a,py_a = (px+movimentos[esquerda][0]*(i+1),py+movimentos[esquerda][1]*(i+1))
        if(px_a>6):
            px_a = px_a - 7
        if(py_a>10):
            py_a = py_a - 11
        
        if(px_a<0):
            px_a = 7+ px_a
        if(py_a<0):
            py_a = 11 + py_a
        
        if(grid[px_a][py_a] == 2 or grid[px_a][py_a] == 1):
            break
        if(grid[px_a][py_a] == 3):
            sensor_esquerda[1] = 1
            break
        else:
            sensor_esquerda[0]+=1
    
    sensor_direita = [0,0] #[distancia,tipo (0:inimigo,1:food)]
    for i in range(0,11):
        px_a,py_a = (px+movimentos[direita][0]*(i+1),py+movimentos[direita][1]*(i+1))
        if(px_a>6):
            px_a = px_a - 7
        if(py_a>10):
            py_a = py_a - 11
        
        if(px_a<0):
            px_a = 7 + px_a
        if(py_a<0):
            py_a = 11 + py_a
        
        
        if(grid[px_a][py_a] == 2 or grid[px_a][py_a] == 1):
            break
        if(grid[px_a][py_a] == 3):
            sensor_direita[1] = 1
            break
        else:
            sensor_direita[0]+=1
    
    # Verificando as diagonais
    tras = frente + 2
    if(tras>=4):
        tras-=4
    
    px_a,py_a = (px+    movimentos[direita][0]  + movimentos[frente][0] )  ,  (py+     movimentos[direita][1]  + movimentos[frente][1])   
    if(px_a>6):
        px_a = px_a - 7
    if(py_a>10):
        py_a = py_a - 11
    
    if(px_a<0):
        px_a = 7+ px_a
    if(py_a<0):
        py_a = 11 + py_a
    frente_direita = grid[px_a,py_a]

    px_a,py_a =   (px+    movimentos[esquerda][0] + movimentos[frente][0] ) ,   (py+     movimentos[esquerda][1] + movimentos[frente][1])
    if(px_a>6):
        px_a = px_a - 7
    if(py_a>10):
        py_a = py_a - 11
    
    if(px_a<0):
        px_a = 7+ px_a
    if(py_a<0):
        py_a = 11 + py_a
    frente_esquerda = grid[px_a,py_a]

    px_a,py_a =      (px+    movimentos[esquerda][0] + movimentos[tras][0]   ) ,   (py+     movimentos[esquerda][1] + movimentos[tras][1]  )
    if(px_a>6):
        px_a = px_a - 7
    if(py_a>10):
        py_a = py_a - 11
    
    if(px_a<0):
        px_a = 7+ px_a
    if(py_a<0):
        py_a = 11 + py_a
    tras_esqueda = grid[px_a,py_a]


    px_a,py_a=      (px+    movimentos[direita][0]  + movimentos[tras][0]   ) ,   (py+     movimentos[direita][1]  + movimentos[tras][1]  )
    if(px_a>6):
        px_a = px_a - 7
    if(py_a>10):
        py_a = py_a - 11
    
    if(px_a<0):
        px_a = 7+ px_a
    if(py_a<0):
        py_a = 11 + py_a
    tras_direita = grid[px_a,py_a]

    return np.array([frente,sensor_frente[0],sensor_frente[1],sensor_esquerda[0],sensor_esquerda[1],sensor_direita[0],sensor_direita[1],frente_direita,frente_esquerda,tras_direita,tras_esqueda])
model = keras.models.load_model('./model')
last = Action.SOUTH
def agent(obs,config):
    global last
    global model
    state = get_grid_from_obs(obs,config.columns,config.rows)
    state = get_sensors_from_grid(state,config.columns,obs,last,False)
    state = np.reshape(state, [1, 11])
    print(state)
    action =np.argmax(model.predict(state)[0]) 
    actL = []
    for act in Action:
            actL.append(act)

    last = opposite(actL[action])
    return actL[action].name
    