import getopt, sys
import wikipedia
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import json



def command_input():
	# Remove 1st argument from the
	# list of command line arguments
	argumentList = sys.argv[1:]
	
	# Options
	options = "k:n:o:"
	
	# Long options
	long_options = ["keyword=", "num_urls=", "output="]
	
	key = "Hello"
	num = 1
	output = "out.json"
	
	
	try:
		# Parsing argument
		arguments, values = getopt.getopt(argumentList, options, long_options)
		
		# checking each argument
		for currentArgument, currentValue in arguments:
	
			if currentArgument in ("-k", "--keyword"):
				key = currentValue			
			elif currentArgument in ("-n", "--num_urls"):
				num = currentValue
			elif currentArgument in ("-o", "--output"):
				output = currentValue			
		
			
	except getopt.error as err:
		# output error, and return with an error code
		print (str(err))
		
	return key, num, output
	

def search_wiki(keywords, number_of_search):
	suggestion = False
	wiki_pages = []
	for word in range(0, len(keywords)):
		print(keywords[word], ">>")
		result_set = wikipedia.search(keywords[word], number_of_search, suggestion)
		for term in result_set:
		
			try:
				page = wikipedia.page(term, preload=False)
				url = page.url
				# Specify url of the web page
				source = urlopen(url).read()
				# Make a soup
				soup = BeautifulSoup(source,features="lxml")
				content = ""
				for par in soup.find_all('p'):
					txt = par.text
					txt = re.sub(r'\[.*?\]+', '', txt)
					txt = txt.replace('\n', '')
					if(len(txt)>10):
						content = txt
						break
				if(len(content)!=0):
					d = {}
					d.update({'link':url, 'content':content})
					wiki_pages.append(d)				
	
			except wikipedia.exceptions.DisambiguationError as error:
				pass
			except wikipedia.exceptions.PageError as error:
				pass

	return wiki_pages

def get_result(key, num, output):
	res = search_wiki([key], num)
	print(res)
	with open(output, 'w', encoding='utf-8') as f:
		json.dump(res, f, ensure_ascii=True, indent=4)
	