import kaggle_environments
from kaggle_environments import make, evaluate, utils
env = make("hungry_geese", debug=False) #set debug to True to see agent internals each step

env.reset()
agents = ["./agents/submission-ralph-coward.py","./agents/submission-ralph-coward.py", "./agents/submission-ralph-coward.py","./agents/submission-ralph-coward.py"]
env.run(agents)


with open('./game.html','wb') as f:   # Use some reasonable temp name
    f.write(env.render(mode="html",width=700, height=600).encode("UTF-8"))

