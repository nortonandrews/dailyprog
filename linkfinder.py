'''This script looks through itsumi's logs and returns the last few URLs posted
and their respective titles encoded in JSON.
'''

import sys
import csv
import re
import json
import requests

if len(sys.argv) != 3:
	print('ERROR: Wrong number of arguments.\nUsage: python3 linkfinder.py <PATH TO LOG FILE> <NUMBER OF LINKS TO GET>', file=sys.stderr)
	quit()

try:
	if int(sys.argv[2]) < 1:
		raise
except:
	print('ERROR: "{0}" is not a valid number of links to fetch.'.format(sys.argv[2]), file=sys.stderr)
	quit()

try:
	with open(sys.argv[1], newline='', encoding='iso-8859-1') as file:
		url_regex = re.compile('(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?')
		reader = csv.reader(file, delimiter=',', escapechar='\\', quoting=csv.QUOTE_MINIMAL)
		links = []

		for row in reader:
			link = url_regex.search(row[2]) # row[2] = chat message content
			if link:
				links.append(link.group(0))

		# Extact title from last X links.
		parsed_links = []
		count = 0

		for link in reversed(links):
			if count == int(sys.argv[2]):
				break

			# Request raw HTML data.
			try:
				html = requests.get(link).text

				# Look for title.
				try:
					# For some reason this breaks when the title has \n or \t.
					#link_title = re.search('<title>.+</title>', html)[0][7:-8]

					# Do it manually then.
					left = html.find('<title>')
					right = html.find('</title>')

					if left == -1 or right == -1:
						raise

					link_title = html[left+7:right].strip()
				except:
					link_title = None
					print('WARNING: Failed to extract title from {0}'.format(link), file=sys.stderr)

				parsed_links.append({
						'url': link,
						'title': link_title
					})

				count += 1
			except:
				print('WARNING: Failed to load {0}'.format(link), file=sys.stderr)
				continue

		# Encode into JSON and print to stdout.
		parsed_links.reverse() # last link posted will be in position [0]
		print(json.dumps(parsed_links))

except FileNotFoundError as ex:
	print('ERROR: Failed to open {0}\nCaught exception: {1}'.format(sys.argv[1], str(ex)), file=sys.stderr)
