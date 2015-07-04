#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from lxml import etree
import requests
import pprint
import traceback
import copy

currPath = os.path.dirname(os.path.abspath(__file__))
cacheDir = os.path.abspath(os.path.join(currPath, "./cache"))
etcDic = os.path.abspath(os.path.join(currPath, "./etc"))
wwwDir = os.path.abspath(os.path.join(currPath, "./www"))
configPath = os.path.join(etcDic, "myadblock.xml")
outputFilePath = os.path.join(wwwDir, "myadblock.txt")

class Helpers(object):
	def toBool(self, o):
		if o is None:
			return False

		if isinstance(o, bool):
			return o

		if isinstance(o, (float, int)):
			return True if o == 1 else False

		if isinstance(o, (unicode, str)):
			try:
				o = int(o)
				return True if o == 1 else False
			except:
				pass

			if o.lower().strip() == "true":
				return True
			else:
				return False

		return False

	def removeTxtHeader(self, t):
		a = []
		for line in t.splitlines():
			line = line.strip()
			if line.lower().startswith("[adblock"):
				continue
			a.append(line)
		t = "\n".join(a)
		
		a, b = [], True
		for line in t.splitlines():
			line = line.strip()
			if b and line == "":
				continue
			
			if line != "":
				b = False
			
			a.append(line)
			
		return "\n".join(a)

	def removeExcludes(self, t):
		a = []
		startDebug = False
		for line in t.splitlines():
			line = line.strip()


			# remove all exceptions
			if self.xcfg.remove_excludes.remove_all:
				if line.startswith("@@"):
					if self.xcfg.app.debugMode:
						print("excluding line: {0} (exclusion line: {1})".format(line, excl))
					
					if self.xcfg.remove_excludes.action_type.remove:
						continue
					
					if not self.xcfg.remove_excludes.action_type.comment:
						continue
					
					if self.xcfg.remove_excludes.action_type.comment_pattern is None:
						continue
					
					pattern = self.xcfg.remove_excludes.action_type.comment_pattern
					if pattern.find("@@RULE@@") >= 0:
						pattern = pattern.replace("@@RULE@@", line)
					
					line = pattern
					a.append(line)
					continue


			# starts-with rules
			for excl in self.xcfg.remove_excludes.starts_with_List:
				if line.startswith(excl):
					if self.xcfg.app.debugMode:
						print("excluding line: {0} (exclusion line: {1})".format(line, excl))
					
					if self.xcfg.remove_excludes.action_type.remove:
						continue
					
					if not self.xcfg.remove_excludes.action_type.comment:
						continue
					
					if self.xcfg.remove_excludes.action_type.comment_pattern is None:
						continue
					
					pattern = self.xcfg.remove_excludes.action_type.comment_pattern
					if pattern.find("@@RULE@@") >= 0:
						pattern = pattern.replace("@@RULE@@", line)
					
					line = pattern
					a.append(line)
					continue
			
			# exact-match rules
			for excl in self.xcfg.remove_excludes.exact_match_List:
				if line == excl:
					if self.xcfg.app.debugMode:
						print("excluding line: {0} (exclusion line: {1})".format(line, excl))

					if self.xcfg.remove_excludes.action_type.remove:
						continue
					
					if not self.xcfg.remove_excludes.action_type.comment:
						continue
					
					if self.xcfg.remove_excludes.action_type.comment_pattern is None:
						continue
					
					pattern = self.xcfg.remove_excludes.action_type.comment_pattern
					if pattern.find("@@RULE@@") >= 0:
						pattern = pattern.replace("@@RULE@@", line)
					
					line = pattern
					a.append(line)
					continue


			# find-any rules
			for excl in self.xcfg.remove_excludes.find_any_List:
				if line.startswith("@@") and line.find(excl) >= 0:
					if self.xcfg.app.debugMode:
						print("excluding line: {0} (exclusion line: {1})".format(line, excl))

					if self.xcfg.remove_excludes.action_type.remove:
						continue
					
					if not self.xcfg.remove_excludes.action_type.comment:
						continue
					
					if self.xcfg.remove_excludes.action_type.comment_pattern is None:
						continue
					
					pattern = self.xcfg.remove_excludes.action_type.comment_pattern
					if pattern.find("@@RULE@@") >= 0:
						pattern = pattern.replace("@@RULE@@", line)
					
					line = pattern
					a.append(line)
					continue
					

			a.append(line)

		return "\n".join(a)
		

class Config_Cache(object):
	enabled = False
	cache_dir = cacheDir

class Config_App(object):
	debug = False
	verbose = False
	currentPath = currPath
	cacheDir = cacheDir
	etcDic = etcDic
	wwwDir = wwwDir
	configPath = configPath
	output_file = outputFilePath
	cache = Config_Cache()
	encoding = "utf-8"
	get_timeout = None

class Config_Subscription(object):
	enabled = False
	mime_type = None
	name = None
	url = None
	localUrl = None

class Config_Subscriptions(object):
	enabled = False
	subscriptionList = []

class Config_rule(object):
	name = None
	enabled = False
	data = None

class Config_AddRules(object):
	title = None
	enabled = False
	ruleList = []

class Config_ActionType(object):
	remove = False
	comment = False
	comment_pattern = None

class Config_RemoveExcludes(object):
	remove_all = False
	action_type = Config_ActionType()
	starts_with_enabled = False
	starts_with_List = []
	exact_match_enabled = False
	exact_match_List = []
	find_any_enabled = False
	find_any_List = []

class Config(object):
	app = Config_App()
	subscriptions = Config_Subscriptions()
	add_rules = Config_AddRules()
	remove_excludes = Config_RemoveExcludes()

class MyAdblock(object):

	debugMode = True
	verboseMode = True
	
	helpers = Helpers()
	xcfg = None
	configParsed = False
	
	def __init__(self):
		
		self.configParsed = False
		if not os.path.exists(cacheDir):
			os.mkdir(cacheDir)
		if not os.path.exists(wwwDir):
			os.mkdir(wwwDir)


	def __del__(self):
		try:
			pass
#			self.wwwFile.close()
		except:
			pass

	def initConfig(self):
		xcfg = Config()
		
#		self.wwwFile = open(xcfg.app.output_file, "w")

		confFilePath = os.path.join(etcDic, "myadblock.xml")

		# parse xml file and get root node
		rootNode = etree.parse(xcfg.app.configPath, etree.XMLParser())
		
		# config->app block
		xcfg.app.debugMode = self.helpers.toBool(rootNode.xpath("//config/app/debug")[0].text)
		xcfg.app.verboseMode = self.helpers.toBool(rootNode.xpath("//config/app/verbose")[0].text)
		of = rootNode.xpath("//config/app/output-file")[0].text
		if of:
			xcfg.app.output_file = of
		xcfg.app.cache.enabled = self.helpers.toBool(rootNode.xpath("//config/app/cache/enabled")[0].text)
		cd = rootNode.xpath("//config/app/cache/dir")[0].text
		if cd:
			cfg.app.cache.cache_dir = cd
		xcfg.app.encoding = rootNode.xpath("//config/app/encoding")[0].text
		xcfg.app.get_timeout = rootNode.xpath("//config/app/get-timeout")[0].text
		try:	xcfg.app.get_timeout = int(xcfg.app.get_timeout)
		except:	pass
		
		# config->subscriptions block
		xcfg.subscriptions.enabled = self.helpers.toBool(rootNode.xpath("//config/subscriptions/enabled")[0].text)
		xcfg.subscriptions.subscriptionList = []
		if xcfg.subscriptions.enabled:
			cs = Config_Subscription()
			for sub in rootNode.xpath("//config/subscriptions/subscription"):
				cs.enabled = self.helpers.toBool(sub.xpath("./enabled")[0].text)
				cs.mime_type = sub.xpath("./mime-type")[0].text
				if cs.mime_type is None:
					cs.mime_type = "text/plain"
				cs.name = sub.xpath("./name")[0].text
				cs.url = sub.xpath("./url")[0].text
				cs.localUrl = cs.url.split("/")[-1]
				xcfg.subscriptions.subscriptionList.append(copy.copy(cs))
		
		# config->add-rules block
		xcfg.add_rules.title = (rootNode.xpath("//config/add-rules/title")[0].text).encode(xcfg.app.encoding)
		xcfg.add_rules.enabled = self.helpers.toBool(rootNode.xpath("//config/add-rules/enabled")[0].text)
		xcfg.add_rules.ruleList = []
		if xcfg.add_rules.enabled:
			for rule in rootNode.xpath("//config/add-rules/rule"):
				cr = Config_rule()
				cr.name = rule.xpath("./name")[0].text
				cr.enabled = self.helpers.toBool(rule.xpath("./enabled")[0].text)
				cr.data = rule.xpath("./data")[0].text
				xcfg.add_rules.ruleList.append(copy.copy(cr))

		# config->remove-excludes block
		xcfg.remove_excludes.remove_all = self.helpers.toBool(rootNode.xpath("//config/remove-excludes/remove-all")[0].text)
		xcfg.remove_excludes.action_type.remove = self.helpers.toBool(rootNode.xpath("//config/remove-excludes/action-type/remove")[0].text)
		xcfg.remove_excludes.action_type.comment = self.helpers.toBool(rootNode.xpath("//config/remove-excludes/action-type/comment")[0].text)
		xcfg.remove_excludes.action_type.comment_pattern = rootNode.xpath("//config/remove-excludes/action-type/comment-pattern")[0].text

		# config->remove-excludes->starts-with block
		xcfg.remove_excludes.starts_with_enabled = self.helpers.toBool(rootNode.xpath("//config/remove-excludes/starts-with/enabled")[0].text)
		xcfg.remove_excludes.starts_with_List = []
		if xcfg.remove_excludes.starts_with_enabled:
			for excl in rootNode.xpath("//config/remove-excludes/starts-with/data")[0].text.splitlines():
				excl = excl.strip()
				if excl == "" or excl.startswith("#") or excl.startswith("!"):
					continue
				xcfg.remove_excludes.starts_with_List.append(copy.copy(excl))
		
		# config->remove-excludes->exact-match block
		xcfg.remove_excludes.exact_match_enabled = self.helpers.toBool(rootNode.xpath("//config/remove-excludes/exact-match/enabled")[0].text)
		xcfg.remove_excludes.exact_match_List = []
		if xcfg.remove_excludes.exact_match_enabled:
			for excl in rootNode.xpath("//config/remove-excludes/exact-match/data")[0].text.splitlines():
				excl = excl.strip()
				if excl == "" or excl.startswith("#") or excl.startswith("!"):
					continue
				xcfg.remove_excludes.exact_match_List.append(copy.copy(excl))

		# config->remove-excludes->find-any block
		xcfg.remove_excludes.find_any_enabled = self.helpers.toBool(rootNode.xpath("//config/remove-excludes/find-any/enabled")[0].text)
		xcfg.remove_excludes.find_any_List = []
		if xcfg.remove_excludes.find_any_enabled:
			for excl in rootNode.xpath("//config/remove-excludes/find-any/data")[0].text.splitlines():
				excl = excl.strip()
				if excl == "" or excl.startswith("#") or excl.startswith("!"):
					continue
				xcfg.remove_excludes.find_any_List.append(copy.copy(excl))
				

		self.configParsed = True
		self.xcfg = xcfg
		self.helpers.xcfg = xcfg

	def run(self):

		adblockContent = []
		adc = adblockContent.append

		adc("[Adblock Plus 2.0]")
		adc("")

		if self.xcfg.add_rules.enabled:
			adc("!")
			adc("! Title: {0}".format(self.xcfg.add_rules.title))
			adc("!")
			for rule in self.xcfg.add_rules.ruleList:
				rule.data = [ a.strip() for a in rule.data.splitlines() if a.strip() != "" ]
				
				adc("! **********************")
				adc("! Block name: {0}".format(rule.name))
				adc("! Enabled: {0}".format("yes" if rule.enabled else "no"))
				adc("! **********************")
				adc("!")
				for r in rule.data:
					adc("{0}{1}".format("!!! " if not rule.enabled else "", r.encode(self.xcfg.app.encoding)))
				adc("")


		if self.xcfg.subscriptions.enabled:
			for sub in self.xcfg.subscriptions.subscriptionList:
				if not sub.enabled:
					continue


				sub.localUrl = os.path.join(self.xcfg.app.cache.cache_dir, sub.localUrl)

				try:
					if sub.mime_type != "text/plain":
						print ("Unsupported url {0}".format(sub.url))
						continue


					if self.xcfg.app.verboseMode:
						print ("Downloading {0}...".format(sub.url))

					resp = requests.get(sub.url, timeout=self.xcfg.app.get_timeout)
					text = resp.text
					
					if self.xcfg.app.cache.enabled:
						open(sub.localUrl, "wb").write(text.encode(self.xcfg.app.encoding) + "\n")
					
				except:
					if True or self.xcfg.app.debugMode:
						traceback.print_exc()
					if self.xcfg.app.cache.enabled and os.path.exists(sub.localUrl):
						text = open(sub.localUrl, "rb").read()
						text = text.decode(self.xcfg.app.encoding)
					else:
						continue
				
				text = self.helpers.removeTxtHeader(text)
				text = self.helpers.removeExcludes(text)
				
				adc("")
				adc("!")
				adc("! Title: {0}".format(sub.name.encode(self.xcfg.app.encoding)))
				adc("! Url: {0}".format(sub.url.encode(self.xcfg.app.encoding)))
				adc("!")
				adc(text.encode(self.xcfg.app.encoding))

		wwwFile = open(self.xcfg.app.output_file, "wb")
		for line in adblockContent:
			wwwFile.write(line + "\n")
		wwwFile.close()


if __name__ == "__main__":
	inst = MyAdblock()
	try:
		inst.initConfig()
		if inst.configParsed and inst.xcfg.app.debugMode:
			print("Config loaded")
		inst.run()
	except Exception, ex:
		print("Cannot initialize application. Error: {0}".format(ex.message))
		if True or inst.configParsed and inst.xcfg.app.debugMode:
			traceback.print_exc()

