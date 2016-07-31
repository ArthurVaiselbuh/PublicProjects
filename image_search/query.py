#Query Image.
# import the necessary packages
from lib.searcher import Searcher
from lib.rgbhistogram import RGBHistogram
from main import show_top_10
import numpy as np
import argparse
import cPickle as pickle
import cv2
import os
 
def parse_args():
    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-d", "--dataset", required = True,
        help = "Path to the directory that contains the images we just indexed")
    ap.add_argument("-i", "--index", required = True,
        help = "Path to where we stored our index")
    args = ap.parse_args()
    return args

 
def work(args):
    index = pickle.loads(open(args.index).read())
    searcher = Searcher(index)
    desc = RGBHistogram([8, 8, 8])
    path = raw_input("Enter te path to the picture to search:\n").strip(" \" ")
    while os.path.exists(path):
        #First get features of the image.
        image = cv2.imread(path)
        features = desc.describe(image)
        #Now search.
        results = searcher.search(features)
        show_top_10(path, results, args.dataset)
        path = raw_input("Enter the path for the next picture to search:\n").strip(" \" ")


if __name__ == '__main__':
    args = parse_args()
    work(args)