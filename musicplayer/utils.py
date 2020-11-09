from collections import deque
from os import walk
from typing import Deque

import eyed3

from .song import Song


def load_list(path: str) -> Deque[Song]:
    song_list = deque()

    for root, dirs, files in walk(path):
        for file in files:
            if not file.endswith('.mp3'):
                continue

            abs_path = f'{root}/{file}'
            title = artist = ''

            audiofile = eyed3.load(abs_path)
            tags = audiofile.tag

            if tags:
                title = tags.title
                artist = tags.artist

            song = Song(
                uid=str(len(song_list) + 1),
                path=root,
                filename=file,
                title=title,
                artist=artist,
                time_secs=audiofile.info.time_secs,
            )
            song_list.append(song)

    print(f'Loaded {len(song_list)} MP3 files from {path}')
    return song_list
