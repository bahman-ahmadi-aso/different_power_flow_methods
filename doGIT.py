import subprocess
import sys
import os
from datetime import date


def doGIT(msg):
    if msg=="":
        msg= str(date.today())
        a=1



    repo_directory = os.getcwd()
    subprocess.run(["git", "add", "."], cwd=repo_directory)
    # commit file
    subprocess.run(["git", "commit", "-m", msg], cwd=repo_directory)
    # push
    subprocess.run(["git", "push","origin",'main'], cwd=repo_directory)  

