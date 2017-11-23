#Project Libraries
import objects as Objects
import filters as Filters
import hdf5_helper as hh

NUM_COMMENTS = 10

#TODO: comment language classification
#TODO: look at MSDB tags
#TODO: ML correlations between tags and comments

def get_comments(song, filter_tag_list, char, filt_songs=None):
    song.fetch_youtube_comments(NUM_COMMENTS, filter_tag_list)
    if song.error is not True:
        song.analyze_sentiment(Objects.SENTIMENT_VADER)
        #song.analyze_sentiment(Objects.SENTIMENT_USER)
        #song.compare_analysis()
        if len(song.comments) >= NUM_COMMENTS:
            if char == 'B' and filt_songs is not None:
                filt_songs.append(song)
            print('AB Testing: %c' % char)
            print(song)

songs = hh.get_all_files() #TODO songs = random.shuffle(songs)
num_total = 0
filt_songs = []

for idx, song_loc in enumerate(songs):
    h5 = hh.open_h5_file_read(song_loc)
    artist = hh.get_artist_name(h5).decode('UTF-8')
    title = hh.get_title(h5).decode('UTF-8')
    print(idx, artist, title)

    # A
    songA = Objects.Song(artist, title)
    filter_tag_list_A = []
    get_comments(songA, filter_tag_list_A, 'A')

    # B
    songB = Objects.Song(artist, title)
    filter_tag_list_B = [Filters.REMOVE_LONG,
            Filters.REMOVE_IF_NO_LIKES, 
            Filters.REMOVE_DUMB_COMMENTS, 
            Filters.KEEP_TITLE_AND_ARTIST, 
            Filters.KEEP_SONG_RELATED, 
            Filters.REMOVE_MOVIE_RELATED]
    get_comments(songB, filter_tag_list_B, 'B', filt_songs)

    num_total+=1
    h5.close()

percentage = len(filt_songs) / num_total*100 
print('%d total songs\n%d usable songs\n%d%% usable' % ( num_total, len(filt_songs), round(percentage)))
