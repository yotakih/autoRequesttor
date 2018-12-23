#-*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import codecs
import requests
import sys
import time
import threading


class Script_invoker(threading.Thread):
    '''
    invoke script
    '''
    def __init__(self, script_reader, form_define_reader, alias_variants):
        self.id = hex(id(self))
        self.kill = False
        self.script_reader = script_reader
        self.form_define_reader = form_define_reader
        self.alias_variants = alias_variants
        self.head_url = self.script_reader.get_head_url()

    def run(self):
        while not self.kill:
            try:
                res = self._get_top_page()
                for think_time, form_name in self.script_reader.get_script_list():
                    if not res.ok:
                        raise Exception('error status: %s url; %s' % (res.status_code, res.url))
                    time.sleep(think_time)
                    res = self._post(form_name, res)
                    if self.kill:
                        break
            except Exception as e:
                self.print_error(str(e))

    def print_error(message):
        print('[!] %s : %s' % (self.id, str(message)))

    def _get_top_page(self):
        res = requests.get(self.script_reader.get_top_url)
        return res

    def _post(self, form_name, before_res):
        url = self._get_url(before_res, form_name)
        data = self.form_define_reader.create_payload(form_name, before_res)
        return requests.post(url=url, cookies=before_res.cookies, data=data)

    def _get_url(self, res, form_name):
        try:
            parser = BeautifulSoup(res.text, 'html.parser')
            return self.head_url + parser.select('form[name=%s]' % (form_name, ))[0].attrs['action']
        except Exception as e:
            raise Exception('form not found: %s' % (form_name, ))


class Script_reader():
    '''
    read script file
    '''
    def __init__(self, script_file):
        self.script = self._read_scirpt_file(script_file)

    def _read_scirpt_file(self, script_file):
        ret = {}
        return ret

    def get_head_url(self):
        return self.script['head_url']

    def get_top_url(self):
        return self.script['top_url']

    def get_script_list(self)):
        '''
        return [(think_time, form_name)]
        '''
        ret = []
        return ret


class Form_define_reader():
    '''
    read form define file
    '''
    def __init__(self, form_define_file):
        self.form_difines = self._read_form_define_file(form_define_file)

    def _read_form_define_file(file):
        ret = {}
        return ret

    def create_payload(self, form_name, res):
        ret = {}
        return ret


def main():
    pass


if __name__ == '__main__':
    main()
