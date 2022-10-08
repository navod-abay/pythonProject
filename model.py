import sqlite3
from mutagen import mp3
from controller import Song
from pathlib import Path

ID3_CODEC_AR = {"ar_name": "TPE1"}
ID3_CODEC_AL = {"al_name": "TALB"}
ID3_CODEC_SO = {"so_name": "TIT2", "year": "TYER", "duration": "TLEN"}


def create_db():
    conn = sqlite3.Connection(":memory:")
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys=ON")
    c.execute("""CREATE TABLE Artist (
                Ar_id INTEGER PRIMARY KEY,
                AR_Name TEXT NOT NULL UNIQUE
                )""")
    c.execute("""CREATE TABLE Albums (
                Al_id INTEGER PRIMARY KEY,
                Al_Name TEXT UNIQUE NOT NULL,
                Tot_tracks INTEGER,
                Tot_time REAL,
                Ar_id INTEGER, 
                FOREIGN KEY (Ar_id) REFERENCES Artist(Ar_id) 
                )""")
    c.execute(""" CREATE TABLE Songs(
                So_id INTEGER PRIMARY KEY,
                So_name TEXT NOT NULL,
                Duration REAL,
                Al_id INTEGER,
                Ar_id INTEGER,
                Year TEXT,
                FOREIGN KEY (Al_id) REFERENCES Albums(Al_id),
                FOREIGN KEY (Ar_id) REFERENCES Artist(Ar_id)
                )""")
    c.execute(""" CREATE TABLE Playlists(
                Pl_id INTEGER PRIMARY KEY,
                Pl_name TEXT NOT NULL,
                Duration REAL,
                So_list TEXT
               )""")
    add_folder(test_path, c)
    create_local_pl(c)
    return conn, c




def mutagen_to_dict(muta: mp3.MP3):
    """" Take a mutagen object and return a dictionary for each table in the DB. missing data will be replaced with
        None"""
    tag = muta.tags
    if tag is None:
        return [{}, {}, {"so_name":muta.filename,"duration":None, "year":None}]
    ar_ta, al_ta, so_ta = {}, {}, {}
    table_map = [(ar_ta, ID3_CODEC_AR), (al_ta, ID3_CODEC_AL), (so_ta, ID3_CODEC_SO)]
    for table, id3 in table_map:
        for field_name, frame in id3.items():
            entry = tag.getall(frame)
            if not entry:  # if theres no frame in the id3 tag its set to None
                entry = None
            else:
                entry = entry[0]
                entry = str(entry).strip()
            table[field_name] = entry
    if so_ta["so_name"] is None:
        so_ta["so_name"] = muta.filename
    if so_ta["duration"] is None:
        so_ta["duration"] = muta.info.length *1000
    return [ar_ta, al_ta, so_ta]


def add_song(filepath: Path, c):
    """ Add the given song to the database. goes through the tables Artists, Albums, Songs in that order. If the title is
    not found the filename is kept as the title"""
    mp3_muta = mp3.MP3(filepath)
    dict_list = mutagen_to_dict(mp3_muta)
    if dict_list[0].get("ar_name"):
        try:
            c.execute("""INSERT INTO Artist(ar_name) 
                         VALUES (:ar_name)""", dict_list[0])
        except sqlite3.IntegrityError:  # pass if the entry is already there
            pass
        finally:    # get the artist id
            ar_id = c.execute("""SELECT Ar_id FROM Artist WHERE ar_name=?""", [dict_list[0].get("ar_name")])
            ar_id = ar_id.fetchone()
            ar_id = ar_id[0]
    else:
        ar_id = None
    dict_list[1].update({"Ar_id": ar_id})
    if dict_list[1].get("al_name"):
        try:
            c.execute("""INSERT INTO Albums(al_name, Ar_id) 
                         VALUES (:al_name, :Ar_id)""", dict_list[1])
        except sqlite3.IntegrityError:
            pass
        finally:
            al_id = c.execute("""SELECT Al_id FROM Albums WHERE Al_name=?""", [dict_list[1].get("al_name")])
            al_id = al_id.fetchone()
            al_id = al_id[0]
    else:
        al_id = None
    dict_list[2].update({"ar_id":ar_id, "al_id":al_id})
    c.execute("""INSERT INTO Songs(
                So_name, Duration, Al_id, Ar_id, Year)
                VALUES (:so_name, :duration, :al_id,:ar_id, :year)""", dict_list[2])



def add_folder(folderpath: Path, cursor):
    for filepath in folderpath.glob("*.mp3"):
        add_song(filepath, cursor)


def create_local_pl(c):
    c.execute(""" SELECT COUNT(*) from Songs """)
    so_count = c.fetchone()
    so_count = so_count[0]
    c.execute("""SELECT SUM(Duration) FROM Songs """)
    tot_dur = c.fetchone()[0]
    lo_so_id_li = str(list(range(so_count)))
    c.execute("""INSERT INTO Playlists(pl_name, Duration, so_list) VALUES (?,?,?)""", ["LOCAL FILES", tot_dur, lo_so_id_li])


class Play_list():
    def __init__(self, id, name, duration, id_list=None, cur_index=0):
        self.id = id
        self.name = name
        self.duration = duration
        if id_list:
            self.id_list = id_list
        else:
            self.id_list = []
        self.cur_index = 0

    def add_song(self, song):
        pass

    def add_mul_songs(self, index_list):
        self.id_list.extend(index_list)

    def remove_song(self, index):
        pass

    def get_next_id(self):
        self.cur_index += 1
        return self.id_list[self.cur_index]

    @classmethod
    def create_from_db(cls, id, name, duration, id_list):
        if not id_list is None:
            id_list = id_list.strip("[]")
            id_list = id_list.split(",")
            id_list = [int(x) for x in id_list]
        return cls(id, name, duration, id_list)



class Model():
    def __init__(self):
        self.current_playlist = Play_list(list(mp3s.keys()), 0, None)
        self.play_lists = []
        self.load_playlists()

    def get_next(self):
        index = self.current_playlist.get_next_id()
        mp3s[index].decode()
        return mp3s[index]

    def load_playlists(self):
        cursor.execute("""SELECT * FROM Playlists""")
        pl_list =  cursor.fetchall()
        for pl in pl_list:
            play_list = Play_list.create_from_db(*pl)
            self.play_lists.append(play_list)

    def get_song_from_id(self, so_id):
        cursor.execute("""SELECT * FROM Songs WHERE So_id=? """, (so_id,))
        song_info = cursor.fetchone()

test_dir = "/home/emil/Music"
test_path = Path(test_dir)
mp3s = {}
hash = 0  # A unique identifier for each mp3 file. A file will be referenced by that for the whole of the script

for file in test_path.glob("*.mp3"):
    mp3s[hash] = Song(file)
    hash += 1

if not Path("data.db").exists():
    connection, cursor = create_db()
else:
    connection = sqlite3.Connection("data.db")
    cursor = conn.cursor()

