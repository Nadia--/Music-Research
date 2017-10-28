#Project Libraries
import objects as Objects
import filters as Filters

song1 = Objects.Song('Duran Duran', 'Come Undone')

# Order Matters
filter_tag_list = [Filters.REMOVE_LONG,
        Filters.REMOVE_IF_NO_LIKES, 
        Filters.REMOVE_DUMB_COMMENTS, 
        Filters.KEEP_TITLE_AND_ARTIST, 
        Filters.KEEP_SONG_RELATED, 
        Filters.REMOVE_MOVIE_RELATED]
#filter_tag_list = []

song1.fetch_youtube_comments(40, filter_tag_list)

song1.analyze_sentiment(Objects.SENTIMENT_VADER)
print(song1)

song1.analyze_sentiment(Objects.SENTIMENT_USER)
song1.compare_analysis()

print(song1)
