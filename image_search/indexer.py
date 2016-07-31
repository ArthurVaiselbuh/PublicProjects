# import the necessary packages
from lib.rgbhistogram import RGBHistogram
import argparse
import cPickle as pickle
import glob
import cv2
import os
 
def parse_args():
    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-d", "--dataset", required = True,
        help = "Path to the directory that contains the images to be indexed")
    ap.add_argument("-i", "--index", required = True,
        help = "Path to where the computed index will be stored")
    args = ap.parse_args()
    return args

def index(dataset, index_path):
    # initialize the index dictionary to store our our quantifed
    # images, with the 'key' of the dictionary being the image
    # filename and the 'value' our computed features
    if not os.path.exists(dataset):
        raise ValueError("Path {} that is meant to be dataset does not exist.".format(dataset))
    index = {}
    # initialize our image descriptor -- a 3D RGB histogram with
    # 8 bins per channel
    desc = RGBHistogram([8, 8, 8])
    # use glob to grab the image paths and loop over them
    for imagePath in glob.glob(os.path.join(dataset, "*.png")):
        # extract our unique image ID (i.e. the filename)
        k = os.path.basename(imagePath)

        # load the image, describe it using our RGB histogram
        # descriptor, and update the index
        image = cv2.imread(imagePath)
        features = desc.describe(image)
        index[k] = features

    # we are now done indexing our image -- now we can write our
    # index to disk
    with open(args.index, "w") as f:
        f.write(pickle.dumps(index))
        f.close()

 
if __name__ == '__main__':
    args = parse_args()
    index(args.dataset, args.index)
