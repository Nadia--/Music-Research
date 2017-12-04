# General Libraries
import re

COMMENT_CUTOFF_LEN = 80;

KEEP_SONG_RELATED = 'keep_song_related'
KEEP_TITLE_AND_ARTIST = 'keep_title_and_artist'

REMOVE_DUMB_COMMENTS = 'remove_dumb_people'
REMOVE_IF_NO_LIKES = 'remove_if_no_likes'
REMOVE_LONG = 'remove_long'
REMOVE_MOVIE_RELATED = 'remove_movie_related'
REMOVE_NONENGLISH_AND_IRRELEVANT = 'remove_nonenglish_irr'
REMOVE_NONENGLISH = 'remove_nonenglish'

eng100 = ['the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'I', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at', 'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she', 'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go', 'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know', 'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them', 'see', 'other', 'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also', 'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first', 'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these', 'give', 'day', 'most', 'us']

eng = [c for c in eng100 if len(c) >= 3]

# Runs Filters in the Order they are Specified
def run_filters(filter_tag_list, comments, title, artist):
    for filt in filter_tag_list:
        (filter_fn, key_words) = filters[filt]
        if filter_fn == comments_filter_title:
            comments_filter_keep(comments, [artist, title])
        else:
            comments = filter_fn(comments, key_words)
    return comments

# ====== Begin Filter Definitions ====== #
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

def comments_filter_english_vader(comments, key_words = None):
    return [comment for comment in comments if comment.vader_sentiment]

def comments_filter_english(comments, key_words = None):
    return [comment for comment in comments
            if set(comment.text.lower().split()) & set(eng)]

def comments_filter_likes(comments, key_words = None):
    return [comment for comment in comments 
            if comment.like_count > 0 or comment.keep == True]

def comments_filter_long(comments, key_words):
    return [comment for comment in comments 
            if len(comment.text) < COMMENT_CUTOFF_LEN or comment.keep == True]

def comments_filter_title(): return None
# ====== End Filter Definitions ====== #


# Alphabetical 
#TODO: choose whether re.search (can do multiple word matches, but also prone to substring matches), or whether use set intersection (can only do 1 word matches, but must be full word).
filters = {
      KEEP_SONG_RELATED: (comments_filter_keep, ['song', 'piece', 'sound'])
    , KEEP_TITLE_AND_ARTIST: (comments_filter_title, [])
    , REMOVE_DUMB_COMMENTS: (comments_filter_remove, ['setting', 'here'])
    # 'who's here from supernatural', 'lio rush brought me here'
    # 'if you change the setting to 1.5 speed it is slightly faster' 
    , REMOVE_IF_NO_LIKES: (comments_filter_likes, []) 
    , REMOVE_LONG: (comments_filter_long, [])
    , REMOVE_MOVIE_RELATED: (comments_filter_remove, ['Inhumans', 'Marvel', 'Lucifer'])
    , REMOVE_NONENGLISH_AND_IRRELEVANT: (comments_filter_english_vader, [])
    , REMOVE_NONENGLISH: (comments_filter_english, [])
}
