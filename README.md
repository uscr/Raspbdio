# Raspbdio

Yet another simple internet radio for a single-board computer.

Tested with Raspberry Pi 2B with rasbbian bullseye, but will work on any computer with any linux distribution.

Origin of this repo: [gitlab.uscr.ru/raspbdio](https://gitlab.uscr.ru/public-projects/raspbdio)

* [Author](#author)
* [Installation](#installation)
    * [Installation of the Rasbdio](#software-installation)
    * [Manage playlists](#manage-playlists)
    * [Starting Rasbpdio](#starting-rasbpdio)
    * [How to hide mouse pointer for touchscreens (byllseyey or older)](#hide-mouse-pointer)
* [User manual](#user-manual)
    * [Application window overview]
    * [Playlist controls](#playlist-controls)
    * [Station controls](#station-controls)
    * [Station information](#station-info)

## Author

Telegram [UsCr0](https://t.me/UsCr0)

## Installation

### Software installation

    ... clone this repo and cd to cloned directory ...

    sudo apt -y install python3-pip vlc
    sudo pip3 install -r requirements.txt
    mkdir -p ~/raspbdio/playlists
    cp raspbdio.py ~/raspbdio/raspbdio.py
    sudo cp raspbdio.service /etc/systemd/system/raspbdio.service
    sudo sed -i "s/<USER>/$USER/g" /etc/systemd/system/raspbdio.service
    sudo systemctl daemon-reload
    sudo systemctl enable raspbdio.service

### Manage playlists

Add playlists in m3u format to ~/raspbdio/playlists.

You can find playlists, for example, in this github repository: [junguler/m3u-radio-music-playlists](https://github.com/junguler/m3u-radio-music-playlists)

### Starting Rasbpdio

    sudo systemctl start raspbdio.service

### Hide mouse pointer

    #Useful for raspbian byllseye or older
    sudo sed -i -- "s/#xserver-command=X/xserver-command=X -nocursor/" /etc/lightdm/lightdm.conf
    reboot

# User manual

## Raspbdio screen overview
![Raspbdio app window](images/raspbdio_screen.png)

Where is 3 lines:
* [Playlist controls](#playlist-controls)
* [Station controls](#station-controls)
* [Station information](#station-info)

### Playlist controls

![Raspbdio playlist controls](images/raspbdio_playlist.png)

Buttons < and > allows you to select a playlist from ~/raspbdio/playlists directory.

### Station controls

![Raspbdio station controls](images/raspbdio_station_controls.png)

* Buttons < and > allow you to select a station from the current playlist.
* Use the "Random" button to play a random station from the current playlist.
    * If the randomly selected station has any problems with the stream, Rasbpdio will automatically retry the random choice until a working station is found.
* The "Mute" button is for stopping the current station stream.
* ❤️ Adding a station to the "Favorites" playlist.
    * The "Favorites" playlist is called "Избранное.m3u". It will always be the first playlist.

### Station info

![Raspbdio station info](images/raspbdio_station_info.png)

* "snakedance" is the current station name as it is written in the playlist file.
    * The symbol on the left side of the station name indicates the stream status. Raspbdio retrieves it from the VLC player instance:
        * ▶ means the stream is working fine.
        * ⌛ means "connecting".
        * ⚠ is for any other status (such as "Error").
* "Rob Zombie - Feel So Numb" is the song name from the station's metadata.
    * Not every station allows reading metadata, so the song name may not be available for different stations.