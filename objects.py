#General Libraries
import urllib.request
import json
import colored
from colored import stylize

#Project Libraries
import filters as Filters 

# https://github.com/cjhutto/vaderSentiment
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


YOUTUBE_QUERY_URL = "https://www.googleapis.com/youtube/v3/"
YOUTUBE_SEARCH_URL = YOUTUBE_QUERY_URL + "search?"
YOUTUBE_COMMENTS_URL = YOUTUBE_QUERY_URL + "commentThreads?"

key = 'AIzaSyBAcQUU5I4FElmsYVK0irkDPVGQ_OLLkO0' #TODO use key that isnt from stackoverflow XD


SENTIMENT_VADER = "vader"
SENTIMENT_USER = "user"

class Comment:
    def __init__(self, comment, like_count):
        self.text = comment
        self.like_count = like_count
        self.keep = False
        self.vader_sentiment = None
        self.user_sentiment = None
        self.closeness = None # -1 = red, 0 = yellow, 1 = green

    def __str__(self):
        
        rep_str = '(L:%d, L"%d' %(self.like_count, self.keep)
        if self.vader_sentiment is not None:
            rep_str += ', SV:%+.3f' % self.vader_sentiment
        if self.user_sentiment is not None:
            rep_str += ', US:%+.3f' % self.user_sentiment
        if self.closeness is not None:
            if self.closeness == -1:
                rep_str += ', ' + stylize('B', colored.fg('red'))
            elif self.closeness == 0:
                rep_str += ', ' + stylize('O', colored.fg('yellow'))
            else: 
                rep_str += ', ' + stylize('G', colored.fg('green'))

        rep_str+= ', M:"%s")' % self.text
        return rep_str

class Song:
    def __init__(self, artist, title): 
        #TODO: incorporate million dollar song laters
        self.artist = artist
        self.title = title
        self.video_id = None
        self.comments = []
        self.average_vader_sentiment = None #TODO: add weights
        self.average_user_sentiment = None 


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
    def analyze_sentiment(self, classifier):
        if classifier == SENTIMENT_VADER:
            analyzer = SentimentIntensityAnalyzer()

        sentiment = 0.0;
        num_items = 0;
        for comment in self.comments:
            num_items+=1
            comment_sentiment = None
            if classifier == SENTIMENT_VADER:
                vs = analyzer.polarity_scores(comment.text)
                comment_sentiment = vs['compound']
                comment.vader_sentiment = comment_sentiment
            if classifier == SENTIMENT_USER:
                print("comment: %s" % comment.text)
                comment_sentiment = float(input("Your rating? [-1,1] "))
                comment.user_sentiment = comment_sentiment
            sentiment += (comment_sentiment - sentiment) / num_items
        if classifier == SENTIMENT_VADER:
            self.average_vader_sentiment = sentiment
        if classifier == SENTIMENT_USER:
            self.average_user_sentiment = sentiment

    def compare_analysis(self):
        if self.average_user_sentiment is None or self.average_vader_sentiment is None:
            return
        for comment in self.comments:
            diff = abs(comment.vader_sentiment - comment.user_sentiment)
            if diff < 0.2:
                comment.closeness = 1
            elif diff < 0.5:
                comment.closeness = 0
            else: 
                comment.closeness = -1

    # How to Represent Self
    def __str__(self):

        pairs = [str(comment) for comment in self.comments]

        rep_str = '%s by %s\n\nvideo id: %s\nresults: %d' % (
                self.title, self.artist, self.video_id, len(self.comments))
        if self.average_vader_sentiment is not None:
            rep_str+= '\nvader senteiment: %+.5f' % self.average_vader_sentiment
        if self.average_user_sentiment is not None:
            rep_str+= '\nuser sentiment: %+5f' % self.average_user_sentiment
        rep_str+='\n'


        return '\n' +rep_str + '\n'.join(pairs) + '\n'


