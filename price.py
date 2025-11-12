#!/usr/bin/python
import requests
print(requests.get("https://blockchain.info/q/24hrprice").text)
