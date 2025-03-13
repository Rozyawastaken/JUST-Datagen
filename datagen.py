"""
Generating data for SRNet
Copyright (c) 2019 Netease Youdao Information Technology Co.,Ltd.
Licensed under the GPL License (see LICENSE for details)
Written by Yu Qian
"""

import os
import cv2
import cfg
from Synthtext.gen import datagen, multiprocess_datagen


def makedirs(path):
    if not os.path.exists(path):
        os.makedirs(path)


def main():

    bg_img_dir = os.path.join(cfg.data_dir, cfg.bg_img_dir)
    source_text_dir = os.path.join(cfg.data_dir, cfg.source_text_dir)
    target_text_dir = os.path.join(cfg.data_dir, cfg.target_text_dir)
    source_img_dir = os.path.join(cfg.data_dir, cfg.source_img_dir)
    target_img_dir = os.path.join(cfg.data_dir, cfg.target_img_dir)
    source_img_grey_dir = os.path.join(cfg.data_dir, cfg.source_img_grey_dir)
    target_img_grey_dir = os.path.join(cfg.data_dir, cfg.target_img_grey_dir)
    source_img_styled_dir = os.path.join(cfg.data_dir, cfg.source_img_styled_dir)
    target_img_styled_dir = os.path.join(cfg.data_dir, cfg.target_img_styled_dir)
    source_sk_dir = os.path.join(cfg.data_dir, cfg.source_sk_dir)
    target_sk_dir = os.path.join(cfg.data_dir, cfg.target_sk_dir)
    source_mask_dir = os.path.join(cfg.data_dir, cfg.source_mask_dir)
    target_mask_dir = os.path.join(cfg.data_dir, cfg.target_mask_dir)

    makedirs(bg_img_dir)
    makedirs(source_text_dir)
    makedirs(target_text_dir)
    makedirs(source_img_dir)
    makedirs(target_img_dir)
    makedirs(source_img_grey_dir)
    makedirs(target_img_grey_dir)
    makedirs(source_img_styled_dir)
    makedirs(target_img_styled_dir)
    makedirs(source_sk_dir)
    makedirs(target_sk_dir)
    makedirs(source_mask_dir)
    makedirs(target_mask_dir)

    mp_gen = multiprocess_datagen(cfg.process_num, cfg.data_capacity)
    mp_gen.multiprocess_runningqueue()
    digit_num = len(str(cfg.sample_num)) - 1
    for idx in range(cfg.sample_num):
        print("Generating step {:>6d} / {:>6d}".format(idx + 1, cfg.sample_num))
        (
            bg_img,
            source_text, target_text,
            source_img, target_img,
            source_img_grey, target_img_grey,
            source_img_styled, target_img_styled,
            source_sk, target_sk,
            source_mask, target_mask
        ) = mp_gen.dequeue_data()

        bg_img_path = os.path.join(bg_img_dir, str(idx).zfill(digit_num) + '.png')
        source_text_path = os.path.join(source_text_dir, str(idx).zfill(digit_num) + '.png')
        target_text_path = os.path.join(target_text_dir, str(idx).zfill(digit_num) + '.png')
        source_img_path = os.path.join(source_img_dir, str(idx).zfill(digit_num) + '.png')
        target_img_path = os.path.join(target_img_dir, str(idx).zfill(digit_num) + '.png')
        source_img_grey_path = os.path.join(source_img_grey_dir, str(idx).zfill(digit_num) + '.png')
        target_img_grey_path = os.path.join(target_img_grey_dir, str(idx).zfill(digit_num) + '.png')
        source_img_styled_path = os.path.join(source_img_styled_dir, str(idx).zfill(digit_num) + '.png')
        target_img_styled_path = os.path.join(target_img_styled_dir, str(idx).zfill(digit_num) + '.png')
        source_sk_path = os.path.join(source_sk_dir, str(idx).zfill(digit_num) + '.png')
        target_sk_path = os.path.join(target_sk_dir, str(idx).zfill(digit_num) + '.png')
        source_mask_path = os.path.join(source_mask_dir, str(idx).zfill(digit_num) + '.png')
        target_mask_path = os.path.join(target_mask_dir, str(idx).zfill(digit_num) + '.png')


        cv2.imwrite(bg_img_path, bg_img, [int(cv2.IMWRITE_PNG_COMPRESSION), 0])
        print(source_text, target_text)

        cv2.imwrite(source_img_path, source_img, [int(cv2.IMWRITE_PNG_COMPRESSION), 0])
        cv2.imwrite(target_img_path, target_img, [int(cv2.IMWRITE_PNG_COMPRESSION), 0])

        cv2.imwrite(source_img_grey_path, source_img_grey, [int(cv2.IMWRITE_PNG_COMPRESSION), 0])
        cv2.imwrite(target_img_grey_path, target_img_grey, [int(cv2.IMWRITE_PNG_COMPRESSION), 0])

        cv2.imwrite(source_img_styled_path, source_img_styled, [int(cv2.IMWRITE_PNG_COMPRESSION), 0])
        cv2.imwrite(target_img_styled_path, target_img_styled, [int(cv2.IMWRITE_PNG_COMPRESSION), 0])

        cv2.imwrite(source_sk_path, source_sk, [int(cv2.IMWRITE_PNG_COMPRESSION), 0])
        cv2.imwrite(target_sk_path, target_sk, [int(cv2.IMWRITE_PNG_COMPRESSION), 0])

        cv2.imwrite(source_mask_path, source_mask, [int(cv2.IMWRITE_PNG_COMPRESSION), 0])
        cv2.imwrite(target_mask_path, target_mask, [int(cv2.IMWRITE_PNG_COMPRESSION), 0])

    mp_gen.terminate_pool()


if __name__ == '__main__':
    main()
