#!/usr/bin/python

import requests
import time
import json
import datetime
from selenium import webdriver
from datetime import date

lastHash = "" # latest hash in the chain
hashTime = 0 # time since the last block
lastBlock = {} # latest block as dict
blockInterval = 0.0
debug = False
verbose = False
logInterval = 30 # interval to log in seconds
queryInterval = 15 # seconds between each query
req_headers = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:143.0) Gecko/20100101 Firefox/143.0"}
chartStats = "https://www.blockchain.com/explorer/charts"
endpoints = {
	# "blockInterval":"https://blockchain.info/q/interval",
	# "hashRate":"https://blockchain.info/q/hashrate",
	"latestHash":"https://blockchain.info/q/latesthash",
	# "latestBlock":"https://blockchain.info/latestblock",
	# "nextBlockETA":"https://blockchain.info/q/eta",
}
if len(endpoints) == 1:
	logInterval = queryInterval

def main():
	global lastHash, lastBlock
	# sschartspage()
	print("Started at {0} | {1}".format(start, date.fromtimestamp(start).ctime()))
	lastHash = getLatestHash()
	block = getBlockData(lastHash)
	lastBlock = json.loads(block)
	extractData(lastBlock)
	while True:
		LogAll()
		time.sleep(logInterval)

def extractData(data):
	global hashTime
	for x in data:
		if x == "time":
			hashTime = lastBlock[x]

def LogAll():
	global lastHash
	t = getTime()
	for x in endpoints:
		data = getURL(endpoints[x])
		time.sleep(queryInterval) # avoid 404
		if data.status_code == 200:
			if x == "latestHash":
				if lastHash != data.text:
					updateData(data.text)
					logAlert(t, x, data.text)
		if len(endpoints) > 1:
			time.sleep(queryInterval)


""" Update block and calc block time """
def updateData(text):
	global lastHash, hashTime, blockInterval
	lastHash = text
	updateBlockData(text)
	logBlock()
	blockInterval = getInterval()
	if verbose:
		print("Interval: {0}".format(blockInterval))
	newTime = getBlockTime(lastBlock)
	since = newTime-hashTime
	print("Since last hash: {0}".format(since))
	logHashTime(since)
	hashTime = newTime

def logBlock():
	with open("blocks.log", mode="+a") as file:
		file.write(json.dumps(lastBlock))

def logAlert(t, x, text):
	with open("alerts.log", mode="+a") as file:
		file.write("{0}|{1}|{2}".format(t, x, text))
		file.write("\n")

def logHashTime(since):
	with open("since.log", mode="+a") as file:
		file.write("{2}:{0}:{1} seconds since last block".format(getTime(), since, lastHash))
		file.write("\n")

def updateBlockData(hash):
	global lastBlock
	data = getBlockData(hash)
	try:
		lastBlock = json.loads(data)
	except:
		print(data)

""" Single block data (JSON) 
top level keys:
bits
next_block
fee
nonce
n_tx
size
block_index
main_chain
height
weight
tx
"""
def getBlockData(hash):
	data = getURL("https://blockchain.info/rawblock/{0}".format(hash))
	if data.status_code == 200:
		return data.text
	elif data.status_code == 404: # block not fully processed
		time.sleep(queryInterval*5)
		return getBlockData(hash)
	else:
		print("Bad status:", data, data.text)

def getBlockTime(block, net=False):
	global lastBlock
	if net == False:
		return block["time"]
	else:
		data = getBlockData(hash)
		if data == None:
			return
		lastBlock = json.loads(data)
		try:
			return lastBlock["time"]
		except:
			print("Bad: {0}", lastBlock)
			return

""" Average time between blocks in seconds """
def getInterval():
	data = getURL("https://blockchain.info/q/interval")
	return data.text

"""  Estimated network hash rate in gigahash """
def getHashRate():
	data = getURL("https://blockchain.info/q/hashrate")
	return data.text

""" Hash of the latest block """
def getLatestHash():
	data = getURL("https://blockchain.info/q/latesthash")
	return data.text

""" Estimated time until the next block (in seconds) """
def getETA():
	data = getURL("https://blockchain.info/q/eta")
	return data.text

def getURL(url):
	return requests.get(url, headers=req_headers)

def getTime():
	return int(time.time())

def sschartspage():
	driver = webdriver.Chrome()
	driver.get(chartStats)
	driver.get_screenshot_as_file("chart.png")
	driver.quit()

start = getTime() # time the app was started

if __name__ == "__main__":
	main()

