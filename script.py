#Project Libraries
import objects as Objects
import filters as Filters
import hdf5_helper as hh

#TODO: many MSDB songs don't have a youtube video with comments. filter them out.
#TODO: comment language classification
#TODO: look at MSDB tags
#TODO: ML correlations between tags and comments

songs = hh.get_all_files() #TODO songs = random.shuffle(songs)

for song_loc in songs:
    h5 = hh.open_h5_file_read(song_loc)
    artist = hh.get_artist_name(h5).decode('UTF-8')
    title = hh.get_title(h5).decode('UTF-8')
    print(artist, title)

    songA = Objects.Song(artist, title)
    songB = Objects.Song(artist, title)

    # No Filters
    filter_tag_list_A = []

    # Order Matters
    filter_tag_list_B = [Filters.REMOVE_LONG,
            Filters.REMOVE_IF_NO_LIKES, 
            Filters.REMOVE_DUMB_COMMENTS, 
            Filters.KEEP_TITLE_AND_ARTIST, 
            Filters.KEEP_SONG_RELATED, 
            Filters.REMOVE_MOVIE_RELATED]

    print('AB Testing: A')
    songA.fetch_youtube_comments(10, filter_tag_list_A)
    songA.analyze_sentiment(Objects.SENTIMENT_VADER)
    #songA.analyze_sentiment(Objects.SENTIMENT_USER)
    #songA.compare_analysis()
    print(songA)

    print('AB Testing: B')
    songB.fetch_youtube_comments(10, filter_tag_list_B)
    songB.analyze_sentiment(Objects.SENTIMENT_VADER)
    #songB.analyze_sentiment(Objects.SENTIMENT_USER)
    #songB.compare_analysis()
    print(songB)

    h5.close()
