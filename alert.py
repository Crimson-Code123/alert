#!/usr/bin/python

import requests
import time
import json
import datetime
# from selenium import webdriver
from datetime import date

lastHash = "" # latest hash in the chain
hashTime = 0 # latest blocks time
prevTime = 0 # prev block time
block = {} # latest block as dict
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

def init():
	global lastHash, block
	lastHash = getLatestHash()
	block = getBlockData(lastHash)

def main():
	global lastHash, block, hashTime
	print("Started at {0} | {1}".format(start, date.fromtimestamp(start).ctime()))
	init()
	while True:
		try:
			monitor(lastHash)
		except Exception as e:
			print("Except:", e)
		time.sleep(logInterval)

def getBlockTime(data):
	for x in data:
		if x == "time":
			return block[x]

def monitor(hash):
	global block, hashTime, lastHash, prevTime
	t = getTime()
	block = getBlockData(hash)
	# not working properly
	if len(block["next_block"]) == 0:
		hashTime = block["time"]
		if prevTime != 0 and prevTime != hashTime:
			logBlock()
			# print("{0} prev {1} hashtime".format(prevTime, hashTime))
			since = hashTime - prevTime
			print("Since last hash: {0}".format(since))
			logHashTime(since)
			prevTime = hashTime
	else:
		hash = block["next_block"][0]
		prevTime = block["time"]
		print(hash)
		lastHash = hash
		hashTime = prevTime

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
	newTime = getBlockTime(block)
	since = newTime-hashTime
	print("Since last hash: {0}".format(since))
	logHashTime(since)
	hashTime = newTime

def logBlock():
	with open("blocks.log", mode="+a") as file:
		file.write(json.dumps(block))

def logAlert(t, x, text):
	with open("alerts.log", mode="+a") as file:
		file.write("{0}|{1}|{2}".format(t, x, text))
		file.write("\n")

def logHashTime(since):
	with open("since.log", mode="+a") as file:
		file.write("{2}:{0}:{1} seconds since last block".format(getTime(), since, lastHash))
		file.write("\n")

def updateBlockData(hash):
	global block
	data = getBlockData(hash)
	try:
		block = json.loads(data)
	except:
		print(data)

""" Single block data (JSON) 
top level keys:
bits
next_block[0]
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
		return json.loads(data.text)
	elif data.status_code == 404: # block not fully processed
		time.sleep(queryInterval*5)
		return getBlockData(hash)
	else:
		print("Bad status:", data, data.text)

def getBlockTime(bblock, net=False):
	global block
	if net == False:
		return block["time"]
	else:
		block = getBlockData(hash)
		if block == None:
			return
		try:
			return block["time"]
		except:
			print("Bad: {0}", block)
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

start = getTime() # time the app was started

if __name__ == "__main__":
	main()

