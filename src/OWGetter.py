import psycopg2
import OWparser
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

class OWGetter:

    def __init__(self, dbname, dbuser, dbpass):
        self.dbname = dbname
        self.dbpass = dbpass
        self.dbuser = dbuser

    def player_exists(self, name, username = None):
        conn = psycopg2.connect(dbname=self.dbname, user=self.dbuser, password = self.dbpass)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        c = conn.cursor()
        if not username:
            c.execute("SELECT player_id FROM players WHERE players.name = %s;", (name,))
            player_id = c.fetchall()
        else:
            print(username)
            c.execute("SELECT player_id FROM players WHERE players.author = %s;", (username,))
            player_id = c.fetchall()
        print(player_id)
        if len(player_id) > 0:
            return player_id
        else:
            return False
        conn.close()

    def get_all_players(self):
        conn = psycopg2.connect(dbname=self.dbname, user=self.dbuser, password = self.dbpass)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        c = conn.cursor()
        c.execute("SELECT name, author FROM players;")
        players = c.fetchall()
        c.close()
        conn.close()
        return players


    def get_player_by_discord_name(self, discord_name):
        conn = psycopg2.connect(dbname=self.dbname, user=self.dbuser, password = self.dbpass)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        c = conn.cursor()
        name = c.execute("SELECT name FROM players WHERE players.author = %s;", (discord_name)).fetchall()
        if len(name) > 0:
            return name[0][0]
        else:
            return "User not in my database."

    def determine_rank(self, rank):
        rank = int(rank)
        if rank <= 1499:
            return "Bronze"
        elif rank <= 1999:
            return "Silver"
        elif rank <= 2499:
            return "Gold"
        elif rank <= 2999:
            return "Platinum"
        elif rank <= 3499:
            return "Diamond"
        elif rank <= 3999:
            return "Master"
        elif rank >= 4000:
            return "Grandmaster"
        else:
            return "Woah theres a problem"

    def get_battle_tag(self, discord_name):
        conn = psycopg2.connect(dbname=self.dbname, user=self.dbuser, password = self.dbpass)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        c = conn.cursor()
        c.execute("SELECT name FROM players WHERE players.author = %s;", (discord_name,))
        battle_tag = c.fetchall()
        conn.close()
        if len(battle_tag) > 0:
            return battle_tag[0][0]
        else:
            return "Your battle tag is not linked to your discord, or you have not added your account to my database."

    def get_quickplay_times(self, name):
        conn = psycopg2.connect(dbname=self.dbname, user=self.dbuser, password = self.dbpass)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        c = conn.cursor()
        c.execute("SELECT player_id FROM players WHERE players.name = %s;", (name,))
        player_id = c.fetchall()
        if self.player_exists(name):
            c.execute("SELECT name, time FROM quickplay_times WHERE quickplay_times.player_id = %s;", (player_id[0][0],))
            quickplay_times = c.fetchall()
            response = ">>> Quickplay Character Times for " + name + "\n-------------\n".format(name)
            for i in quickplay_times:
                response = response + i[0] + " : " + i[1] + "\n"
            return response
        else:
            return "User not found."
        conn.close()

    def get_competitive_times(self, name):
        conn = psycopg2.connect(dbname=self.dbname, user=self.dbuser, password = self.dbpass)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        c = conn.cursor()
        c.execute("SELECT player_id FROM players WHERE players.name = %s;", (name,))
        player_id = c.fetchall()
        if self.player_exists(name):
            c.execute("SELECT name, time FROM competitive_times WHERE competitive_times.player_id = %s;", (player_id[0][0],))
            competitive_times = c.fetchall()
            response = ">>> Competitive Character Times for " + name + "\n-------------\n".format(name)
            for i in competitive_times:
                response = response + i[0] + " : " + i[1] + "\n"
            return response
        else:
            return "User not found."
        self.conn.close()

    def get_quickplay_stats(self, name):
        conn = psycopg2.connect(dbname=self.dbname, user=self.dbuser, password = self.dbpass)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        c = conn.cursor()
        c.execute("SELECT player_id FROM players WHERE players.name = %s;", (name,))
        player_id = c.fetchall()
        if self.player_exists(name):
            c.execute("SELECT datatype, data, column_header FROM quickplay_stats WHERE quickplay_stats.player_id = %s;", (player_id[0][0],))
            stats = c.fetchall()
            current_header = ""
            response = ">>> Stats for " + name
            for i in stats:
                if current_header != i[2]:
                    current_header = i[2]
                    response = response + "\n\n"
                    response = response +  current_header + "\n\n"
                    response = response + i[0] + " : " +  i[1] + "\n"
                elif i[0] == "":
                    response = response + "\n\n"
                    response = response +  i[1] + "\n\n"
                else:
                    response = response + i[0] + " : " + i[1] + "\n"
            return response
        else:
            return "User not found."
        self.conn.close()

    def get_ranks(self, name, username = None):
        conn = psycopg2.connect(dbname=self.dbname, user=self.dbuser, password = self.dbpass)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        c = conn.cursor()
        if not username:
            player_id = self.player_exists(name)
        else:
            player_id = self.player_exists(None, username)
        if player_id:
            c.execute("SELECT role, rank FROM ranks WHERE ranks.player_id = %s;", (player_id[0][0],))
            given_name = name or username
            response = ""
            for i in c.fetchall():
                response = response + i[0] + " : " + i[1] + " " + self.determine_rank(i[1]) + "\n"
            if len(response) == 0:
                return ">>> {} is not yet ranked.".format(given_name)
            else:
                response = ">>> Ranks for {}\n\n".format(given_name) + response
                return response
        else:
            return "Player not found."

