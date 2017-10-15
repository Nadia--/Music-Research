import urllib.request
import json
import re

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

YOUTUBE_QUERY_URL = "https://www.googleapis.com/youtube/v3/"
YOUTUBE_SEARCH_URL = YOUTUBE_QUERY_URL + "search?"
YOUTUBE_COMMENTS_URL = YOUTUBE_QUERY_URL + "commentThreads?"

key = 'AIzaSyBAcQUU5I4FElmsYVK0irkDPVGQ_OLLkO0' #TODO use key that isnt from stackoverflow XD

KEEP_SONG_RELATED = 'keep_song_related'
KEEP_TITLE_AND_ARTIST = 'keep_title_and_artist'

REMOVE_IF_NO_LIKES = 'remove_if_no_likes'
REMOVE_MOVIE_RELATED = 'remove_movie_related'
REMOVE_DUMB_COMMENTS = 'remove_dumb_people'

def comments_filter_remove(comments, key_words):
    regex_key_words = '|'.join(key_words)
    return [comment for comment in comments if 
            re.search(regex_key_words, comment.text, re.IGNORECASE) is None or 
            comment.keep == True]

def comments_filter_keep(comments, key_words):
    regex_key_words = '|'.join(key_words)
    for comment in comments:
        match = re.search(regex_key_words, comment.text, re.IGNORECASE)
        if match:
            comment.keep = True
    return comments

def comments_filter_likes(comments, key_words):
    return [comment for comment in comments if comment.like_count > 0 or comment.keep == True]

def comments_filter_title(): return None


filters = {
      KEEP_SONG_RELATED: (comments_filter_keep, ['song', 'piece', 'sound'])
    , KEEP_TITLE_AND_ARTIST: (comments_filter_title, [])
    , REMOVE_DUMB_COMMENTS: (comments_filter_remove, ['setting', 'here'])
    # 'who's here from supernatural', 'lio rush brought me here'
    # 'if you change the setting to 1.5 speed it is slightly faster' 
    , REMOVE_IF_NO_LIKES: (comments_filter_likes, []) 
    , REMOVE_MOVIE_RELATED: (comments_filter_remove, ['Inhumans', 'Marvel', 'Lucifer'])
}

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
        self.weighted_sentiment = None #TODO: add relevancy weights

    def fetch_youtube_comments(self, comment_count, filter_tag_list):
        #search for YouTube video
        search_parameters = {'part': 'snippet', 'q': self.title + " "+ self.artist, 'key': key}
        search_url = YOUTUBE_SEARCH_URL + urllib.parse.urlencode(search_parameters)
        json_search = urllib.request.urlopen(search_url).read().decode('utf-8')
        parsed_search = json.loads(json_search)

        #obtain video_id
        #TODO: filter for legit link ("official music video" title or description)
        chosen_result = 0 #takes the first result
        self.video_id = parsed_search['items'][chosen_result]['id']['videoId']

        #obtain comments
        nextPageToken = None
        while comment_count > 0:
            comments_parameters = {'part': 'snippet', 'videoId': self.video_id, 'key': key, 'maxResults': 100, 'nextPageToken': nextPageToken, 'order':'relevance'}
            comments_url = YOUTUBE_COMMENTS_URL + urllib.parse.urlencode(comments_parameters)
            json_comments = urllib.request.urlopen(comments_url).read().decode('utf-8')
            parsed_comments = json.loads(json_comments)
            comments = [Comment(x['snippet']['topLevelComment']['snippet']['textOriginal'], x['snippet']['topLevelComment']['snippet']['likeCount']) for x in parsed_comments['items']]

            for filt in filter_tag_list:
                (filter_fn, key_words) = filters[filt]
                if filter_fn == comments_filter_title:
                    comments_filter_keep(comments, [self.artist, self.title])
                else:
                    comments = filter_fn(comments, key_words)

            self.comments += comments[0:min(len(comments), comment_count)]
            comment_count -= len(comments)
            nextPageToken = parsed_comments['nextPageToken']

    def analyze_sentiment(self):
        analyzer = SentimentIntensityAnalyzer()

        sentiment = 0.0;
        num_items = 0;
        for comment in self.comments:
            num_items+=1.0
            vs = analyzer.polarity_scores(comment.text)
            comment.sentiment = vs['compound']
            sentiment += (vs['compound'] - sentiment) / num_items
        self.weighted_sentiment = sentiment

    def __str__(self):
        pairs = ['(%d, %d, %f, "%s")' % (comment.like_count, comment.keep, comment.sentiment, comment.text) for comment in self.comments]
        return '\n'.join(pairs)


black = Song('Ciara', 'Paint It Black')
filter_tag_list = [REMOVE_IF_NO_LIKES, REMOVE_DUMB_COMMENTS, KEEP_TITLE_AND_ARTIST, KEEP_SONG_RELATED, REMOVE_MOVIE_RELATED]
filter_tag_list = []
black.fetch_youtube_comments(30, filter_tag_list)
black.analyze_sentiment()
print("video_id %s" % black.video_id)
print(len(black.comments))
print(black)
print(black.weighted_sentiment)

