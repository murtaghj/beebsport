#!/usr/bin/env python
########################################################################################################################
# Author: John Murtagh
# Project: beebsport
# Description: This project is designed to scrape information from BBC Sports football section
#
#
########################################################################################################################
import urllib2
from bs4 import BeautifulSoup
import argparse
from tabulate import tabulate
import sys

# TODO: introduce ability to filter on losses/fails/draws
# TODO: Get teams with most cards
# TODO: Filter on league
# TODO: print full league table


parser = argparse.ArgumentParser()

parser.add_argument('-t', action='store', dest='team',
                    help='The team that you want to see information for.')

parser.add_argument('-l', action='store', dest='last_months', default=1,
                    help='Get match results for the last "n" months')

parser.add_argument('-r', action='store_true', dest='match_results',
                    help='Get results for specified team')

parser.add_argument('-f', action='store_true', dest='fixtures',
                    help='Get fixtures for specified team')

parser.add_argument('-T', action='store', dest='show_table',
                    help='Show specified table')

parser.add_argument('-nf', action='store_true', dest='next_fixture',
                    help='Find the next fixture for specified team')

results = parser.parse_args()


def main():
    """
    @Summary: The main function that will be executed.
    @return: 
    """
    if results.fixtures:
        print("Getting upcoming available fixtures for {}..".format(results.team))
        fixtures = getFixtures()
        printFormatFixtures(fixtures)
        print "\n"
    if results.match_results:
        print("Getting match results for {}..".format(results.team))
        res = getResults()
        printFormatResults(res)
        print "\n"

    if results.show_table:
        print("Getting table for league ".format(results.show_table))
        table = getTable(results.show_table)
        printFormatTable(table)
        print "\n"


def printFormatFixtures(fixtureList):
    """
    @Summary: Format fixtures list
    @return: Pretty table that shows the fixtures
    """
    res = []
    headers = ["Competition", "Home", "Away", "Date", "Time"]
    for fix in fixtureList:
        res.append([fix.comp, fix.homeTeam, fix.awayTeam, fix.date, fix.time])
    print tabulate(res, headers=headers)


def printFormatResults(resultList):
    """
    @Summary: Print results in table format 
    @param resultList: 
    @return: 
    """
    res = []
    headers = ["Competition", "Home", "Score", "Away", "Date", "Time"]
    for result in resultList:
        res.append([result.comp, result.homeTeam, result.result, result.awayTeam, result.date, result.time])
    print tabulate(res, headers=headers)


def printFormatTable(resultTable):
    """
    @Summary: Print results in table format 
    @param resultList: 
    @return: 
    """
    res = []
    headers = ["Position", "Team", "P", "W", "D", "L", "F", "A", "GD", "Points"]
    for result in resultTable:
        pos = "".join(x for x in result["position"] if x.isdigit())
        res.append([pos, result["team"], result["played"], result["won"], result["drawn"],
                    result["lost"], result["for"], result["against"], result["goal-difference"], result["points"]])
    print tabulate(res, headers=headers)


def getFixtures():
    """
    @Summary: Get all fixtures for a specific team.
    :return: 
    """
    url = 'http://www.bbc.co.uk/sport/football/teams/{}/fixtures'.format(results.team)
    soup = getResponse(url)
    table = soup.find('table', {'class': 'table-stats'})
    allFixtures = table.find_all('tr', {'class': 'preview'})
    objs = []
    for f in allFixtures:
        comp = f.find('td', {'class': 'match-competition'}).getText().strip()
        date = f.find('td', {'class': 'match-date'}).getText().strip()
        time = f.find('td', {'class': 'kickoff'}).getText().strip()
        home = f.find('span', {'class': 'team-home teams'}).getText().strip()
        away = f.find('span', {'class': 'team-away teams'}).getText().strip()
        objs.append(fixture(homeTeam=home, awayTeam=away, date=date, time=time, comp=comp))
    return objs


def getResults():
    """
    @Summary: Get results for a given specified team
    :return: 
    """
    url = 'http://www.bbc.co.uk/sport/football/teams/{}/results'.format(results.team)
    soup = getResponse(url)
    table = soup.find('div', {'class': 'fixtures-table team-fixtures full-table-medium'})

    all_stats_tables = table.find_all('table', {'class': 'table-stats'})
    months_available = len(all_stats_tables)
    if int(results.last_months) > months_available:
        print("You have requested result than data is available for! "
              "Selected months = {}, Available months = {}".format(str(results.last_months), str(months_available)))
        sys.exit()
    match_lst = []
    for table_stat in all_stats_tables[:int(results.last_months)]:
        report = table_stat.find_all('tr', {'class': 'report'})
        for m in report:
            comp = m.find('td', {'class': 'match-competition'}).getText().strip()
            date = m.find('td', {'class': 'match-date'}).getText().strip()
            time = m.find('td', {'class': 'time'}).getText().strip()
            home = m.find('span', {'class': 'team-home teams'}).getText().strip()
            score = m.find('span', {'class': 'score'}).getText().strip()
            away = m.find('span', {'class': 'team-away teams'}).getText().strip()
            match_lst.append(result(homeTeam=home, awayTeam=away, date=date, time=time, result=score, comp=comp))
    return match_lst


def getTable(league):
    """
    @Summary: Get the table for a specified league
    @param league: 
    @return: (str) League
    """
    url = "http://www.bbc.co.uk/sport/football/{}/table".format(league)
    soup = getResponse(url)
    team_list = []
    table = soup.find('table', {'class': 'table-stats'})
    all_teams = table.find_all('tr', {'class': 'team'})
    for t in all_teams:
        stats = {}
        stats["position"] = t.find('td', {'class': 'position'}).getText().strip()
        stats["team"] = t.find('td', {'class': 'team-name'}).getText().strip()
        stats["played"] = t.find('td', {'class': 'played'}).getText().strip()
        stats["won"] = t.find('td', {'class': 'won'}).getText().strip()
        stats["drawn"] = t.find('td', {'class': 'drawn'}).getText().strip()
        stats["lost"] = t.find('td', {'class': 'lost'}).getText().strip()
        stats["for"] = t.find('td', {'class': 'for'}).getText().strip()
        stats["against"] = t.find('td', {'class': 'against'}).getText().strip()
        stats["goal-difference"] = t.find('td', {'class': 'goal-difference'}).getText().strip()
        stats["points"] = t.find('td', {'class': 'points'}).getText().strip()
        team_list.append(stats)
    return team_list



def getResponse(url):
    """
    @Summary: Get html Response
    :return html response 
    """
    response = urllib2.urlopen(url)
    html = response.read()
    return BeautifulSoup(html, "lxml")


class fixture:
    def __init__(self, homeTeam, awayTeam, date, time, comp):
        """
        @Summary: This class defines a fixture.
        @param homeTeam: (str) A string containing the home Team Name. 
        @param awayTeam: (str) A string containing the away Team Name.
        @param date: (str) A string containing the date of the fixture.
        @param time: (str) A string containing a time.
        @parm comp (str) The comp that fixture is in
        """
        self.homeTeam = homeTeam
        self.awayTeam = awayTeam
        self.date = date
        self.time = time
        self.comp = comp


class result:
    def __init__(self, homeTeam, awayTeam, date, time, comp, result):
        """
        @Summary: This class defines a fixture.
        @param homeTeam: (str) A string containing the home Team Name. 
        @param awayTeam: (str) A string containing the away Team Name.
        @param date: (str) A string containing the date of the fixture.
        @param time: (str) A string containing a time.
        @parm comp: (str) The comp that fixture is in
        @Param result: (str) Result of match
        """
        self.homeTeam = homeTeam
        self.awayTeam = awayTeam
        self.date = date
        self.time = time
        self.comp = comp
        self.result = result


if __name__ == "__main__":
    main()
