#Project Libraries
import objects as Objects
import filters as Filters

black = Objects.Song('Ciara', 'Paint It Black')

# Order Matters
filter_tag_list = [Filters.REMOVE_LONG,
        Filters.REMOVE_IF_NO_LIKES, 
        Filters.REMOVE_DUMB_COMMENTS, 
        Filters.KEEP_TITLE_AND_ARTIST, 
        Filters.KEEP_SONG_RELATED, 
        Filters.REMOVE_MOVIE_RELATED]
#filter_tag_list = []

black.fetch_youtube_comments(40, filter_tag_list)

black.analyze_sentiment()

print(black)
