import os
import sys
import time
import json
import requests
import feedparser

debug = False

# Set update interval here. Should not be too short as to not get IP banned.
update_interval = 3600 # 1 hour (3600s)

# Add more channels here.
channels = [
	'KingHerring',
	'dubbeltumme'
	]

# Check if JSON file needs to be updated.
filename = os.path.join(
	os.path.dirname(os.path.abspath(__file__)),
	'dailyprog_recent_videos.json'
	)

try:
	if os.stat(filename).st_mtime > time.time() - update_interval:
		print('JSON file is not older than {0} seconds. Exiting...'
				.format(update_interval), file=sys.stderr)
		quit()
except FileNotFoundError:
	print('JSON file not found. Fetching new videos...', file=sys.stderr)

'''for username in channels:
	filename = os.path.join(
		os.path.dirname(os.path.abspath(__file__)),
		'{0}.xml'.format(username)
		)

	try:
		with open(filename, 'wb') as new_file:
			response = requests.get('https://www.youtube.com/feeds/videos.xml?user={0}'
				.format(username))
			new_file.write(response.content)
	except Exception as ex:
		print('Could not update channel {0}.\nCaught exception: {1}'
			.format(username, str(ex)), file=sys.stderr)'''

videos = []
most_recent_videos = []

for username in channels:
	'''filename = os.path.join(
		os.path.dirname(os.path.abspath(__file__)),
		'{0}.xml'.format(username)
		)
	f = feedparser.parse(filename)'''
	f = feedparser.parse('https://www.youtube.com/feeds/videos.xml?user={0}'
				.format(username))
	processing_latest_video = True

	# Loops are slow. Maybe replace this with something more efficient later?
	for item in f.entries:
		video = {
			'title': item.title,
			'url': item.link,
			'id': item.link[32:], # This is prone to breaking. If anything goes
								  # wrong this is a good place to check.
			'date': item.published
			}

		# Most recent video from each channel should be at the top of list -
		# send them to separate list at first so they don't get sorted.
		if processing_latest_video:
			most_recent_videos.append(video)
			processing_latest_video = False
		else:
			videos.append(video)

# Sort videos by date
videos.sort(key=lambda r: r['date'], reverse=True)

# Add most recent video from each channel to the list.
videos = most_recent_videos + videos

# Print video list for testing.
if debug:
	for v in videos:
		print('{0} - {1} - {2}'.format(v['date'], v['title'], v['url']))
	quit()

# Encode into JSON and write to file.
filename = os.path.join(
	os.path.dirname(os.path.abspath(__file__)),
	'dailyprog_recent_videos.json'
	)

try:
	with open(filename, 'w') as f:
		print(json.dumps(videos), file=f)
except Exception as ex:
	print('Could not write JSON file.\nCaught exception: {0}'.format(str(ex)), file=sys.stderr)