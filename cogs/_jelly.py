import os
import random

class Jelly:

    def __init__(self):
        self.images = []

        # set all images in self.images
        for image in os.listdir(r"./images"):
            self.images.append(image)

    async def get_random_jelly(self):
        jelly = random.choice(self.images)
        return f"images/{jelly}"

    if __name__ == "__main__":
        pass