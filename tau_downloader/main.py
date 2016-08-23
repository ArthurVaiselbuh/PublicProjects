#!/usr/bin/python3
import requests
from bs4 import BeautifulSoup

import credentials
from bs4 import BeautifulSoup

class TauHandler(object):
    def __init__(self):
        self.session = requests.session()
        self.last_resp = None

    def login(self, credentials):
        BASE = "https://nidp.tau.ac.il"
        LOGIN_PAGE = "http://moodle.tau.ac.il/login/index.php"
        SUCCESS_STRING = 'Your session has been authenticated'

        name_uname = 'Ecom_User_ID'
        name_id = 'Ecom_User_Pid'
        name_pswd = 'Ecom_Password'
        data_dict = {'option':'credential', #some hidden value
                    name_id:credentials.id_num,
                    name_uname:credentials.uname,
                    name_pswd:credentials.pswd
                    }
        self.last_resp = self.session.get("http://moodle.tau.ac.il")
        assert self.last_resp.status_code == 200
        self.last_resp = self.session.get(LOGIN_PAGE)
        assert self.last_resp.status_code == 200
        # find link to login form
        bs = BeautifulSoup(self.last_resp.text, 'lxml')
        iframe = bs.find('iframe')
        content_address = iframe.attrs['src']
        self.last_resp = self.session.get(BASE + content_address)
        bs = BeautifulSoup(self.last_resp.text, 'lxml')
        iframe = bs.find('iframe')
        login_address = iframe.attrs['src']
        self.last_resp = self.session.get(BASE + login_address)
        bs = BeautifulSoup(self.last_resp.text, 'lxml')
        form = bs.find('form')
        login_post = form.attrs['action']
        self.last_resp = self.session.post(login_post, data=data_dict)
        to_find = 'top.location.href='
        start = self.last_resp.text.find(to_find) + len(to_find) + 1
        # find end of next address to get
        end = self.last_resp.text.find("'", start)
        addr = self.last_resp.text[start:end]
        self.last_resp = self.session.get(self.last_resp.url.rsplit("/", 1)[0] + "/" + addr)
        #finally submit some form
        bs = BeautifulSoup(self.last_resp.text, 'lxml')
        form = bs.find("form")
        data = {}
        for child in form.findAll("input"):
            data[child.attrs['name']] = child.attrs['value']
        submit_addr = form.attrs['action'] # need encoding type?
        #finally post!
        self.last_resp = self.session.post(submit_addr, data=data)
        pass




if __name__ == '__main__':
    t = TauHandler()
    t.login(credentials)

