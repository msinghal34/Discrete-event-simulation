import yaml
import sys
import os

os.system("python3 main.py")
with open("config.yaml", 'r') as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
exclusion = 2*int(config["num_users"])
os.system("python3 script.py " + str(exclusion))