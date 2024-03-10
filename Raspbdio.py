import os
import vlc

favorites_name = "Избранное"
empty_playlist_message = "Плейлист пуст"
parse_playlist_error_message = "Ошибка чтения плейлиста"
parse_station_name_error_message = "Ошибка получения имени станции"
class Raspbdio:
    def __init__(self, playlist_path):

        self.current_playlist_index = 0
        self.current_station_index = 0

        self.playlist_path = playlist_path
        self.playlists = ["%s.m3u"%favorites_name] + [f for f in os.listdir(playlist_path) if os.path.isfile(os.path.join(playlist_path, f)) and f.endswith(".m3u") and f != "%s.m3u"%favorites_name]
        
        try:
            with open('./station.txt', 'r') as f:
                saved_station = f.read()
        except FileNotFoundError:
            saved_station = ""
        try:
            with open('./playlist.txt', 'r') as f:
                saved_playlist = f.read()
        except FileNotFoundError:
            saved_playlist = ""

        self.favorite_stations, self.favorite_stations_dict = self._parse_favorite()

        for i in range(len(self.playlists)):
            if saved_playlist == self.playlists[i]:
                self.current_playlist_index = i
                break
        if len(self.favorite_stations) == 0 and self.current_playlist_index == 0 and len(self.playlists) > 1:
            self.current_playlist_index = 1

        self.stations, self.stations_data = self._parse_playlist()

        for i in range(len(self.stations)):
            if saved_station == self.stations[i]:
                self.current_station_index = i
                break
        self.stopped = False
        try:
            self.curent_station_title = self.stations[self.current_station_index]
        except IndexError:
            self.curent_station_title = empty_playlist_message
        self.media_player = vlc.MediaPlayer()
        self.media = None
        self.stream_statuses = {"OK": 0, "WAIT": 1, "ERROR": 2}
        self.stream_status=self.stream_statuses["ERROR"]
        self.stream_status_symbol="⚠"
        self.media_title=None
        self.media_note_symbol = "♪"

    def _parse_playlist(self):
        stations = []
        stations_data = {}
        with open(os.path.join(self.playlist_path, self.playlists[self.current_playlist_index]), 'r') as f:
            playlist_data = f.read().split('\n')
        extinf = False
        text_station_title = parse_station_name_error_message
        for row in playlist_data:
            if extinf:
                extinf = False
                stations_data[text_station_title] = {"stream": row}
            if row.startswith("#EXTINF"):
                extinf = True
                text_station_title = "".join(row.split(",")[1:]).strip()
                stations.append(text_station_title)
        return (stations, stations_data)

    def _parse_favorite(self):
        favorite_stations = []
        favorite_stations_dict = {}
        try:
            with open(os.path.join(self.playlist_path, "%s.m3u"%favorites_name), 'r') as f:
                playlist_data = f.read().split('\n')
        except FileNotFoundError:
            return ([], {})
        extinf = False
        text_station_title = parse_station_name_error_message
        for row in playlist_data:
            if extinf:
                extinf = False
                favorite_stations_dict[text_station_title] = {"stream": row}
            if row.startswith("#EXTINF"):
                extinf = True
                text_station_title = "".join(row.split(",")[1:])
                favorite_stations.append(text_station_title)
        return (favorite_stations, favorite_stations_dict)

    def playlist_changed(self):
        self.stations, self.stations_data = self._parse_playlist()
        self.current_station_index = 0
        self.update_state(self)

    def update_state(self):
        try:
            self.curent_station_title = self.stations[self.current_station_index]
        except IndexError:
            if len(self.stations) == 0:
                self.curent_station_title = empty_playlist_message
            else:
                self.curent_station_title = parse_playlist_error_message
        if len(self.stations) > 0:
            stream = self.stations_data[self.curent_station_title]["stream"]
            if self.media is None or self.media.get_mrl() != stream:
                self.media = vlc.Media(stream)
                self.media_player.set_media(self.media)
                self.media_player.play()
                self.save_data()
        else:
            self.media_player.stop()

        player_state = self.media_player.get_state()
        if player_state==vlc.State.Playing:
            self.stream_status_symbol = "▶"
            self.stream_status=self.stream_statuses['OK']
        elif player_state==vlc.State.Opening:
            self.stream_status_symbol = "⌛"
            self.stream_status=self.stream_statuses['WAIT']
        else:
            self.stream_status_symbol="⚠"
            self.stream_status=self.stream_statuses['ERROR']

        media = self.media_player.get_media()

        if media == None or media.get_meta(12) == None or media.get_meta(12) == "":
            self.media_title = None
        else:
            self.media_title = media.get_meta(12)
        if not self.media_title is None:
            if self.media_note_symbol == "♪":
                self.media_note_symbol="♫"
            else:
                self.media_note_symbol="♪"

    def save_data(self):
        with open('./station.txt','w') as f:
            f.write(self.stations[self.current_station_index])
        with open('./playlist.txt','w') as f:
            f.write(self.playlists[self.current_playlist_index])
        with open(os.path.join(self.playlist_path, "%s.m3u"%favorites_name),'w') as f:
            for fav_sta in self.favorite_stations:
                f.write("#EXTINF:-1,{title}\n{stream}\n".format(title=fav_sta, stream=self.favorite_stations_dict[fav_sta]["stream"]))