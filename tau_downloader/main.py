#!/usr/bin/python3
import requests
import os
from bs4 import BeautifulSoup

import credentials
from bs4 import BeautifulSoup

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
        self.logged_in = self.last_resp.url == 'http://moodle.tau.ac.il'
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
        courses = bs.findAll(attrs={'class':'courselink'})
        for course in courses:
            link = course.find("a")
            if not link:
                #no link, nothing to download
                continue
            #Create dir with course name.
            name = course.text + "_0"
            idx = 0
            while os.path.exists(os.path.join(basedir, name)):
                idx += 1
                name = name[:-1] + idx
            os.mkdir(os.path.join(basedir, name))
            self.download_course(link.attrs['href'], os.path.join(basedir, name))

    def download_course(self, url, path):
        """Folder must be empty or stuff could get overwritten"""
        self.last_resp = self.get(url)
        bs = BeautifulSoup(self.last_resp.text, 'lxml')
        content = bs.find(attrs={'class':'course-content'})
        sections = content.findAll(attrs={'class':'content'})
        for section in sections.findAll("li"):
            if section.id == 'section-0':
                # Skip general stuff
                continue
            name = section.find(attrs={'class':'sectionname'}).text
            section_dir = os.path.join(path, name)
            os.mkdir(section_dir)
            for link in section.findAll("a"):
                flname = link.find(attrs={'class':'instancename'}).text
                self.download_file(link.attrs['href'] + '&redirect=1', os.path.join(section_dir, flname))


    def download_file(self, url, filename):
        resp = self.get(url, stream=True)
        with open(filename, 'wb') as fl:
            for chunk in resp.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    fl.write(chunk)



if __name__ == '__main__':
    t = TauHandler()
    t.login(credentials)
    t.download_course('http://moodle.tau.ac.il/course/view.php?id=509182998',
                      '/home/arthur/Projects/tau_downloader/test')

