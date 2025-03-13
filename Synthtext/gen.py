# -*- coding: utf-8 -*-
"""
SRNet data generator.
Copyright (c) 2019 Netease Youdao Information Technology Co.,Ltd.
Licensed under the GPL License (see LICENSE for details)
Written by Yu Qian
"""

import os
import cv2
import math
import glob
import numpy as np
import pandas as pd
import pygame
from pygame import freetype
import random
import multiprocessing
import queue
import Augmentor

from . import render_text_mask
from . import colorize
from . import skeletonization
from . import render_standard_text
from . import data_cfg


class datagen():

    def __init__(self):
        
        freetype.init()
        cur_file_path = os.path.dirname(__file__)

        font_dir = os.path.join(cur_file_path, data_cfg.font_dir)
        self.font_list = glob.glob(os.path.join(font_dir, '**', '*.ttf'), recursive=True)
        self.standard_font_path = os.path.join(cur_file_path, data_cfg.standard_font_path)
        
        color_filepath = os.path.join(cur_file_path, data_cfg.color_filepath)
        self.colorsRGB, self.colorsLAB = colorize.get_color_matrix(color_filepath)
        
        words_filepath = os.path.join(cur_file_path, data_cfg.words_filepath)
        self.words_df = pd.read_parquet(words_filepath)
        
        bg_filepath = os.path.join(cur_file_path, data_cfg.bg_filepath)
        self.bg_list = open(bg_filepath, 'r').readlines()
        self.bg_list = [img_path.strip() for img_path in self.bg_list]
        
        self.surf_augmentor = Augmentor.DataPipeline(None)
        self.surf_augmentor.random_distortion(probability = data_cfg.elastic_rate, grid_width = data_cfg.elastic_grid_size, grid_height = data_cfg.elastic_grid_size, magnitude = data_cfg.elastic_magnitude)
        
        self.bg_augmentor = Augmentor.DataPipeline(None)
        self.bg_augmentor.random_brightness(probability = data_cfg.brightness_rate, min_factor = data_cfg.brightness_min, max_factor = data_cfg.brightness_max)
        self.bg_augmentor.random_color(probability = data_cfg.color_rate, min_factor = data_cfg.color_min, max_factor = data_cfg.color_max)
        self.bg_augmentor.random_contrast(probability = data_cfg.contrast_rate, min_factor = data_cfg.contrast_min, max_factor = data_cfg.contrast_max)

    def gen_srnet_data_with_background(self):
        
        while True:
            # choose font, text and bg
            font = np.random.choice(self.font_list)
            random_row = self.words_df.sample(n=1)
            text1, text2 = random_row["japanese"].iloc[0], random_row["ukrainian"].iloc[0]

            # No need to capitalize

            # upper_rand = np.random.rand()
            # if upper_rand < data_cfg.capitalize_rate + data_cfg.uppercase_rate:
            #     text1, text2 = text1.capitalize(), text2.capitalize()
            # if upper_rand < data_cfg.uppercase_rate:
            #     text1, text2 = text1.upper(), text2.upper()
            bg = cv2.imread(random.choice(self.bg_list))

            # init font
            font = freetype.Font(font)
            font.antialiased = True
            font.origin = True

            # choose font style
            font.size = np.random.randint(data_cfg.font_size[0], data_cfg.font_size[1] + 1)
            font.underline = np.random.rand() < data_cfg.underline_rate
            font.strong = np.random.rand() < data_cfg.strong_rate
            font.oblique = np.random.rand() < data_cfg.oblique_rate

            text2 = render_standard_text.preprocess_text(font, text2)

            # render text to surf
            param = {
                        'is_curve': np.random.rand() < data_cfg.is_curve_rate,
                        'curve_rate': data_cfg.curve_rate_param[0] * np.random.randn() 
                                      + data_cfg.curve_rate_param[1],
                        'curve_center': np.random.randint(0, len(text1))
                    }
            surf1, bbs1 = render_text_mask.render_text(font, text1, param)
            param['curve_center'] = int(param['curve_center'] / len(text1) * len(text2))
            surf2, bbs2 = render_text_mask.render_text(font, text2, param)

            # get padding
            padding_ud = np.random.randint(data_cfg.padding_ud[0], data_cfg.padding_ud[1] + 1, 2)
            padding_lr = np.random.randint(data_cfg.padding_lr[0], data_cfg.padding_lr[1] + 1, 2)
            padding = np.hstack((padding_ud, padding_lr))

            # perspect the surf
            rotate = data_cfg.rotate_param[0] * np.random.randn() + data_cfg.rotate_param[1]
            zoom = data_cfg.zoom_param[0] * np.random.randn(2) + data_cfg.zoom_param[1]
            shear = data_cfg.shear_param[0] * np.random.randn(2) + data_cfg.shear_param[1]
            perspect = data_cfg.perspect_param[0] * np.random.randn(2) +data_cfg.perspect_param[1]
            surf1 = render_text_mask.perspective(surf1, rotate, zoom, shear, perspect, padding) # w first
            surf2 = render_text_mask.perspective(surf2, rotate, zoom, shear, perspect, padding) # w first

            # choose a background
            surf1_h, surf1_w = surf1.shape[:2]
            surf2_h, surf2_w = surf2.shape[:2]
            surf_h = max(surf1_h, surf2_h)
            surf_w = max(surf1_w, surf2_w)
            surf1 = render_text_mask.center2size(surf1, (surf_h, surf_w))
            surf2 = render_text_mask.center2size(surf2, (surf_h, surf_w))

            bg_h, bg_w = bg.shape[:2]
            if bg_w < surf_w or bg_h < surf_h:
                continue
            x = np.random.randint(0, bg_w - surf_w + 1)
            y = np.random.randint(0, bg_h - surf_h + 1)
            bg_img = bg[y:y+surf_h, x:x+surf_w, :]
            
            # augment surf
            surfs = [[surf1, surf2]]
            self.surf_augmentor.augmentor_images = surfs
            surf1, surf2 = self.surf_augmentor.sample(1)[0]
            
            # bg augment
            bg_imgs = [[bg_img]]
            self.bg_augmentor.augmentor_images = bg_imgs
            bg_img = self.bg_augmentor.sample(1)[0][0]

            # render standard text
            source_img_grey = render_standard_text.make_standard_text(self.standard_font_path, text1, (surf_h, surf_w))
            target_img_grey = render_standard_text.make_standard_text(self.standard_font_path, text2, (surf_h, surf_w))

            # get min h of bbs
            min_h1 = np.min(bbs1[:, 3])
            min_h2 = np.min(bbs2[:, 3])
            min_h = min(min_h1, min_h2)

            # get font color
            if np.random.rand() < data_cfg.use_random_color_rate:
                fg_col, bg_col = (np.random.rand(3) * 255.).astype(np.uint8), (np.random.rand(3) * 255.).astype(np.uint8)
            else:
                fg_col, bg_col = colorize.get_font_color(self.colorsRGB, self.colorsLAB, bg_img)

            # colorful the surf and conbine foreground and background
            param = {
                'is_border': np.random.rand() < data_cfg.is_border_rate,
                'bordar_color': tuple(np.random.randint(0, 256, 3)),
                'is_shadow': np.random.rand() < data_cfg.is_shadow_rate,
                'shadow_angle': np.pi / 4 * np.random.choice(data_cfg.shadow_angle_degree) + data_cfg.shadow_angle_param[0] * np.random.randn(),
                'shadow_shift': data_cfg.shadow_shift_param[0, :] * np.random.randn(3) + data_cfg.shadow_shift_param[1, :],
                'shadow_opacity': data_cfg.shadow_opacity_param[0] * np.random.randn() + data_cfg.shadow_opacity_param[1]
            }
            source_img_styled, source_img = colorize.colorize(surf1, bg_img, fg_col, bg_col, self.colorsRGB, self.colorsLAB, min_h, param)
            target_img_styled, target_img = colorize.colorize(surf2, bg_img, fg_col, bg_col, self.colorsRGB, self.colorsLAB, min_h, param)
            
            # skeletonization
            source_sk = skeletonization.skeletonization(surf1, 127)
            target_sk = skeletonization.skeletonization(surf2, 127)
            break
   
        return [bg_img, text1, text2, source_img, target_img, source_img_grey, target_img_grey, source_img_styled, target_img_styled,  source_sk, target_sk, surf1, surf2]


def enqueue_data(queue, capacity):  
    np.random.seed()
    gen = datagen()
    while True:
        try:
            data = gen.gen_srnet_data_with_background()
        except Exception as e:
            print(e)
        if queue.qsize() < capacity:
            queue.put(data)

class multiprocess_datagen():
    
    def __init__(self, process_num, data_capacity):
        
        self.process_num = process_num
        self.data_capacity = data_capacity
            
    def multiprocess_runningqueue(self):
        
        manager = multiprocessing.Manager()
        self.queue = manager.Queue()
        self.pool = multiprocessing.Pool(processes = self.process_num)
        self.processes = []
        for _ in range(self.process_num):
            p = self.pool.apply_async(enqueue_data, args = (self.queue, self.data_capacity))
            self.processes.append(p)
        self.pool.close()
        
    def dequeue_data(self):
        
        while self.queue.empty():
            pass
        data = self.queue.get()
        return data
        '''
        data = None
        if not self.queue.empty():
            data = self.queue.get()
        return data
        '''

    def dequeue_batch(self, batch_size, data_shape):
        
        while self.queue.qsize() < batch_size:
            pass

        bg_img_batch = []
        source_text_batch, target_text_batch = [], []
        source_img_grey_batch, target_img_grey_batch = [], []
        source_img_styled_batch, target_img_styled_batch = [], []
        source_img_batch, target_img_batch = [], []
        source_sk_batch, target_sk_batch = [], []
        source_mask_batch, target_mask_batch = [], []
        
        for i in range(batch_size):
            (
                bg_img,
                source_text, target_text,
                source_img, target_img,
                source_img_grey, target_img_grey,
                source_img_styled, target_img_styled,
                source_sk, target_sk,
                source_mask, target_mask
            ) = self.dequeue_data()

            bg_img_batch.append(bg_img)

            source_text_batch.append(source_text)
            target_text_batch.append(target_text)

            source_img_grey_batch.append(source_img_grey)
            target_img_grey_batch.append(target_img_grey)

            source_img_styled_batch.append(source_img_styled)
            target_img_styled_batch.append(target_img_styled)

            source_img_batch.append(source_img)
            target_img_batch.append(target_img)

            source_sk_batch.append(source_sk)
            target_sk_batch.append(target_sk)

            source_mask_batch.append(source_mask)
            target_mask_batch.append(target_mask)

        w_sum = 0
        for bg_img in bg_img_batch:
            h, w = bg_img.shape[:2]
            scale_ratio = data_shape[0] / h
            w_sum += int(w * scale_ratio)
        
        to_h = data_shape[0]
        to_w = w_sum // batch_size
        to_w = int(round(to_w / 8)) * 8
        to_size = (to_w, to_h) # w first for cv2
        for i in range(batch_size): 
            bg_img_batch[i] = cv2.resize(bg_img_batch[i], to_size)
            source_img_batch[i] = cv2.resize(source_img_batch[i], to_size)
            target_img_batch[i] = cv2.resize(target_img_batch[i], to_size)

            source_img_grey_batch[i] = cv2.resize(source_img_grey_batch[i], to_size)
            target_img_grey_batch[i] = cv2.resize(target_img_grey_batch[i], to_size)

            source_img_styled_batch[i] = cv2.resize(source_img_styled_batch[i], to_size)
            target_img_styled_batch[i] = cv2.resize(target_img_styled_batch[i], to_size)

            source_sk_batch[i] = cv2.resize(source_sk_batch[i], to_size, interpolation=cv2.INTER_NEAREST)
            target_sk_batch[i] = cv2.resize(target_sk_batch[i], to_size, interpolation=cv2.INTER_NEAREST)

            source_mask_batch[i] = cv2.resize(source_mask_batch[i], to_size, interpolation=cv2.INTER_NEAREST)
            target_mask_batch[i] = cv2.resize(target_mask_batch[i], to_size, interpolation=cv2.INTER_NEAREST)

            # eliminate the effect of resize on t_sk
            source_sk_batch[i] = skeletonization.skeletonization(source_mask_batch[i], 127)
            target_sk_batch[i] = skeletonization.skeletonization(target_mask_batch[i], 127)

        bg_img_batch = np.stack(bg_img_batch).astype(np.float32) / 127.5 - 1.

        source_text_batch = np.stack(source_text_batch)
        target_text_batch = np.stack(target_text_batch)

        source_img_batch = np.stack(source_img_batch).astype(np.float32) / 127.5 - 1.
        target_img_batch = np.stack(target_img_batch).astype(np.float32) / 127.5 - 1.

        source_img_grey_batch = np.stack(source_img_grey_batch).astype(np.float32) / 127.5 - 1.
        target_img_grey_batch = np.stack(target_img_grey_batch).astype(np.float32) / 127.5 - 1.

        source_img_styled_batch = np.stack(source_img_styled_batch).astype(np.float32) / 127.5 - 1.
        target_img_styled_batch = np.stack(target_img_styled_batch).astype(np.float32) / 127.5 - 1.

        source_sk_batch = np.expand_dims(np.stack(source_sk_batch), axis=-1).astype(np.float32) / 255.
        target_sk_batch = np.expand_dims(np.stack(target_sk_batch), axis=-1).astype(np.float32) / 255.

        source_mask_batch = np.expand_dims(np.stack(source_mask_batch), axis=-1).astype(np.float32) / 255.
        target_mask_batch = np.expand_dims(np.stack(target_mask_batch), axis=-1).astype(np.float32) / 255.

        return [
            bg_img_batch,
            source_text_batch, target_text_batch,
            source_img_batch, target_img_batch,
            source_img_grey_batch, target_img_grey_batch,
            source_img_styled_batch, target_img_styled_batch,
            source_sk_batch, target_sk_batch,
            source_mask_batch, target_mask_batch
        ]
    
    def get_queue_size(self):
        
        return self.queue.qsize()
    
    def terminate_pool(self):
        
        self.pool.terminate()
