#-*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import codecs
import json
import os
from pprint import pprint
import requests
import sys
import threading
import time

def pause_json_file(path):
  ret = {}
  with codecs.open(path, 'r', 'utf-8') as f:
      ret = json.load(f)
  return ret


def _check_exists_file(path):
	if not os.path.exists(path):
		raise Exception('not found file: %s' % (path, ))


def save_res(file_name, res);
	with codecs.open(file_name + '.html', 'w', 'utf-8') as f:
		f.write(res.text)


class Scriptinvoker_manager():
  '''
  manage Script_invoker
  '''
  def __init__(self, variant_file, script_file, form_define_file):
    _check_exists_file(variant_file)
    _check_exists_file(script_file)
    _check_exists_file(form_define_file)
    self.invokers = []
    script_reader = Script_reader(script_file)
    form_define_reader = Form_define_reader(form_define_file)
    for vars in self._read_variant_file(variant_file):
      self.invokers.append(Script_invoker(script_reader, form_define_reader, vars))

  def invoke(self, exec_time):
    print('[*] start ')
    for invoker in self.invokers:
    	time.sleep(1)
    	invoker.start()
    time.sleep(exec_time)
    for invoker in self.invokers:
    	invoker.kill = True


    def _read_variant_file(self, variant_file):
    	'''
    		file format
    		[
					{
						<variant_name> : <variant_value>,
						... : ...
					}, 
					{
						...
					}
    		]
    	'''
    	ret = parse_json_file(variant_file)
    	return ret


class Script_invoker(threading.Thread):
    '''
    invoke script
    '''
    def __init__(self, script_reader, form_define_reader, alias_variants):
  		threading.Thread.__init__(self)
      self.id = hex(id(self))
      self.kill = False
      self.script_reader = script_reader
      self.form_define_reader = form_define_reader
      self.alias_variants = alias_variants
      self.head_url = self.script_reader.get_haed_url()
      self.script_exec_count = 0

    def run(self):
      while not self.kill:
        try:
        	self.script_exec_count += 1
          res = self._get_top_page()
          cookie = res.cookies
          for script_info in self.script_reader.get_script_list():
            if not res.ok:
       	   		raise Exception('error status: %s url; %s' % (res.status_code, res.url))
            time.sleep(script_info['think_time'])
            res = self._post(
            		script_info['forom-name'],
            		script_info['form_id'],
            		res,
            		cookie
            	)
            save_res('%s_%s_%02d' % (self.id, script_info['action_name'], self.script_exec_count), res)
            if self.kill:
              break
        except Exception as e:
          self.print_error(str(e))

    def print_error(self, message):
      print('[!] %s : %s' % (self.id, str(message)))

    def print_info(self, message):
      print('[*] %s : %s' % (self.id, str(message)))

    def _get_top_page(self):
      res = requests.get(self.script_reader.get_top_url())
      return res

    def _post(self, form_name, before_res, cookie):
    	url, data = self.form_define_reader.create_payload(form_name, form_id, before_res, self.alias_variants)
    	url = self.head_url + url
    	self.print_info('url: %s' % (url, ))
    	res = requests.post(url=url, cookies=cookie, data=data)
    	return res

    def _get_url(self, res, form_name):
      parser = BeautifulSoup(res.text, 'html.parser')
      urls = self.head_url + parser.select('form[name=%s]' % (form_name, ))
			if len(urls) == 0:
      	raise Exception('form not found: %s' % (form_name, ))
      return urls[0]


class Script_reader():
    '''
    read script file
    '''
    def __init__(self, script_file):
    	self.head_url = ''
    	self.top_url = ''
    	self.scripts = []
    	self._read_script_file(script_file)

    def _read_scirpt_file(self, script_file):
    	'''
    	file format
    	{
				head_url : <url head>,
				top_url : <url top>,
				scripts : [
					{
						think_time : <think_time(sec)>, 
						form_name : <form name>,
						form_id : <form id>,
						action_name : <action name>
					}
				]
    	}
    	'''
    	ret = parse_json_file(script_file)
    	if not 'head_url' in ret.keys():
    		raise Exception('not found <head_url> in script file')
    	if not 'top_url' in res.keys():
    		raise Exception('not found <top_url> in script file')
    	self.head_url = ret['head_url']
    	self.top_url = ret['top_url']
    	if not 'scripts' in ret.keys():
    		raise Exception('not found <scripts> in script file')
    	self.scripts = ret['scripts']

    def get_head_url(self):
      return self.script['head_url']

    def get_top_url(self):
      return self.script['top_url']

    def get_script_list(self):
      return self.scripts


class Form_define_reader():
    '''
    read form define file
    '''
    def __init__(self, form_define_file):
        self.form_difines = self._read_form_define_file(form_define_file)

    def _read_form_define_file(file):
    	ret = parse_json_file(file)
    	return ret

    def create_payload(self, form_name, res):
    	HTML_VAL = '<USE_HTML_VAL>'
    	if not form_id in self.form_defines.keys():
    		raise Exception('form : %s is not found in form_defines_file' % (form_id, ))
    	form_define = self.form_defines[form_id]
    	frms = BeautifulSoup(res.text, 'html.parser').select('form[name=%s]' % (form_name, ))
    	if len(frms) == 0:
    		raise Exception('form : %s is not found in response' % (form_name, ))
    	tagname = ''
    	for frm in frms:
    		ret = {}
    		url = frm.attrs['action']
    		for tag_name in form_define.keys():
    			if form_define[tag_name] == HTML_VAL:
    				inpt_tag = self._find_inputtag_byname(frm, tag_name)
    				if len(inpt_tag) == 0:
    					break
    				inpt_tag = inpt_tag[0]
    				ret[tag_name] = inpt_tag.attrs['value']
    			elif form_define[tag_name] in vars.keys():
    				ret[tag_name] = var[form_define[tag_name]]
    			else:
    				ret[tag_name] = form_define[tag_name]
    		else:
    			return (url, ret)
  		else:
  			raise Exception('input tag : %s is not found in form : %s' % (tag_name, form_name))
  		return None


	def find_inputtag_byname(self, form_tag_inpt_tag_name):
		ret = []
		for inpt_tag in form_tag.select('input'):
			if inpt_tag['name'] == inpt_tag_name:
				ret.append(inpt_tag)
		return ret


def main():
	args = []
	args.appned('')
	args.append('./vars.js')
	args.append('./script.js')
	args.append('./form_define.js')
	args.append(60)

	if len(args) < 5:
		print('[!] invalid arg count')
		print('[!] variants file path')
		print('[!] scripts file path')
		print('[!] form define file path')
		print('[!] exec time (sec)')
		return
	exec_time = 0
	try:
		exec_time = int(args[4])
	except:
		print('[!] 4th arg is not numeric')
		return
	try:
		scrpt_inv_mgr = Scriptinvoker_manager(args[1], args[2], args[3])
		scrpt_inv_mgr.invoke(exec_time)
	except Exception as e:
		print(e.__traceback__())


if __name__ == '__main__':
    main()
