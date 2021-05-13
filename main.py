import kaggle_environments
from kaggle_environments import make, evaluate, utils
from pprint import pprint
env1 = make("hungry_geese", debug=False) #set debug to True to see agent internals each step

env1.reset()
agents = ["./agents/submission-ralph-astar.py","./agents/submission-x-astar.py","./agents/submission-ralph-coward.py"]
obs = env1.run(agents)



with open('./game.html','wb') as f:   # Use some reasonable temp name
    f.write(env1.render(mode="html",width=700, height=600).encode("UTF-8"))

