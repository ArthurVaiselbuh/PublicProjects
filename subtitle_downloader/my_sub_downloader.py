#!/usr/bin/python
import xmlrpclib
import logging
import os, sys
import hashlib
import requests
import gzip
import argparse
import time
import traceback
from io import BytesIO
from ReturnThread import ReturnThread

OSUB_UNAME = ''
OSUB_PASSWORD = ''
OSUB_AGENT = "OSTestUserAgent"

#python3 compatibility
if sys.version.startswith("3"):
    raw_input = input

def log_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(traceback.format_exc())
    return wrapper

def get_file_hash_and_size(path, hash_size=64*1024):
    """
    Returns tuple: md5hash of first and last hash_size bits, as well as bytelenght of the file.
    """
    with open(path, 'rb') as fl:
        data = fl.read(hash_size)
        fl.seek(-hash_size, os.SEEK_END)
        data += fl.read(hash_size)
    v_hash = hashlib.md5(data).hexdigest()
    info = os.stat(path)
    size = info.st_size
    return v_hash, size


class SubtitleDownloader(object):
    OPEN_SUBTITLES_API_URL = "http://api.opensubtitles.org/xml-rpc"
    LANGUAGE = 'eng' # Default language.
    CREDENTIALS = (OSUB_UNAME, OSUB_PASSWORD, LANGUAGE, OSUB_AGENT)
    def __init__(self):
        self.proxy = xmlrpclib.ServerProxy(self.OPEN_SUBTITLES_API_URL)
        if self.try_login():
            self.site = 1
        else:
            # In the future should add another possible site
            pass

    def try_login(self):
        try:
            rtn = self.proxy.LogIn(*self.CREDENTIALS)
            self.token = rtn['token']
            return True
        except KeyError:
            logging.error("Return message from opensubtitles does not contain 'token'. Message is:{}".format(rtn))
        except Exception as e:
            logging.error("Unexpected exception: {}".format(e))
            raise

    def download_for_path(self, path, lang='eng', include_subdir=False):
        """
        If given path is a file download subtitles for it.
        If it is a directory download subtitles for every video file in it.
        lang is the language the subtitles should be in.
        if include_subdir is True, every subdirectory will be handled in this manner as well.
        Returs a tuple of integers: (success, all file request).
        """
        logging.info("Begin getting subtitles for:{}".format(path))
        if os.path.isfile(path):
            return (1 if self.get_subtitles_for_file(path, lang) else 0, 1)# 1 or 0 out of 1
        # it is a dir:
        threads = []
        for dirpath, dirnames, fnames in os.walk(path):
            logging.debug("Working in folder:{}".format(dirpath))
            for fname in fnames:
                #Check that it is a video file:
                found = False
                for ext in VIDEO_EXTENTIONS:
                    if fname.endswith(ext):
                        found = True
                        break
                if not found:
                    continue #Not a video file
                fpath = os.path.join(dirpath, fname)
                # spawn thread to make this faster
                t = ReturnThread(target=self.get_subtitles_for_file, args=(fpath, lang))
                t.start()
                threads.append(t)
            if not include_subdir:
                break
        #gather all results
        results = []
        for t in threads:
            #t.join waits for thread to finish and gets it's return value.
            results.append(t.join())
        ret = (results.count(True), len(results))
        logging.info("Finished getting subtitles for {}. result:{}/{}".format(path, ret[0], ret[1]))
        return ret

    @log_error
    def get_subtitles_for_file(self, filepath, lang=None):
        """
        Find and download data for subtitles for given filepath.
        Output file will be filepath - extention + .srt
        """
        #hold proxy for it's own to allow multithreading
        proxy = xmlrpclib.ServerProxy(self.OPEN_SUBTITLES_API_URL)
        if lang is None:
            lang = self.LANGUAGE
        file_hash, bytesize = get_file_hash_and_size(filepath)
        if self.site == 1:
            params = []
            params.append(dict(
                            moviehash=file_hash,
                            moviebytesize=bytesize,
                            sublanguageid=lang
                            ))
            response = proxy.SearchSubtitles(self.token, params)
            data = response['data']
            if data == []:
                logging.warning("No subtitles found for '{}'".format(filepath))
                return False
            url = data[0]['SubDownloadLink']
            extention = data[0]['SubFileName'].rsplit(".", 1)[1]
            new_filename = os.path.join(os.path.dirname(filepath), os.path.basename(filepath).rsplit(".", 1)[0] + "." + extention)
            logging.debug("New filename for subtitle is:'{}'".format(new_filename))
            resp = requests.get(url)
            bio = BytesIO(resp.content)
            # This is entirely in memory, probably not best way.
            try:
                with open(new_filename, 'wb') as fl:
                    gz = gzip.GzipFile(fileobj=bio)
                    fl.write(gz.read())
            except Exception as e:
                logging.error("Error unpacking gzip or writing file:{}".format(e))
            return True
        return False

VIDEO_EXTENTIONS = ['3g2', '3gp', '3gp2', '3gpp', '60d', 'ajp', 'asf', 'asx', 'avchd', 'avi', 'bik', 'bix', 'box', 'cam', 'dat', 'divx', 'dmf', 'dv', 'dvr-ms', 'evo', 'flc', 'fli', 'flic', 'flv', 'flx', 'gvi', 'gvp', 'h264', 'm1v', 'm2p', 'm2ts', 'm2v', 'm4e', 'm4v', 'mjp', 'mjpeg', 'mjpg', 'mkv', 'moov', 'mov', 'movhd', 'movie', 'movx', 'mp4', 'mpe', 'mpeg', 'mpg', 'mpv', 'mpv2', 'mxf', 'nsv', 'nut', 'ogg', 'ogm',
'omf', 'ps', 'qt', 'ram', 'rm', 'rmvb', 'swf', 'ts', 'vfw', 'vid', 'video', 'viv', 'vivo', 'vob', 'vro', 'wm', 'wmv', 'wmx', 'wrap', 'wvx', 'wx', 'x264', 'xvid']



if __name__ == "__main__":
    logging.basicConfig(filename="subtitle_downloader.log", level=logging.DEBUG)
    logging.getLogger().addHandler(logging.StreamHandler())
    logging.info("Begin running at:{}".format(time.ctime()))
    
    ap = argparse.ArgumentParser(description='Download subtitles for directory/video.')
    ap.add_argument('-l', default='eng', help='language of subtitles', dest='lang')
    ap.add_argument(nargs='*', dest='paths')
    args = ap.parse_args()

    paths = args.paths
    # Allow interactive mode
    if not paths:
        paths = raw_input('Path to file/directory for subtitle download:\n').strip('"\' ')
        paths = [paths]

    dldr = SubtitleDownloader()
    success, total = 0,0
    logging.info("Running for paths:{}".format(paths))
    for path in paths:
        res = dldr.download_for_path(path, include_subdir=True, lang=args.lang)
        success += res[0]
        total += res[1]
    logging.info("Finished. Downloaded {}/{}.".format(success, total))
