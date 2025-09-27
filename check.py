#!/usr/bin/python

import requests
import json
import time

""" 
>>> date.fromtimestamp(1361388002)
datetime.date(2013, 2, 20)
>>> date.fromtimestamp(1526057932)
datetime.date(2018, 5, 11)
>>> date.fromtimestamp(1679616709)
datetime.date(2023, 3, 23)
 """


height = 782222 # block height to start at
heightURL = "https://blockchain.info/block-height/{0}?format=json"
blockURL = "https://blockchain.info/rawblock/{0}"
prevTime = 0
nextHash = "00000000000000000001d789a89fd529656ccbcbe9f4e44a6aeec1350c8903b5"
since = None

def main():
	global prevTime, nextHash
	if nextHash == "" and prevTime == None:
		data = getHeight()
		prevTime = data["blocks"][0]["time"]
		nextHash = data["blocks"][0]["next_block"][0]
	# getHashandTime(data)
	while True:
		# print(nextHash)
		data = nextBlock(nextHash)
		getHashandTime(data)
		log()
		time.sleep(10)

def getHashandTime(data):
	global prevTime, nextHash, since
	try:
		nextHash = data["next_block"][0]
		since = data["time"] - prevTime
		prevTime = data["time"]
		print("{0} seconds since last block mined".format(since))
	except:
		print(data)

def log():
	with open("record.log", mode="+a") as file:
		file.write("{0}|{1}|{2}\n".format(nextHash, prevTime, since))


def getHeight():
	data = requests.get(heightURL.format(height))
	block = json.loads(data.text)
	return block

def nextBlock(hash):
	data = requests.get("https://blockchain.info/rawblock/{0}".format(hash))
	if data.text == "":
		return hash
	block = json.loads(data.text)
	return block

if __name__ == "__main__":
	main()
