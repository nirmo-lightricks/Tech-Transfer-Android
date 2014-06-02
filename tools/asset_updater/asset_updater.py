# Copyright (c) 2014 Lightricks. All rights reserved.
# Created by Nir Bruner

from os import walk
from os.path import basename
from os.path import dirname
from os.path import splitext
from os.path import getsize
from os.path import join
from os.path import relpath
from distutils.dir_util import copy_tree
from shutil import copy
from PIL import Image
import argparse


def update_assets(input, output):
    for root, dirs, files in walk(input):
        if basename(root) == "assets":
            if basename(dirname(root)) == "Help":
                copy_split_pngs(root, root, output + "/res")
            else:
                copy_tree(root, output + "/res")

        if basename(root) == "assets-beta":
            copy_tree(root, output + "/res-beta")


def copy_split_pngs(base, input, output):
    for root, dirs, files in walk(input):
        for file in files:
            fullpath = join(root, file)
            outputpath = join(output, relpath(fullpath, base))
            if splitext(fullpath)[1] != ".png" or getsize(fullpath) < 102400:
                copy(fullpath, outputpath)
            else:
                copy_split_png(fullpath, dirname(outputpath))
        for dir in dirs:
            copy_split_pngs(base, join(root, dir), output)


def copy_split_png(input, output):
    png = Image.open(input)

    bands = png.split()
    mask = bands[3].point(lambda i: 255 if i == 0 else 0)
    bands[0].paste(0, None, mask)
    bands[1].paste(0, None, mask)
    bands[2].paste(0, None, mask)

    rgb = Image.merge("RGB", (bands[0], bands[1], bands[2]))
    rgbpath = join(output, splitext(basename(input))[0] + "__rgb.jpg")
    rgb.save(rgbpath)

    alpha = bands[3]
    alphapath = join(output, splitext(basename(input))[0] + "__a.jpg")
    alpha.save(alphapath)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Copy assets from Creative's Bar to facetune-android.")
    parser.add_argument('--input-dir', required=True, dest='input', help='input directory')
    parser.add_argument('--output-dir', required=True, dest='output', help='output directory')

    args = parser.parse_args()
    update_assets(args.input, args.output)
