#!/usr/bin/python3

import vlc, random, datetime
from time import localtime, strftime
from Raspbdio import Raspbdio
from tkinter import *

playlist_path = "./playlists"

stop_button_label = "Стоп"
random_button_label = "Случайная"
favorite_button_label = "❤"
delete_favorite_button_label = "Убрать\n❤"
station_word = "Станция"
from_word = "из"
playlist_word = "Плейлист"

def station_prev(raspbdio):
    if raspbdio.current_station_index == 0:
        raspbdio.current_station_index = len(raspbdio.stations)-1
    else:
        raspbdio.current_station_index -= 1

def station_next(raspbdio):
    if raspbdio.current_station_index == len(raspbdio.stations)-1:
        raspbdio.current_station_index = 0
    else:
        raspbdio.current_station_index += 1

def playlist_prev(raspbdio):
    if raspbdio.current_playlist_index == 0:
        raspbdio.current_playlist_index = len(raspbdio.playlists)-1
    else:
        raspbdio.current_playlist_index -= 1
    raspbdio.playlist_changed()

def playlist_next(raspbdio):
    global current_playlist_index
    if raspbdio.current_playlist_index == len(raspbdio.playlists)-1:
        raspbdio.current_playlist_index = 0
    else:
        raspbdio.current_playlist_index += 1
    raspbdio.playlist_changed()

def station_random(raspbdio, btn):
    if len(raspbdio.stations) > 1:
        random_station_index = raspbdio.current_station_index
        while random_station_index == raspbdio.current_station_index:
            random_station_index = random.randint(0, len(raspbdio.stations)-1)
        raspbdio.current_station_index = random_station_index
        btn.after(1000, lambda : check_random_choice(raspbdio, btn, 0))

def check_random_choice(raspbdio, btn, check_num):
    if raspbdio.stream_status == raspbdio.stream_statuses["OK"]:
        return

    if raspbdio.stream_status == raspbdio.stream_statuses["WAIT"]:
        if check_num <= 10:
            btn.after(1000, lambda : check_random_choice(raspbdio, btn, check_num+1))
        else:
            station_random(raspbdio, btn)

    if raspbdio.stream_status == raspbdio.stream_statuses["ERROR"]:
        if check_num == 0:
            btn.after(1000, lambda : check_random_choice(raspbdio, btn, check_num+1))
        else:
            station_random(raspbdio, btn)

def station_fav(raspbdio):

    title = raspbdio.stations[raspbdio.current_station_index]
    stream = raspbdio.stations_data[title]["stream"]
    if stream == raspbdio.favorite_stations_dict.get(title, {"stream":""})["stream"]:
        del raspbdio.favorite_stations_dict[title]
        raspbdio.favorite_stations.remove(title)
    else:
        raspbdio.favorite_stations_dict[title] = {"stream": stream}
        raspbdio.favorite_stations.append(title)
    raspbdio.save_data()

def station_stop(raspbdio):
    if raspbdio.stopped:
        raspbdio.media_player.play()
        raspbdio.stopped = False
    else:
        raspbdio.media_player.stop()
        raspbdio.stopped = True

def update_state(root, raspbdio):
    raspbdio.update_state()
    root.after(1000, lambda : update_state(root, raspbdio))

def label_textkeeper(label, max_font_size, min_font_size=10, magic_number=730):
    text_len = len(label.cget('text'))
    if text_len == 0:
        text_len = 1
    if magic_number/text_len > max_font_size:
        label.config(font=("Arial", max_font_size))
    elif magic_number/text_len < min_font_size:
        label.config(font=("Arial", min_font_size))
    else:
        label.config(font=("Arial", int(magic_number/text_len)))
    label.after(100, lambda : label_textkeeper(label, max_font_size))

def update_sys_info(label):
    label.config(text=strftime("%H:%M:%S", localtime()))
    label.after(500, lambda : update_sys_info(label))

def update_station_info(label, raspbdio):
    label.config(text="{station} {cur_sta} {from_word} {sta_cnt}".format(station=station_word, from_word=from_word, cur_sta=raspbdio.current_station_index+1, sta_cnt=len(raspbdio.stations)))
    label.after(300, lambda : update_station_info(label, raspbdio))

def update_plailist_index(label, raspbdio):
    label.config(text="{playlist} {cur_pla} {from_word} {pla_cnt}".format(playlist=playlist_word, from_word=from_word, cur_pla=raspbdio.current_playlist_index+1, pla_cnt=len(raspbdio.playlists)))
    label.after(300, lambda : update_plailist_index(label, raspbdio))

def update_plailist_name(label, raspbdio):
    label.config(text="{title}".format(title=raspbdio.playlists[raspbdio.current_playlist_index].replace('.m3u','')))
    label.after(300, lambda : update_plailist_name(label, raspbdio))

def update_sta_label(label, raspbdio):
    label.config(text="{status} {title}"\
                 .format(status=raspbdio.stream_status_symbol if not raspbdio.stopped else "", title=raspbdio.curent_station_title))
    label.after(300, lambda : update_sta_label(label, raspbdio))

def update_media_label(label, raspbdio):
    label.config(text="{note} {title}"\
    .format(note=raspbdio.media_note_symbol, title=raspbdio.media_title) if not raspbdio.media_title is None and not raspbdio.stopped else "" )
    label.after(1000, lambda : update_media_label(label, raspbdio))

def update_stop_button(button, raspbdio):
    button.config(text="{text}".format(text="▶" if raspbdio.stopped else stop_button_label))
    button.after(300, lambda : update_stop_button(button, raspbdio))

def update_favs_button(button, raspbdio):
    stream = raspbdio.media.get_mrl()
    if stream == raspbdio.favorite_stations_dict.get(raspbdio.stations[raspbdio.current_station_index], {"stream":""})["stream"]:
        button.config(text = delete_favorite_button_label)
    else:
        button.config(text = favorite_button_label)
    button.after(1000, lambda : update_favs_button(button, raspbdio))

if __name__ == '__main__':
    raspbdio = Raspbdio(playlist_path)

    bgcolor = "#1D1D1D"
    fontcolor = "#D1D1D1"

    root = Tk()
    root.attributes('-fullscreen', True)
    root.title("Raspbdio")
    root.configure(background=bgcolor)
    root.update()

    base_width = root.winfo_width()
    base_height = root.winfo_height()

    # Информация о системе
    sys_info = Label(root, text="", anchor="center", bg=bgcolor, fg=fontcolor, font=("Arial", int(base_height/40)))
    sys_info.place(relx=1, rely=0.01, anchor="ne")
    
    sys_info.after(500, lambda : update_sys_info(sys_info))

    # Информация о выбранной радиостанции
    sta_index = Label(root, text="", anchor="center", bg=bgcolor, fg=fontcolor, font=("Arial", int(base_height/40)))
    sta_index.place(relx=0, rely=0.01, anchor="nw")

    sta_index.after(500, lambda : update_station_info(sta_index, raspbdio))

    sta_label = Label(root, text="Ultra", anchor="center", bg=bgcolor, fg=fontcolor, font=("Arial", 10))
    sta_label.place(relx=0.5, rely=0.12, relwidth=1, anchor="c")
    sta_media_label = Label(root, text="Виктор Цой", anchor="center", bg=bgcolor, fg=fontcolor, font=("Arial", 10))
    sta_media_label.place(relx=0.5, rely=0.26, relwidth=1, anchor="c")
    
    sta_label.after(500, lambda : label_textkeeper(sta_label, int(base_height/12), int(base_height/40)))
    sta_label.after(500, lambda : update_sta_label(sta_label, raspbdio))
    sta_media_label.after(500, lambda : label_textkeeper(sta_media_label, int(base_height/12), int(base_height/40)))
    sta_media_label.after(500, lambda : update_media_label(sta_media_label, raspbdio))

    # Кнопки управления станцией
    sta_prev_btn = Button(root, text="<", command=lambda : station_prev(raspbdio),\
        bg=bgcolor, fg=fontcolor, activebackground=bgcolor, activeforeground=fontcolor, borderwidth=0, font=("Arial", int(base_height/5), "bold"))
    sta_prev_btn.place(relx=0, rely=0.55, relwidth=0.29, relheight=0.41, anchor="w")
    
    sta_next_btn = Button(root, text=">", command=lambda : station_next(raspbdio),\
        bg=bgcolor, fg=fontcolor, activebackground=bgcolor, activeforeground=fontcolor, font=("Arial", int(base_height/5), "bold"))
    sta_next_btn.place(relx=1, rely=0.55, relwidth=0.29, relheight=0.41, anchor="e")
    
    sta_rndm_btn = Button(root, text=random_button_label, command=lambda : station_random(raspbdio, sta_rndm_btn),\
        bg=bgcolor, fg=fontcolor, activebackground=bgcolor, activeforeground=fontcolor, font=("Arial", int(base_height/15)))
    sta_rndm_btn.place(relx=0.5, rely=0.45, relwidth=0.39, relheight=0.2, anchor="center")

    sta_favs_btn = Button(root, text=favorite_button_label, command=lambda : station_fav(raspbdio),\
        bg=bgcolor, fg=fontcolor, activebackground=bgcolor, activeforeground=fontcolor, font=("Arial", int(base_height/15)))
    sta_favs_btn.place(relx=0.4, rely=0.66, relwidth=0.19, relheight=0.2, anchor="center")

    sta_stop_btn = Button(root, text=stop_button_label, command=lambda : station_stop(raspbdio),\
        bg=bgcolor, fg=fontcolor, activebackground=bgcolor, activeforeground=fontcolor, font=("Arial", int(base_height/15)))
    sta_stop_btn.place(relx=0.6, rely=0.66, relwidth=0.19, relheight=0.2, anchor="center")
    
    sta_stop_btn.after(500, lambda : update_stop_button(sta_stop_btn, raspbdio))
    sta_favs_btn.after(1000, lambda : update_favs_button(sta_favs_btn, raspbdio))

    # Кнопки выбора плейлиста и информация о плейлисте
    pla_prev_btn = Button(root, text="<", command=lambda : playlist_prev(raspbdio), \
        bg=bgcolor, fg=fontcolor, activebackground=bgcolor, activeforeground=fontcolor, font=("Arial", int(base_height/10), "bold"))
    pla_prev_btn.place(relx=0, rely=1, relwidth=0.3, height=int(base_height/6), anchor="sw")
    
    pla_next_btn = Button(root, text=">", command=lambda : playlist_next(raspbdio),\
        bg=bgcolor, fg=fontcolor, activebackground=bgcolor, activeforeground=fontcolor, font=("Arial", int(base_height/10), "bold"))
    pla_next_btn.place(relx=1, rely=1, relwidth=0.3, height=int(base_height/6), anchor="se")

    pla_label = Label(root, text="", anchor="center", bg=bgcolor, fg=fontcolor)
    pla_label.place(relx=0.5, rely=0.92, relwidth=0.4, anchor="s")

    pla_index = Label(root, text="", anchor="center", bg=bgcolor, fg=fontcolor, font=("Arial", int(base_height/25)))
    pla_index.place(relx=0.5, rely=1, relwidth=0.4, anchor="s")
    
    pla_label.after(500, lambda : label_textkeeper(pla_label, int(base_height/20), int(base_height/40), magic_number=500))
    pla_label.after(500, lambda : update_plailist_name(pla_label, raspbdio))
    pla_index.after(500, lambda : update_plailist_index(pla_index, raspbdio))

    root.after(500, lambda : update_state(root, raspbdio))

    root.mainloop()
    # update_text_and_housekeep()
    # text_station_title.repeat(1000, update_text_and_housekeep)  
    # app.display()
