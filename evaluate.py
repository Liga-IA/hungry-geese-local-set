from kaggle_environments import make, evaluate, utils
from pprint import pprint
#import matplotlib.pyplot as plt
from tqdm import tqdm
import plotly.express as px 
import pandas as pd

RalphAstarP = [0]
XAstarP = [0]
cowardP = [0]
ind = [0]
for i in tqdm(range(0,100)):
    env1 = make("hungry_geese", debug=False) #set debug to True to see agent internals each step
    env1.reset()
    configuration = {"rows": 10, "columns": 8}
    agents = ["./agents/submission-ralph-astar.py","./agents/submission-x-astar.py","./agents/submission-ralph-coward.py"]
    steps = env1.run(agents)

    obs = steps[len(steps) - 1][0]["observation"]
    RalphAstar = RalphAstarP[len(RalphAstarP)-1]
    XAstar = XAstarP[len(XAstarP)-1]
    coward = cowardP[len(cowardP)-1]
    geese = obs["geese"]
    if(len(geese[0])>0):
        RalphAstar = RalphAstar + 1
    if(len(geese[1])>0):
        XAstar = XAstar + 1
    if(len(geese[2])>0):
        coward = coward + 1
    cowardP.append(coward)
    RalphAstarP.append(RalphAstar)
    XAstarP.append(XAstar)

    ind.append(len(ind))


df = pd.DataFrame()
df["RalphAstar"] = RalphAstarP
df["XAstar"] = XAstarP
df["Coward"] = cowardP
df["ind"] = ind
fig = px.line(df, x='ind', y=['RalphAstar', 'XAstar',"Coward"])
fig.show()
fig.write_html("plot.html")
