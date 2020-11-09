from pathlib import Path
from random import shuffle
from typing import (
    Deque,
    Generator,
    Optional,
)

from .song import Song
from .utils import load_list


class SongDB(object):
    def __init__(self, path: Path = None):
        self._current = None
        self._song_list = None
        self._path = path

        if path is not None:
            self.load_path()

    def load_path(self) -> None:
        song_list = load_list(self._path)
        self.set_list(song_list)
        self.shuffle()

    def next(self) -> Optional[Song]:
        if not self._song_list:
            return None

        song = self._song_list.popleft()
        self.set_current(song)
        self._song_list.append(song)
        return self.get_current()

    def prev(self) -> Optional[Song]:
        if not self._song_list:
            return None

        song = self._song_list.pop()
        self._song_list.appendleft(song)
        self.set_current(song)
        return self.get_current()

    def set_current(self, song: Song) -> None:
        self._current = song

    def get_current(self) -> Song:
        return self._current

    def set_list(self, song_list: Deque[Song]) -> None:
        self._song_list = song_list

    def get_songs(self) -> Generator[Song, None, None]:
        yield from self._song_list

    def shuffle(self) -> None:
        shuffle(self._song_list)

    def get(self, uid: str) -> Optional[Song]:
        for song in self.get_songs():
            if song.uid == uid:
                return song
        return None
