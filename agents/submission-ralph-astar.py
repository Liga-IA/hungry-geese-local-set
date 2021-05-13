from kaggle_environments.envs.hungry_geese.hungry_geese import Observation, Configuration,Action, row_col
from kaggle_environments.envs.hungry_geese.hungry_geese import adjacent_positions,min_distance
from pprint import pprint
import numpy as np
import pandas as pd
from math import *
from copy import deepcopy

ralph_last_action = [
    None,
    None,
    None,
    None
]

class Path():
    def __init__(self, caminho,next_heu,next_pos):
        self.caminho = caminho
        self.next_p = next_pos
        self.g = len(caminho)
        self.next_heu = next_heu
    def print(self):
        s = "Caminho: "
        for cam in self.caminho:
           s = s + "(" + str(cam[0]) + ","+str(cam[1])+"), " 
        s = s + "next: ("+str(self.next_p[0])+","+str(self.next_p[1]) + ")\n" + "g = " + str(self.g) + "\n" + "next_h = " + str(self.next_heu) +"\n"
        print(s)
class AStar():
    def __init__(self,observation, configuration):
        self.obs = observation
        self.config = configuration
        self.rows = configuration.rows
        self.cols = configuration.columns
        self.player_index = self.obs.index
        self.start = row_col(self.obs.geese[self.player_index][0],self.cols)
        self.mapa = self.get_grid_from_obs()
        self.heu_map = self.heristic()
        self.frontier = []
    
    def walk(self,cam,last):
        pos = cam[len(cam) - 1]
        next_positions = self.vizinhos(pos)
        vizinhos_validos = []
        for next_pos in next_positions:
            action, (row,col) = next_pos
            if(last is not None):
                if(row != last[0] or col != last[1]):
                    vizinhos_validos.append([row,col])
            else:
                vizinhos_validos.append([row,col])
        for vizinho in vizinhos_validos:
            if(self.heu_map[vizinho[0]][vizinho[1]] != -1):
                path = Path(cam,self.heu_map[vizinho[0]][vizinho[1]],vizinho)
                self.frontier.append(path)

    def search(self):
        global ralph_last_action
        self.walk([self.start],ralph_last_action[self.player_index])
        max_exploration = 1000
        aux = 0
        while aux<=max_exploration:
            f = None
            pathd = None
            for p in self.frontier:
                f_n = p.g + p.next_heu
                if(f is not None):
                    if(f>f_n):
                        f = f_n
                        pathd = p
                else:
                    f = f_n
                    pathd = p
            path = deepcopy(pathd)
            if(path is None):
                return None
            self.frontier.remove(pathd)
            cam = deepcopy(path.caminho)
            pos = path.next_p

            if(self.heu_map[pos[0]][pos[1]] == 0):
                print("ACHEI")
                path.print()
                return path

            cam.append(path.next_p)
            self.walk(cam,path.caminho[len(path.caminho) - 1])
            aux = aux +1
        return None
    def vizinhos(self,pos):
        row, col = pos
        candidates = [
            ("NORTH", (row - 1, col)),
            ("SOUTH", (row + 1, col)),
            ("WEST", (row, col - 1)),
            ("EAST", (row, col + 1))
        ]

        resultado = []
        for action, (r, c) in candidates:
            if(r<0):
                r = self.rows + r
            if(r>=self.rows):
                r = self.rows - r

            if(c<0):
                c = self.cols + c
            if(c>=self.cols):
                c = self.cols - c
            
            resultado.append((action,(r,c)))
            '''if 0 <= r < self.height and 0 <= c < self.width and not self.paredes[r][c]:
                resultado.append((action, (r, c)))
            '''
        return resultado

    def get_grid_from_obs(self):
        # 0: Livre
        # 1: Cabeça
        # 2: "Parede" (inimigos ou a ultima posicao)
        # 3: Comida (Objetivo)

        global ralph_last_action
        last_pos = ralph_last_action[self.player_index]
        mapa = []
        row = []
        for i in range(0,self.rows):
            mapa.append([])

            for j in range(0,self.cols):
                achou = False
                
                for food in self.obs['food']:
                    x,y = row_col(food,self.cols)
                    if(x == i and y == j):
                        mapa[i].append(3)
                        achou = True
                        break
                if(achou):
                    continue
                if(last_pos):
                    if(last_pos[0] == i and last_pos[1] == j):
                        mapa[i].append(2)
                        continue
                for goose in self.obs['geese']:
                    gs = 2
                    for part in goose:
                        x,y = row_col(part,self.cols)
                        if(x == i and y == j):
                            if(gs == 1 and last_pos == ralph_last_action[self.player_index]):
                                ralph_last_action[self.player_index] = [i,j]
                            mapa[i].append(gs)
                            achou = True
                            break
                    if(achou):
                        break
                if(achou):
                    continue
                mapa[i].append(0)
        pprint(mapa)
        print()
        for goose in self.obs.geese:
            if(len(goose)==0):
                continue
            x,y = row_col(goose[0],self.cols)
            if( x == self.start[0] and y == self.start[1]):
                continue
            viz = self.vizinhos([x,y])
            for v in viz:
                action, (row,col) = v
                mapa[row][col] = 2
        pprint(mapa)
        return np.array(mapa)

    def border_distance(self,p,lim):
        d = 0
        if(lim/2 < p):
            d = lim - p
        else:
            d = p
        return d
    def distance(self,x1,y1,x2,y2):
        d1 = sqrt((x1-x2)**2)
        d2 = sqrt((y1-y2)**2)

        dx1 = self.border_distance(x1, self.rows)
        dx2 = self.border_distance(x2, self.rows)

        
        dy1 = self.border_distance(y1, self.cols)
        dy2 = self.border_distance(y2, self.cols)
        
        if(dx1+dx2<d1):
            d1 = dx1+dx2
        if(dy1+dy2<d2):
            d2 = dy1+dy2

        return  d1 + d2
    def heristic(self):
        heu = []
        foodPos = []
        for food in self.obs['food']:
            x,y = row_col(food,self.cols)
            foodPos.append([x,y])

        for i in range(0,self.mapa.shape[0]):
            
            heu.append([])
            for j in range(0,self.mapa.shape[1]):
                tp = self.mapa[i][j]
                if(tp == 2):
                    heu[i].append(-1)
                    continue
                else:
                    d = 1000000
                    for pos in foodPos:
                        if(d>self.distance(i, j, pos[0], pos[1])):
                            d = self.distance(i, j, pos[0], pos[1])
                    heu[i].append(d)
        
        return np.array(heu,dtype="int32")
def get_choice(path, pos,rows,cols):
    row = pos[0]
    col = pos[1]
    candidates = [
            ("NORTH", (row - 1, col)),
            ("SOUTH", (row + 1, col)),
            ("WEST", (row, col - 1)),
            ("EAST", (row, col + 1))
        ]

    resultado = []
    for action, (r, c) in candidates:
        if(r<0):
            r = rows + r
        if(r>=rows):
            r = rows - r

        if(c<0):
            c = cols + c
        if(c>=cols):
            c = cols - c
        
        if(r == path[0] and c == path[1]):
            return action
def opposite(action):
    if action == Action.NORTH.name:
        return Action.SOUTH.name
    if action == Action.SOUTH.name:
        return Action.NORTH.name
    if action == Action.EAST.name:
        return Action.WEST.name
    if action == Action.WEST.name:
        return Action.EAST.name

def agent(obs_dict,config_dict):
    global ralph_last_action
    
    #np.set_printoptions(precision=2)
    observation = Observation(obs_dict)
    configuration = Configuration(config_dict)

    astar = AStar(observation, configuration)
    path = astar.search()
    choice = "WEST"
    if(path is not None):
        cam = []
        if(len(path.caminho)>1):
            cam = path.caminho[1]
        else:
            cam = path.next_p
        choice = get_choice(cam,astar.start,astar.rows,astar.cols)
        print(choice)
        '''for line in astar.heu_map:
            print(line)'''
    else:
        if(ralph_last_action[observation.index] is not None):
            choice = opposite(
            get_choice(ralph_last_action[observation.index],astar.start,astar.rows,astar.cols)
            )
        else:
            coice = "WEST"
    
    
        print()
        print()
        print()
    ralph_last_action[observation.index] = astar.start
    return choice