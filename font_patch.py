import os
import glob
import pygame
import random
from pygame.freetype import Font


def check_font_support(font_paths, letters):
    pygame.init()
    missing_chars = {}

    for font_path in font_paths:
        font = Font(font_path, 17)
        missing_indices = [
            i for i, metric in enumerate(font.get_metrics(letters)) if metric is None
        ]
        if missing_indices:
            missing_chars[font_path] = missing_indices

    pygame.quit()
    return missing_chars


def main():

    font_dir = "C:\\Users\\Icem1\\PycharmProjects\\SRNEt-Datagen\\Synthtext\\files\\fonts\\japanese"
    font_paths = glob.glob(f"{font_dir}\\**\\*.ttf", recursive=True)

    # random_font = random.choice(font_paths)
    pygame.init()
    # font = Font(random_font, 17)

    for font_path in font_paths:
        text = "гґеєії'еэi'"
        font = Font(font_path, 17)
        metrics = font.get_metrics(text)
        if not all(metrics):
            print(font.path.split('\\')[-1], metrics)

            text = text.replace("ґ", "г")
            text = text.replace("є", "э")  # ukrainian to russian
            text = text.replace("і", "i")  # ukrainian to english
            text = text.replace("ї", "i")  # ukrainian `ї` to english `і`
            new_metrics = font.get_metrics(text)
            if not all(new_metrics):
                print("Still broken", text, new_metrics)
            else:
                print("FIXED", text)
        else:
            print("GOOD", font.path.split('\\')[-1])

if __name__ == '__main__':
    main()
