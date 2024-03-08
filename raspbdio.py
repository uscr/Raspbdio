#!/usr/bin/python3

import vlc, os, random, datetime
from guizero import App, Text, PushButton, Box

playlist_path = "playlists"

def station_prev():
    global current_station_index
    if current_station_index == 0:
        current_station_index = len(stations)-1
    else:
        current_station_index -= 1
    update_text_and_housekeep()
    play_stream()
    save_data()

def station_next():
    global current_station_index
    if current_station_index == len(stations)-1:
        current_station_index = 0
    else:
        current_station_index += 1
    update_text_and_housekeep()
    play_stream()
    save_data()

def station_random():
    global random_sta
    random_sta = True
    if len(stations) > 1:
        global current_station_index
        random_station_index = current_station_index
        while random_station_index == current_station_index:
            random_station_index = random.randint(0, len(stations)-1)
        current_station_index = random_station_index
        update_text_and_housekeep()
        play_stream()
        save_data()

def station_fav():
    global favorite_stations
    title = stations[current_station_index]
    stream = stations_data[title]["stream"]
    if stream == favorite_stations_dict.get(title, {"stream":""})["stream"]:
        del favorite_stations_dict[title]
        favorite_stations.remove(title)
        if current_playlist_index == 0:
            save_data()
            parse_playlist(True)
            play_stream()
    else:
        favorite_stations_dict[title] = {"stream": stream}
        favorite_stations.append(title)
        save_data()
    update_text_and_housekeep()

def playlist_prev():
    global current_playlist_index
    if current_playlist_index == 0:
        current_playlist_index = len(playlists)-1
    else:
        current_playlist_index -= 1
    parse_playlist(True)
    update_text_and_housekeep()
    play_stream()
    save_data()

def playlist_next():
    global current_playlist_index
    if current_playlist_index == len(playlists)-1:
        current_playlist_index = 0
    else:
        current_playlist_index += 1
    parse_playlist(True)
    update_text_and_housekeep()
    play_stream()
    save_data()

def parse_playlist(event=False):
    if event:
        global stations
        global stations_data
        global current_station_index
        current_station_index = 0
    stations = []
    stations_data = {}
    with open(os.path.join(playlist_path, playlists[current_playlist_index]), 'r') as f:
        playlist_data = f.read().split('\n')
    extinf = False
    text_station_title = "Parse failed"
    for row in playlist_data:
        if extinf:
            extinf = False
            stations_data[text_station_title] = {"stream": row}
        if row.startswith("#EXTINF"):
            extinf = True
            text_station_title = "".join(row.split(",")[1:]).strip()
            stations.append(text_station_title)
    if not event:
        return (stations, stations_data)

def parse_favorite():
    favorite_stations = []
    favorite_stations_dict = {}
    try:
        with open(os.path.join(playlist_path, "Избранное.m3u"), 'r') as f:
            playlist_data = f.read().split('\n')
    except FileNotFoundError:
        return ([], {})
    extinf = False
    text_station_title = "Parse failed"
    for row in playlist_data:
        if extinf:
            extinf = False
            favorite_stations_dict[text_station_title] = {"stream": row}
        if row.startswith("#EXTINF"):
            extinf = True
            text_station_title = "".join(row.split(",")[1:])
            favorite_stations.append(text_station_title)
    return (favorite_stations, favorite_stations_dict)

# Обновляет текст на дисплее
# Перезапускает рандомный поиск если поток не удаётся получить
def update_text_and_housekeep():
    global note_symbol
    global random_sta
    global random_sta_opening_timestamp
    global random_sta_playing_timestamp
    global random_sta_error_timestamp
    player_state = media_player.get_state()
    if player_state==vlc.State.Playing:
        stream_status = "▶"
        if random_sta and random_sta_playing_timestamp == None:
            random_sta_playing_timestamp = datetime.datetime.now()
        else:
            if random_sta and datetime.datetime.now() - random_sta_playing_timestamp > random_sta_playing_timeout:
                random_sta = False
                random_sta_playing_timestamp = random_sta_opening_timestamp = random_sta_error_timestamp = None
    elif player_state==vlc.State.Opening:
        stream_status = "⌛"
        if random_sta and random_sta_opening_timestamp == None:
            random_sta_opening_timestamp = datetime.datetime.now()
        else:
            if random_sta and datetime.datetime.now() - random_sta_opening_timestamp > random_sta_opening_timeout:
                random_sta_opening_timestamp = None
                station_random()
    else:
        stream_status="⚠"
        if random_sta and random_sta_error_timestamp == None:
            random_sta_error_timestamp = datetime.datetime.now()
        else:
            if random_sta and datetime.datetime.now() - random_sta_error_timestamp > datetime.timedelta(seconds=5):
                random_sta_error_timestamp = None
                station_random()

    curent_station_title = stations[current_station_index]
    curr_sta_title_len = len(curent_station_title)
    if curr_sta_title_len >= 45:
        text_station_title.size = 9
    elif curr_sta_title_len >= 35:
        text_station_title.size = 16
    elif curr_sta_title_len >= 30:
        text_station_title.size = 20
    else:
        text_station_title.size = 24

    text_station_index.value = "Станция {cur_sta} из {sta_cnt}".format(cur_sta=current_station_index+1, sta_cnt=len(stations))
    text_station_title.value = "{status} {title}".format(status=stream_status if not mute else "", title=curent_station_title)
    media = media_player.get_media()
    media_meta = []
    for i in range(0,13):
        media_meta.append(media.get_meta(i))

    if media_meta[12] == None:
        media_meta[12] = ""

    if len(media_meta[12]) > 40:
        text_media_title.size = 9
    elif len(media_meta[12]) >= 30:
        text_media_title.size = 12
    else:
        text_media_title.size = 16
    if not (media_meta[12] is None or media_meta[12]==""):
        if note_symbol == "♪":
            note_symbol="♫"
        else:
            note_symbol="♪"
        text_media_title.value = "{note} {title} {note}".format(title=media_meta[12] if not mute else "", note=note_symbol if not mute else "")
    else:
        text_media_title.value = ""

    text_playlist_index.value = "Плейлист {cur_pla} из {pla_cnt}".format(cur_pla=current_playlist_index+1, pla_cnt=len(playlists))
    text_playlist_title.value = "{title}".format(title=playlists[current_playlist_index].replace('.m3u',''))

    stream = stations_data[curent_station_title]["stream"]
    if stream == favorite_stations_dict.get(curent_station_title, {"stream":""})["stream"]:
        button_favs_station.text = "DEL ❤"
    else:
        button_favs_station.text = "❤"

    if mute:
        button_mute.text = "Unmute"
    else:
        button_mute.text = "Mute"

def play_stream():
    title = stations[current_station_index]
    stream = stations_data[title]["stream"]
    media = vlc.Media(stream)
    media_player.set_media(media)
    media_player.play()

def mute_stream():
    global mute
    if mute:
        media_player.play()
        mute = False
    else:
        media_player.stop()
        mute = True
    update_text_and_housekeep()

def save_data():
    station = stations[current_station_index]
    playlist = playlists[current_playlist_index]
    with open('/etc/radio/station.txt','w') as f:
        f.write(station)
    with open('/etc/radio/playlist.txt','w') as f:
        f.write(playlist)
    with open(os.path.join(playlist_path, 'Избранное.m3u'),'w') as f:
        for fav_sta in favorite_stations:
            f.write("#EXTINF:-1,{title}\n{stream}\n".format(title=fav_sta, stream=favorite_stations_dict[fav_sta]["stream"]))


if __name__ == '__main__':
    playlists = ["Избранное.m3u"]
    playlists += [f for f in os.listdir(playlist_path) if os.path.isfile(os.path.join(playlist_path, f)) and f.endswith(".m3u") and f != "Избранное.m3u"]
    # Текущий плейлист (global в процедурах)
    current_playlist_index = 0
    # Станция в выбранном плейлисте (global в процедурах)
    current_station_index = 0
    # Используется в анимации названия трека в update_text_and_housekeep(). Да, она тоже глобальная!
    note_symbol="♪"
    # Используется как признак рандомного поиска станции для продолжения поиска в случае битого потока. Разумеется, global
    random_sta = False
    # Таймстемп старта и таймаут ожидания стабилизации потока случайной станции для ошибочного статуса
    random_sta_error_timestamp = None
    # Таймстемп старта и таймаут ожидания стабилизации потока случайной станции для статуса vlc.State.Opening
    random_sta_opening_timestamp = None
    random_sta_opening_timeout = datetime.timedelta(seconds=10)
    # Таймаут ожидания стабилизации потока случайной станции для статуса vlc.State.Playing
    # Этот статус не означает что всё уже хорошо, лол
    random_sta_playing_timestamp = None
    random_sta_playing_timeout = datetime.timedelta(seconds=5)
    # Статус мьюта
    mute = False

    with open('/etc/radio/station.txt', 'r') as f:
        saved_station = f.read()
    with open('/etc/radio/playlist.txt', 'r') as f:
        saved_playlist = f.read()

    for i in range(len(playlists)):
        if saved_playlist == playlists[i]:
            current_playlist_index = i
            print("Founded playlist %s index %s"%(saved_playlist, i))
            break

    stations, stations_data = parse_playlist()
    favorite_stations, favorite_stations_dict = parse_favorite()

    for i in range(len(stations)):
        if saved_station == stations[i]:
            current_station_index = i
            print("Founded station %s index %s"%(saved_station, i))
            break

    media_player = vlc.MediaPlayer()

    app = App(title="Radio", bg="black", layout="auto")
    app.set_full_screen()

    # Playlist controllers (need to be alignet to bottom first for be a really bottom)
    playlist_box = Box(app, width="fill", align="top", border=False)
    button_prev_playlist = PushButton(playlist_box, command=playlist_prev, text="<", height=1, width=15, align="left")
    button_next_playlist = PushButton(playlist_box, command=playlist_next, text=">", height=1, width=15, align="right")
    text_playlist_index = Text(playlist_box, text="", color="gray", height=2, width="fill", size=9)
    text_playlist_title = Text(playlist_box, text="", color="gray", height=1, width="fill", size=12)
    button_prev_playlist.text_color="gray"
    button_next_playlist.text_color="gray"

    # Station controllers
    station_button_box = Box(app, width="fill", border=False)
    button_prev_station = PushButton(station_button_box, command=station_prev, text="<", height=6, width=15, align="left")
    button_next_station = PushButton(station_button_box, command=station_next, text=">", height=6, width=15, align="right")
    button_rnd_station = PushButton(station_button_box, command=station_random, text="Random", height=2, width=19, align="top")
    button_mute = PushButton(station_button_box, command=mute_stream, text="Mute", height=2, width=8, align="left")
    button_favs_station = PushButton(station_button_box, command=station_fav, text="❤", height=2, width=8, align="right")
    button_prev_station.text_color="gray"
    button_next_station.text_color="gray"
    button_rnd_station.text_color="gray"
    button_mute.text_color="gray"
    button_favs_station.text_color="gray"

    # Station info
    station_box = Box(app, width="fill", align="bottom", border=False)
    text_station_title = Text(station_box, text="", color="gray", height=2, width="fill", align="top", size=24)
    text_media_title = Text(station_box, text="", color="gray", height=2, width="fill", align="top", size=16)
    text_station_index = Text(station_box, text="", color="gray", height=2, width="fill", align="bottom", size=9)

    play_stream()
    update_text_and_housekeep()
    text_station_title.repeat(1000, update_text_and_housekeep)  
    app.display()
