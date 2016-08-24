#!/usr/bin/python3
import requests
import os
import logging
import time
from bs4 import BeautifulSoup

import credentials

# file length limit due to os limits
OS_FNAME_LIMIT = 140

def remove_empty_folders(path):
    to_del = []
    for dirpath, dirnames, filenames in os.walk(path):
        pass

def find_free_name(basepath, name, limit=OS_FNAME_LIMIT):
    """
    Find free file/path name for creating a new dir/file.
    limit is max length of final path.
    Return final path.
    """
    # this is linux, remove /
    name = name.replace("/", '')
    full = os.path.join(basepath, name)
    if (not os.path.exists(full)) and len(full) <= limit:
        return full
    if len(full) >= limit - 1:
        diff = len(full) + 1 - limit
        name = name[:-diff]
    idx = 0
    while os.path.exists(os.path.join(basepath, name + "{}".format(idx))):
        idx += 1
        if idx % 10 == 0 and len(os.path.join(basepath, name+"{}".format(idx))) > limit:
            name = name[:-1]
    return os.path.join(basepath, "{}{}".format(name, idx))


class TauHandler(object):
    def __init__(self):
        self.session = requests.session()
        self.last_resp = None
        self.logged_in = False

    def login(self, credentials):
        BASE = "https://nidp.tau.ac.il"
        LOGIN_PAGE = "http://moodle.tau.ac.il/login/index.php"

        name_uname = 'Ecom_User_ID'
        name_id = 'Ecom_User_Pid'
        name_pswd = 'Ecom_Password'
        data_dict = {'option':'credential', #some hidden value
                    name_id:credentials.id_num,
                    name_uname:credentials.uname,
                    name_pswd:credentials.pswd
                    }
        self.last_resp = self.get("http://moodle.tau.ac.il")
        assert self.last_resp.status_code == 200
        self.last_resp = self.get(LOGIN_PAGE)
        assert self.last_resp.status_code == 200
        # find link to login form
        bs = BeautifulSoup(self.last_resp.text, 'lxml')
        iframe = bs.find('iframe')
        content_address = iframe.attrs['src']
        self.last_resp = self.get(BASE + content_address)
        bs = BeautifulSoup(self.last_resp.text, 'lxml')
        iframe = bs.find('iframe')
        login_address = iframe.attrs['src']
        self.last_resp = self.get(BASE + login_address)
        bs = BeautifulSoup(self.last_resp.text, 'lxml')
        form = bs.find('form')
        login_post = form.attrs['action']
        self.last_resp = self.post(login_post, data=data_dict)
        to_find = 'top.location.href='
        start = self.last_resp.text.find(to_find) + len(to_find) + 1
        # find end of next address to get
        end = self.last_resp.text.find("'", start)
        addr = self.last_resp.text[start:end]
        self.last_resp = self.get(self.last_resp.url.rsplit("/", 1)[0] + "/" + addr)
        #finally submit some form
        bs = BeautifulSoup(self.last_resp.text, 'lxml')
        form = bs.find("form")
        data = {}
        for child in form.findAll("input"):
            data[child.attrs['name']] = child.attrs['value']
        submit_addr = form.attrs['action'] # need encoding type?
        #finally post!
        self.last_resp = self.post(submit_addr, data=data)
        self.logged_in = self.last_resp.url.strip('/ ') == 'http://moodle.tau.ac.il'
        return self.logged_in

    def get(self, *args, **kwargs):
        """GET through session. Short for self.session.get"""
        return self.session.get(*args, **kwargs)

    def post(self, *args, **kwargs):
        """POST through session. Short for self.session.post"""
        return self.session.post(*args, **kwargs)

    def download_all_files(self, basedir):
        assert os.path.isdir(basedir)
        assert self.logged_in
        moodle = self.get("http://moodle.tau.ac.il")
        bs = BeautifulSoup(moodle.text, 'lxml')
        courses = bs.findAll(attrs={'class': 'courselink'})
        for course in courses:
            link = course.find("a")
            if not link:
                # no link, nothing to download
                continue
            name = course.text
            # if dir exists skip course
            if os.path.exists(os.path.join(basedir, name)):
                logging.info("Skipping course {}, dir already exists".format(name))
                continue
            os.mkdir(os.path.join(basedir, name))
            self.download_course(link.attrs['href'], os.path.join(basedir, name))

    def download_course(self, url, path):
        """Folder must be empty or stuff could get overwritten"""
        logging.info("Begin downloading course from url {} to: {}".format(url, path))
        self.last_resp = self.get(url)
        bs = BeautifulSoup(self.last_resp.text, 'lxml')
        content = bs.find(attrs={'class': 'course-content'})
        sections = content.findAll(attrs={'class': 'content'})
        for section in sections:
            node = section.find(attrs={'class': 'sectionname'})
            if node is None:
                logging.warning('Did not find section name for section id "{}"'.format(section.id))
                continue
            name = node.text
            section_dir = find_free_name(path, name)
            os.mkdir(section_dir)
            for link in section.findAll("a"):
                node = link.find(attrs={'class': 'instancename'})
                if node is None:
                    logging.warning("No name found for {}".format(link.attrs['href']))
                    continue
                flname = node.text
                flpath = find_free_name(section_dir, flname)
                self.download_file(link.attrs['href'] + '&redirect=1', flpath)
        logging.info("Finished downloading course to {}".format(path))

    def download_file(self, url, filename):
        resp = self.get(url, stream=True)
        logging.info("Downloading file: {}")
        with open(filename, 'wb') as fl:
            for chunk in resp.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    fl.write(chunk)



if __name__ == '__main__':
    logging.basicConfig(filename="tau_downloader.log", level=logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler())
    logging.info("Begin running at:{}".format(time.ctime()))

    t = TauHandler()
    t.login(credentials)
    t.download_all_files('/home/arthur/Projects/tau_downloader/testall')

