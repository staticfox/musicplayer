from dataclasses import dataclass


@dataclass
class Song(object):
    '''
    Represents a playable song from the file system.
    '''
    uid: str
    path: str
    filename: str
    time_secs: int
    title: str = ''
    artist: str = ''

    @property
    def abs_path(self) -> str:
        return f'{self.path}/{self.filename}'

    @property
    def filename_noext(self) -> str:
        return self.filename.rsplit('.')[0]

    @property
    def display_name(self) -> str:
        title = self.title or self.filename_noext
        artist = self.artist or 'Unknown Artist'
        return f'{title} - {artist}'
