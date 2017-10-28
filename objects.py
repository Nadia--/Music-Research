#General Libraries
import urllib.request
import json

#Project Libraries
import filters as Filters

# https://github.com/cjhutto/vaderSentiment
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

YOUTUBE_QUERY_URL = "https://www.googleapis.com/youtube/v3/"
YOUTUBE_SEARCH_URL = YOUTUBE_QUERY_URL + "search?"
YOUTUBE_COMMENTS_URL = YOUTUBE_QUERY_URL + "commentThreads?"

key = 'AIzaSyBAcQUU5I4FElmsYVK0irkDPVGQ_OLLkO0' #TODO use key that isnt from stackoverflow XD

class Comment:
    def __init__(self, comment, like_count):
        self.text = comment
        self.like_count = like_count
        self.keep = False
        self.sentiment = None

class Song:
    def __init__(self, artist, title): 
        #TODO: incorporate million dollar song laters
        self.artist = artist
        self.title = title
        self.video_id = None
        self.comments = []
        self.average_sentiment = None #TODO: add weights

    # Populates Song.video_id and Song.comments
    def fetch_youtube_comments(self, comment_count, filter_tag_list):
        # Search for YouTube Video
        search_parameters = {'part': 'snippet', 'q': self.title + " "+ self.artist, 'key': key}
        search_url = YOUTUBE_SEARCH_URL + urllib.parse.urlencode(search_parameters)
        json_search = urllib.request.urlopen(search_url).read().decode('utf-8')
        parsed_search = json.loads(json_search)

        # Obtain YouTube Video ID
        # TODO: filter for legit link ("official music video" title or description)
        chosen_result = 0 #takes the first result
        self.video_id = parsed_search['items'][chosen_result]['id']['videoId']

        # Obtain Comments
        nextPageToken = None
        while comment_count > 0:
            comments_parameters = {'part': 'snippet', 
                    'videoId': self.video_id, 
                    'key': key, 
                    'maxResults': 100, 
                    'order':'relevance'}
            if nextPageToken is not None:
                comments_parameters['pageToken'] = nextPageToken

            comments_url = YOUTUBE_COMMENTS_URL + urllib.parse.urlencode(comments_parameters)
            json_comments = urllib.request.urlopen(comments_url).read().decode('utf-8')
            parsed_comments = json.loads(json_comments)
            #print(json.dumps(parsed_comments, indent=4, sort_keys=True))

            comments = [Comment(
                x['snippet']['topLevelComment']['snippet']['textOriginal'], 
                x['snippet']['topLevelComment']['snippet']['likeCount']) 
                for x in parsed_comments['items']]

            nextPageToken = parsed_comments['nextPageToken']

            # Filter Comments While Obtaining Them
            comments = Filters.run_filters(filter_tag_list, comments, self.title, self.artist)

            num_added = min(len(comments), comment_count)
            self.comments += comments[0:num_added]
            comment_count -= num_added

    # Populate Sentiment 
    def analyze_sentiment(self):
        analyzer = SentimentIntensityAnalyzer()

        sentiment = 0.0;
        num_items = 0;
        for comment in self.comments:
            num_items+=1.0
            vs = analyzer.polarity_scores(comment.text)
            comment.sentiment = vs['compound']
            sentiment += (vs['compound'] - sentiment) / num_items
        self.average_sentiment = sentiment


    # How to Represent Self
    def __str__(self):
        pairs = ['(L:%d, K:%d, S:%+.3f, M:"%s")' % (comment.like_count, comment.keep, comment.sentiment, comment.text) for comment in self.comments]
        rep_str = '%s by %s\n\nvideo id: %s\nresults: %d\nvader sentiment: %+.5f\n' % (
                self.title, self.artist, self.video_id, len(self.comments), self.average_sentiment)
        return '\n' +rep_str + '\n'.join(pairs) + '\n'


