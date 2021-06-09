from kaggle_environments import make, evaluate, utils
from pprint import pprint
#import matplotlib.pyplot as plt
from tqdm import tqdm
import plotly.express as px 
import pandas as pd

agents_points = []
ind = [0]
configuration = {"rows": 10, "columns": 8}
agents_names = ["submission-ralph-astar.py","submission-x-astar.py","submission-ralph-coward.py","submission-ralph-rl.py"]
#agents_names = ["random.py","submission-ralph-rl.py"]
agents = []
for agent in agents_names:
    agents.append("./agents/"+agent)
    agents_points.append([0])
for i in tqdm(range(0,100)):
    env1 = make("hungry_geese", debug=True) #set debug to True to see agent internals each step
    env1.reset()
    
    steps = env1.run(agents)

    obs = steps[len(steps) - 1][0]["observation"]

    round_points = []
    #print()
    #print(agents_points)
    #print()
    #print()
    for i,points in enumerate(agents_points):
        #print(agents_points[i][len(agents_points[i])-1])
        round_points.append(agents_points[i][len(agents_points[i])-1])

    
    #print(round_points)
    
    geese = obs["geese"]

    for i,goose in enumerate(geese):
        #print(i,goose)
        p = round_points[i]
        if(len(goose)>0):
            p = p +1
        agents_points[i].append(p)
            


    ind.append(len(ind))


df = pd.DataFrame()
for i,name in enumerate(agents_names):
    df[name] = agents_points[i]
df["ind"] = ind
fig = px.line(df, x='ind', y=agents_names)
fig.show()
fig.write_html("plot.html")
