from datetime import datetime
import os
from pathlib import Path
from queue import Empty
from subprocess import (
    DEVNULL,
    Popen,
)
import threading
from time import sleep

import pytz

from .song import Song


class Player(threading.Thread):
    def __init__(self, queue, songdb, config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._queue = queue
        self._songdb = songdb
        self._player = None
        self._running = True
        self._changing_songs = False
        self._paused = False
        self._config = config

    @property
    def playing(self):
        if self._player is None:
            # Player not running
            return False

        result = self._player.poll()
        if result is not None:
            # Received a returncode, player stopped
            return False

        # Playing music
        return True

    @property
    def within_schedule(self):
        '''
        Only play between 7am and 10pm local time if the schedule
        itself is enabled.
        '''
        if not self._config['schedule']['enabled']:
            return True

        local_tz = pytz.timezone(self._config['schedule']['timezone'])
        now = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(local_tz)
        if now.hour > 7 and now.hour < 22:
            return True
        return False

    def play_song(self, song: Song):
        self._changing_songs = True

        for path in self._config['settings'].get('path_env_extras', []):
            expanded_path = str(Path(path).expanduser().resolve()).strip().rstrip()
            os.environ['PATH'] += ':' + expanded_path

        if self.playing:
            self._player.terminate()

        player_args = self._config['settings']['player_arg_fmt'].split(' ')

        variables = {
            r'%filepath%': song.abs_path,
            r'%duration%': str(song.time_secs),
        }

        for idx, arg in enumerate(player_args):
            for var_key, var_val in variables.items():
                if var_key in arg:
                    player_args[idx] = arg.replace(var_key, var_val)

        self._player = Popen(player_args, stdout=DEVNULL, stderr=DEVNULL)
        print(f'Now playing: {song.display_name}')

        self._changing_songs = False

    def play_next(self):
        self._paused = False

        next_song = self._songdb.next()
        self.play_song(next_song)

    def play_previous(self):
        next_song = self._songdb.prev()
        self.play_song(next_song)

    def stop_music(self):
        self._paused = True

        if self._player:
            self._player.terminate()

            result = None
            while result is None:
                result = self._player.poll()

            print('Stopped player.')

        self._songdb.set_current(None)

    def run(self):
        while self._running:
            if self._paused:
                sleep(0.01)
                continue

            if not self.within_schedule:
                if not self._paused:
                    self.stop_music()
                sleep(10)
                continue

            try:
                song = self._queue.get(False, 0.01)
                self.play_song(song)
            except Empty:
                if not self.playing and not self._changing_songs:
                    self.play_next()
            except KeyboardInterrupt:
                self._running = False

        print('Stopping player.')
