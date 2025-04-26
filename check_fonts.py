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
    letters = "абвгґдеєжзиіїйклмнопрстуфхцчшщьюя'абвгдеэжзиiйклмнопрстуфхцчшщьюя'"
    fonts_to_fix = check_font_support(font_paths, letters)
    print("Total fonts:", len(font_paths))
    for font, chars in fonts_to_fix.items():
        font = font.split('\\')[-1]
        if chars != [4, 7, 11, 12]:
            print(font, chars, [letters[c] for c in chars])
    print(len(fonts_to_fix))
    # before: 158
    # after: 113
    # removed:
    # MochiyPopOne-Regular.ttf,
    # MochiyPopPOne-Regular.ttf,
    # MPLUS1/,
    # MPLUS1Code/,
    # MPLUS2/,
    # NewTegomin-Regular
    # PottaOne-Regular.ttf
    # ShipporiAntique-Regular.ttf
    # ShipporiAntiqueB1-Regular.ttf
    # Shippori_Mincho/
    # Shippori_Mincho_B1/
    # YuseiMagic-Regular.ttf

if __name__ == '__main__':
    main()
