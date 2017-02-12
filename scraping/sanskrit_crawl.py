"""
Download this script and req.txt
Create a directory named 'download' in same folder

Run:
pip install -r req.txt
python sanskrit_crawl.py
"""

import pprint as pp
import requests, re, string

from lxml import html, etree
from time import ctime, sleep
from selenium import webdriver
from pyvirtualdisplay import Display
from lxml.cssselect import CSSSelector
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

MAX_SCROLL = 100
COUNT = 1

class Page(object):
	"""Container for page details"""


	def __init__(self, url):
		"""Construct object using _url_ of page"""

		self.url = url
		connected = False
		while not connected:
			try:
				self.text = requests.get(self.url).text
				connected = True
			except:
				sleep(30)
				pass
		self.dom = html.fromstring(self.text, parser=html.HTMLParser(encoding='utf-8'))

	def selenium_load(self):
		""" Load _url_ in selenium webdriver using virtual display"""
		
		display = Display(visible=0, size=(800, 600))
		display.start()	
		browser = webdriver.Firefox()
		browser.get(self.url)
		return browser

	def scrolldown(self, browser):
		""" Handle pages which load content on scroll events """

		ypos = 0
		for t in range(0, MAX_SCROLL):
		  ypos += 1000
		  script = "window.scrollTo(0," + str(ypos) + " );"
		  browser.execute_script(script)
		return browser


def main():
	global COUNT

	site_url = "http://www.sanskritlibrary.org/"
	seed_url = "http://www.sanskritlibrary.org/textsList.html"
	titus_url = "http://titus.uni-frankfurt.de"
	p = Page(seed_url)

	a_tags = CSSSelector('a')
	div_tags = CSSSelector('div')
	span_tags = CSSSelector('span')
	body_tags = CSSSelector('body')

	div = [e for e in div_tags(p.dom) if e.get("class")=="text"]
	div = div[0]
	links = [site_url + i.get("href") for i in div.getchildren() if i.tag=='a']
	print "Links of texts:", len(links)
	source_links = list()


	#Creating list of links
	for l in links:
		lpage = Page(l)
		slinks = [i.get("href") for i in a_tags(lpage.dom) if i.get("target")=="source"]
		source_links += slinks

	
	print "Links of sources:", len(source_links) #134
	source_links = list(set(source_links))
	print "Unique links of sources:", len(source_links) #94

	#Considering only ramayana and mahabharat links
	source_links = [i for i in source_links if ("/mbh" in i or "/ram" in i)]
	pp.pprint(source_links)

	b = p.selenium_load()
	for link in source_links:
		lp = link

		print "SOURCE_LINK",link
		while lp:
			try:
				b.get(lp)
				sleep(0.25)

				b.switch_to_frame(b.find_elements_by_tag_name("frame")[0])
				bdom=html.fromstring(b.page_source, parser=html.HTMLParser(encoding='utf-8'))
				bt = body_tags(bdom)
				if len(bt)==0:
					print "No body tag for " + lp
					continue
				body = bt[0]
				f = open("download/" + lp[lp.rfind("/")+1:]+".txt", 'w')
				f.write(body.text_content().encode('utf-8'))
				f.close()
				print "File no. " + str(COUNT) + " created"
				COUNT += 1
				anchors = a_tags(bdom)

				lp = None


				for i in range(len(anchors)-1, max(0, len(anchors)-5), -1):
				
					if len(anchors[i].getchildren())==1 and anchors[i].getchildren()[0].tag=="img" and "arribar" in anchors[i].getchildren()[0].get("src"):
						href = anchors[i].get("href")
						lp = titus_url+href
						print i, len(anchors)-i
						print "New frame:", lp
						break
			except:
				lp = None

if __name__=="__main__":
	main()



