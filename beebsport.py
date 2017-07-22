#!/usr/bin/env python
########################################################################################################################
# Author: John Murtagh
# Project: footy_results
# Description: This script will gather data from the sky sports website. It will print out the specified information in
# the shell
#
########################################################################################################################
import urllib2
from bs4 import BeautifulSoup
import argparse
from tabulate import tabulate
import re

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

parser.add_argument('-s', action='store', dest='season',
                    help='Get results for a specified season')

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
        print("Getting table for league {}".format(results.show_table))
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
    url = 'http://www.skysports.com/{}-fixtures'.format(results.team)
    soup = getResponse(url)
    table = soup.find('div', {'class': 'fixres__body'})
    allFixtures = table.find_all('div', {'class': 'fixres__item'})
    objs = []
    allDates = getAllFixtureDates(table)
    allComps = getAllComps(table)

    for f, date, comp in zip(allFixtures, allDates, allComps):
        time = getMatchTime(f)
        home = getHomeTeam(f)
        away = getAwayTeam(f)
        objs.append(fixture(homeTeam=home, awayTeam=away, date=date, time=time, comp=comp))
    return objs


def getHomeTeam(data):
    """
    @param data:
    @return: (str) Return home team
    """
    d = data.find('span', {'class': 'matches__item-col matches__participant matches__participant--side1'})
    home = d.find('span', {'class': 'swap-text__target'}).getText().strip()
    return home


def getAwayTeam(data):
    """
    :param data:
    :return:
    """
    d = data.find('span', {'class': 'matches__item-col matches__participant matches__participant--side2'})
    home = d.find('span', {'class': 'swap-text__target'}).getText().strip()
    return home


def getMatchTime(data):
    """
    @Summary: get status data
    :param data:
    :return:
    """
    d = data.find('span', {'class': 'matches__item-col matches__status'})
    date = d.find('span', {'class': 'matches__date'}).getText().strip()
    return date


def getScores(data):
    """
    @Summary: get team scores
    :param data:
    :return:
    """
    d = data.find('span', {'class': 'matches__teamscores'})
    scores = d.find_all('span', {'class': 'matches__teamscores-side'})
    home = scores[0].getText().strip()
    away = scores[1].getText().strip()
    return home, away


def getAllFixtureDates(data):
    """
    @Summary this function will return a list of all fixture dates

    Fixture dates are displayed as header1
    :return: (list)
    """
    return [d.getText() for d in data.find_all('h4', {'class': 'fixres__header2'})]


def getAllComps(data):
    """
    @Summary: Get all the competitions that will be played
    :return:
    """
    return [d.getText() for d in data.find_all('h5', {'class': 'fixres__header3'})]


def getResults():
    """
    @Summary: Get all fixtures for a specific team.
    :return:
    """
    if results.season:
        url = 'http://www.skysports.com/{}-results/{}'.format(results.team, results.season)
    else:
        url = 'http://www.skysports.com/{}-results/'.format(results.team)
    soup = getResponse(url)
    table = soup.find('div', {'class': 'fixres__body'})
    allFixtures = table.find_all('div', {'class': 'fixres__item'})
    objs = []
    allDates = getAllFixtureDates(table)
    allComps = getAllComps(table)

    for f, date, comp in zip(allFixtures, allDates, allComps):
        time = getMatchTime(f)
        home = getHomeTeam(f)
        away = getAwayTeam(f)
        homeScore, awayScore = getScores(f)
        objs.append(result(homeTeam=home, awayTeam=away, date=date, time=time, result="{}-{}".format(homeScore, awayScore), comp=comp))
    return objs


def getTable(league, season=results.season):
    """
    @Summary: Get the table for a specified league
    @param league: 
    @return: (str) League
    """
    if season:
        url = "http://www.skysports.com/{0}-table/{1}".format(league, season)
    else:
        url = "http://www.skysports.com/{}-table".format(league)
    soup = getResponse(url)
    team_list = []
    table = soup.find('table', {'class': 'standing-table__table'})
    rows = table.find_all('tr', {'class': 'standing-table__row'})
    for row in rows[1::]:
        attributes = row.find_all(class_=re.compile('^standing-table__cell$'))
        stats = {}
        stats["position"] = attributes[0].getText().strip()
        stats["team"] = attributes[1].getText().strip()
        stats["played"] = attributes[2].getText().strip()
        stats["won"] = attributes[3].getText().strip()
        stats["drawn"] = attributes[4].getText().strip()
        stats["lost"] = attributes[5].getText().strip()
        stats["for"] = attributes[6].getText().strip()
        stats["against"] = attributes[7].getText().strip()
        stats["goal-difference"] = attributes[8].getText().strip()
        stats["points"] = attributes[9].getText().strip()
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
