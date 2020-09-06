import os
import random
from datetime import datetime


class Jelly:

    def __init__(self):
        self.image, self.score = get_random_jelly()
        self.channel_id = int()
        self.spawn_time = datetime.now()

    if __name__ == "__main__":
        pass


def get_random_jelly():
    images = []

    # set all images in self.images
    for image in os.listdir(r"./images"):
        images.append(image)
    jelly = random.choice(images)
    score = int(jelly[:2])
    return f"images/{jelly}", score

