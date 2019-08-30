import psycopg2
from OWScraper import scraper
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


class OWParser:

    def __init__(self, dbname, user, password, host, port):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.create_table()


    def create_table(self):
        conn = psycopg2.connect(dbname = self.dbname , user=self.user, password=self.password, host=self.host, port=self.port)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS quickplay_times (player_id integer, name text, time text);")
        c.execute("CREATE TABLE IF NOT EXISTS competitive_times (player_id integer, name text, time text);")
        c.execute("CREATE TABLE IF NOT EXISTS quickplay_stats (player_id integer, datatype text, data text, column_header text);")
        c.execute("CREATE TABLE IF NOT EXISTS players (player_id SERIAL PRIMARY KEY, name text, author text);")
        c.execute("CREATE TABLE IF NOT EXISTS ranks (player_id integer, role text, rank text);")
        conn.commit()
        c.close()
        conn.close()

    def parse_data(self, name, json, author = ""):
        conn = psycopg2.connect(dbname = self.dbname , user=self.user, password=self.password, host=self.host, port=self.port)
        c = conn.cursor()
        c.execute("INSERT INTO players (name, author) VALUES (%s, %s);", (name, author))
        c.execute("SELECT player_id FROM players WHERE players.name = %s;", (name,))
        player_id = c.fetchall()[0][0]
        quickplay_stats = json["All Heroes Quickplay"]
        for k, v in quickplay_stats.items():
            column_header = k
            for a, b in v.items():
                c.execute("INSERT INTO quickplay_stats (player_id, datatype, data, column_header) VALUES (%s, %s, %s, %s);", (player_id, a, b, column_header))

        competitive_times = json["Competitive Times"]
        for k, v in competitive_times.items():
            c.execute("INSERT INTO competitive_times (player_id, name, time) VALUES (%s,%s,%s);", (player_id, k, v))


        quickplay_times = json["Quickplay Times Played"]
        for k, v in quickplay_times.items():
            c.execute("INSERT INTO quickplay_times (player_id, name, time) VALUES (%s,%s,%s);", (player_id, k, v))

        try:
            ranks = json["Ranks"]
            for k, v in ranks.items():
                c.execute("INSERT INTO ranks (player_id, role, rank) VALUES (%s, %s, %s);", (player_id, k, v))
        except:
            pass
        conn.commit()
        c.close()
        conn.close()

