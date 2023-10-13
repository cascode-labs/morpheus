


import subprocess


class cadenceRunner:
    def __init__(self,pin) -> None:
        subprocess.run(["virtuoso", "-nograph"]) 
