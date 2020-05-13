import random
import time


def randomSleep(sec: int):
    time.sleep(sec * (random.random() + 1))
