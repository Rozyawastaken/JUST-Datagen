"""
rendering standard text.
Copyright (c) 2019 Netease Youdao Information Technology Co.,Ltd.
Licensed under the GPL License (see LICENSE for details)
Written by Yu Qian
"""
import pygame
import pygame.locals
from pygame import freetype
import numpy as np
import cv2
import glob
import os

# def render_normal(font, text):
#     line_spacing = font.get_sized_height() + 1
#     line_bounds = font.get_rect(text)
#     fsize = (round(2.0 * line_bounds.width), round(1.25 * line_spacing))
#     surf = pygame.Surface(fsize, pygame.locals.SRCALPHA, 32)
#     x, y = 0, line_spacing
#
#     rect = font.render_to(surf, (x, y), text)
#     rect.x = x + rect.x
#     rect.y = y - rect.y
#
#     surf = pygame.surfarray.pixels_alpha(surf).swapaxes(0, 1)
#     loc = np.where(surf > 20)
#     miny, minx = np.min(loc[0]), np.min(loc[1])
#     maxy, maxx = np.max(loc[0]), np.max(loc[1])
#     return surf[miny:maxy+1, minx:maxx+1], rect


def render_normal(font, text):
    line_spacing = font.get_sized_height() + 1
    line_bounds = font.get_rect(text)
    fsize = (round(2.0 * line_bounds.width), round(1.25 * line_spacing))
    surf = pygame.Surface(fsize, pygame.locals.SRCALPHA, 32)
    x, y = 0, line_spacing

    for char in text:
        if char in ("э", "Э"):
            temp_surf = pygame.Surface((font.get_rect(char).width, line_spacing), pygame.locals.SRCALPHA, 32)
            font.render_to(temp_surf, (0, line_spacing), char)
            temp_surf = pygame.transform.flip(temp_surf, True, False)  # Flip horizontally
            surf.blit(temp_surf, (x, 0))  # Paste flipped char
        else:
            font.render_to(surf, (x, y), char)

        x += font.get_rect(char).width  # Move to next character position

    surf = pygame.surfarray.pixels_alpha(surf).swapaxes(0, 1)
    loc = np.where(surf > 20)
    miny, minx = np.min(loc[0]), np.min(loc[1])
    maxy, maxx = np.max(loc[0]), np.max(loc[1])
    return surf[miny:maxy + 1, minx:maxx + 1], font.get_rect(text)


def make_standard_text(font_path, text, shape, padding = 0.1, color = (0, 0, 0), init_fontsize = 25):
    font = freetype.Font(font_path)
    font.antialiased = True
    font.origin = True
    fontsize = init_fontsize
    font.size = fontsize
    text = preprocess_text(font, text)
    pre_remain = None
    if padding < 1:
        border = int(min(shape) * padding)
    else:
        border = int(padding)
    target_shape = tuple(np.array(shape) - 2 * border)
    while True:
        rect = font.get_rect(text)
        res_shape = tuple(np.array(rect[1:3]))
        remain = np.min(np.array(target_shape) - np.array(res_shape))
        if pre_remain is not None:
            m = pre_remain * remain
            if m <= 0:
                if m < 0 and remain < 0:
                    fontsize -= 1
                if m == 0 and remain != 0:
                    if remain < 0:
                        fontsize -= 1
                    elif remain > 0:
                        fontsize += 1
                break
        if remain < 0:
            if fontsize == 2:
                break
            fontsize -= 1
        else:
            fontsize += 1
        pre_remain = remain
        font.size = fontsize

    surf, rect = render_normal(font, text)
    if np.max(np.array(surf.shape) - np.array(target_shape)) > 0:
        scale = np.min(np.array(target_shape, dtype = np.float32) / np.array(surf.shape, dtype = np.float32))
        to_shape = tuple((np.array(surf.shape) * scale).astype(np.int32)[::-1])
        surf = cv2.resize(surf, to_shape)
    canvas = np.zeros(shape, dtype = np.uint8)
    tly, tlx = int((shape[0] - surf.shape[0]) // 2), int((shape[1] - surf.shape[1]) // 2)
    canvas[tly:tly+surf.shape[0], tlx:tlx+surf.shape[1]] = surf
    canvas = ((1. - canvas.astype(np.float32) / 255.) * 127.).astype(np.uint8)

    return cv2.cvtColor(canvas, cv2.COLOR_GRAY2RGB)


def preprocess_text(font, text):
    if all(font.get_metrics(text)):
        return text

    text = text.replace("ґ", "г").replace("Ґ", "Г")
    text = text.replace("є", "e").replace("Є", "E")  # ukrainian to russian
    # text = text.replace("є", "э").replace("Є", "Э")  # ukrainian to russian
    text = text.replace("і", "i").replace("І", "I")  # ukrainian to english
    text = text.replace("ї", "i").replace("Ї", "I")  # ukrainian `ї` to english `і`

    if all(font.get_metrics(text)):
        return text
    else:
        print("Still wrong", font.path, text)

    raise ValueError("Font is still broken:", font.path, text)


def main():
    pygame.init()
    freetype.init()

    cur_file_path = os.path.dirname(__file__)
    standard_font_path = 'files\\fonts\\japanese\\Noto_Serif_JP\\static\\NotoSerifJP-Regular.ttf'

    font = os.path.join(cur_file_path, standard_font_path)

    text = "абвгґдеєжзиіїйклмнопрстуфхцчшцьюя'iэ"
    shape = (224, 448)
    i_t = make_standard_text(font, text, shape)
    cv2.imshow('i_t', i_t)
    cv2.waitKey()

if __name__ == '__main__':
    main()
