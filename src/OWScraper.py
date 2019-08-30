from bs4 import BeautifulSoup
import requests
import json
import re

#scrape player data for each player and return a hash of a players information
def scraper(owName):

        headers = {'User-Agent':'Mozilla/5.0'}
        response = requests.get("https://playoverwatch.com/en-us/career/pc/{0}".format(owName), headers = headers)
        page_content = BeautifulSoup(response.text, "html.parser")


        times = re.compile('.*:.*:.*|.*:.*|.. MIN')
        all_stats = {}

        #gather all a players statistics from their quickplay games
        def quickplay_stats():
            heroes = ["Widowmaker", "Roadhog", "Wrecking Ball", "Moira", "Junkrat", "Hanzo", "McCree", "Pharah", "Mercy",
                      "D.Va", "Reaper", "Bastion", "Winston", "Brigitte", "Lúcio", "Ana", "Tracer", "Symmetra", "Zenyatta",
                    "Reinhardt", "Orisa", "Doomfist", "Mei", "Torbjörn", "Ashe", "Zarya", "Genji", "Baptiste", "Sombra", "Sigma"]
            quickplay_dict = {}
            quickplay_content = page_content.findAll("div", attrs = {"id": ["quickplay"]})
            divs = []
            for i in quickplay_content:
                divs.append(i.findAll("div", attrs = {"class": ["ProgressBar-description", "ProgressBar-title"]}))
            quickplay_times_played = {}  
            yeet = divs[0]
            
            for i in yeet:
                if not re.match(times,i.text) and i.text not in heroes:
                    break
                if re.match(times,i.text):
                    quickplay_dict[before] = i.text
                else:
                    before = i.text
                    heroes.remove(before)
            if len(heroes) > 0:
                for i in heroes:
                    quickplay_dict[i] = "0 MINS"
            all_stats["Quickplay Times Played"] = quickplay_dict

        #gather a players competitive stats
        def comp_stats():
            comp_stats = page_content.findAll("div", attrs = {"id": ["competitive"]})
            yeet = []
            comp_dict = {}
            for i in comp_stats:
                yeet.append(i.findAll("div", attrs = {"class": ["ProgressBar-description", "ProgressBar-title"]}))

            yeet = yeet[0]
            
            for i in yeet:
                if re.match(times,i.text):
                    comp_dict[before.text] = i.text
                else:
                    before = i
            all_stats["Competitive Times"] = comp_dict


        #gather overall quickplay stats for a player
        def all_heroes_table():
            tables = page_content.findAll("table", attrs = {"class": ["DataTable"]})
            all_heroes_dict = {}
            for i in range(7):
                header = tables[i].find("h5").text
                stats = {}
                table_content = tables[i].findAll("td", attrs = {"class": "DataTable-tableColumn"})
                count = 1
                for i in table_content:
                    if count % 2 == 1:
                        key = i.text
                    else:
                        value = i.text
                        stats[key] = value
                    count+= 1
                all_heroes_dict[header] = stats
            all_stats["All Heroes Quickplay"] = all_heroes_dict


        #scrape a players competitive ranks (altered for role queue)
        def get_ranks():
            ranks_dict = {}
            ranks_containers = page_content.find("div", attrs = {"class": "competitive-rank"})
            if ranks_containers is not None:
                for container in ranks_containers:
                    ranks_dict[(container.find("div", attrs ={"class": "competitive-rank-tier"})['data-ow-tooltip-text'])] = container.find("div", attrs = {"class": "competitive-rank-level"}).text
                all_stats["Ranks"] = ranks_dict

        def get_stuff():
            all_heroes_table()
            comp_stats()
            quickplay_stats()
            get_ranks()

        get_stuff()
        return all_stats