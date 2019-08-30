import sys
sys.path.append('./lib')
import OWparser
import OWGetter
import psycopg2
from OWScraper import scraper
from time import sleep
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

class OWUpdater:

    def __init__(self, parser, getter):
        self.getter = getter
        self.parser = parser

    def update_all(self):
        players = self.getter.get_all_players()
        for player in players:
            if len(player) ==  2:
                self.remove_user(player[0].strip(), player[1])
                sleep(2)
                self.bind_author_to_user(player[0].strip(), player[1])
            elif len(player) == 1:
                self.remove_user(player[0].strip())
                sleep(2)
                self.add_user(player[0].strip())
            sleep(2)



    def remove_user(self, name, username = None):
        conn = psycopg2.connect(dbname="data", user="postgres", password = "patrickstar")
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        c = conn.cursor()
        if username == None:
            c.execute("SELECT player_id FROM players WHERE players.name = %s;", (name,))
        else:
            c.execute("SELECT player_id FROM players WHERE players.author = %s;", (username,))
        player_id = c.fetchall()
        try:
            c.execute("DELETE FROM quickplay_times WHERE quickplay_times.player_id = %s;", (player_id[0][0],))
            c.execute("DELETE FROM players WHERE players.player_id = %s;", (player_id[0][0],))
            c.execute("DELETE FROM competitive_times WHERE competitive_times.player_id = %s;", (player_id[0][0],))
            c.execute("DELETE FROM quickplay_stats WHERE quickplay_stats.player_id = %s;", (player_id[0][0],))
            c.execute("DELETE FROM ranks WHERE ranks.player_id = %s;", (player_id[0][0],))
            conn.commit()
            if not username:
                return(name + " has been deleted.")
            else:
                return(username + " has been deleted.")
        except:
            if not username: 
                return(name + " not found in database.")
            else:
                return("Your stats are either not in the database, or not linked to your discord name.")
        conn.close()

    def add_user(self, name):
        conn = psycopg2.connect(dbname="data", user="postgres", password = "patrickstar")
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        c = conn.cursor()
        c.execute("SELECT player_id FROM players WHERE players.name = %s;", (name,))
        player_id = c.fetchall()
        if len(player_id) == 0:
            json = scraper(name)
            self.parser.parse_data(name, json)
            conn.commit()
        else:
            return "This player exists in my database"
        conn.close()

    def bind_author_to_user(self, name, author):
        conn = psycopg2.connect(dbname="data", user="postgres", password = "patrickstar")
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        c = conn.cursor()
        c.execute("SELECT author FROM players WHERE players.name = %s;", (name,))
        player_id = c.fetchall()
        if len(player_id) == 0:
            json = scraper(name)
            self.parser.parse_data(name, json, author)
            conn.commit()
        else:
            return "This player exists in my database"
        conn.close()