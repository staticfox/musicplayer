from configparser import ConfigParser
from pathlib import Path
from queue import Queue

from flask import (
    Blueprint,
    Flask,
    jsonify,
    render_template,
)

from .player import Player
from .songdb import SongDB


def create_app():
    app = Flask(__name__)

    cwd = Path(__file__).parent.absolute()
    config_file = cwd / '..' / 'etc' / 'config.ini'

    config = ConfigParser()
    config.read(config_file)
    folder = Path(config['settings']['music_location']).expanduser().resolve()

    songdb = SongDB(folder)
    queue = Queue()
    player = Player(queue, songdb, config)
    player.daemon = True
    player.start()

    bp = Blueprint('app', __name__, template_folder='templates')

    @bp.route('/')
    def index():
        current_song = songdb.get_current()
        songs = songdb.get_songs()

        return render_template(
            'index.j2',
            current_song=current_song,
            songs=songs,
            folder=folder,
        )

    @bp.route('/start')
    def start():
        player.play_next()
        return ''

    @bp.route('/next')
    def next_route():
        player.play_next()
        return ''

    @bp.route('/previous')
    def prev():
        player.play_previous()
        return ''

    @bp.route('/stop')
    def stop():
        player.stop_music()
        songdb.set_current(None)
        return ''

    @bp.route('/shuffle')
    def shuffle():
        songdb.shuffle()
        player.play_next()
        return ''

    @bp.route('/reload_music_dir')
    def reload_music_path():
        songdb.load_path()
        return ''

    @bp.route('/set_song/<string:uid>')
    def set_song(uid: str):
        song = songdb.get(uid)
        if not song:
            return jsonify({'ok': False}), 404

        player.play_song(song)
        songdb.set_current(song)
        return jsonify({'ok': True})

    app.register_blueprint(bp)
    return app
