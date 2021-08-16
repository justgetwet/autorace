# -*- coding: utf-8 -*-
import urllib.request
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import re
# import json
import pathlib
import datetime
from tkdf import TkDf

class Scrape:

  def get_soup(self, url: str):
    try: 
      html = urllib.request.urlopen(url)
    except urllib.error.URLError as e:
      print("URLError", e.reason)
      html = "<html></html>"

    soup = BeautifulSoup(html, "lxml")

    return soup

  def get_dfs(self, soup):
    dfs = [pd.DataFrame()]
    if soup.find("table") == None:
      print("get_dfs: a table is not found.")
    else:
      dfs = pd.io.html.read_html(soup.prettify())

    return dfs

  def is_num(self, str_num: str) -> bool:
    try:
      float(str_num)
    except ValueError:
      return False
    else:
      return True

class RaceUrls:

  url_oddspark = "https://www.oddspark.com/autorace"
  
  url_racelist = url_oddspark + "/RaceList.do?"
  url_odds = url_oddspark + "/Odds.do?"
  url_pred = url_oddspark + "/yosou"
  url_result = url_oddspark + "/RaceResult.do?"
  url_kaisai = url_oddspark + "/KaisaiRaceList.do"

  url_oneday = url_oddspark + "/OneDayRaceList.do?"

  url_search = "https://www.oddspark.com/autorace/SearchPlayerResult.do?playerNm="
  search_opt = "&toAge=&totalVic=&retirementDv=0"

  placeCd_d = {'川口': '02', '伊勢崎': '03', '浜松': '04', '飯塚': '05', '山陽': '06'}
  placeEn_d = {'川口': 'kawaguchi', '伊勢崎': 'isesaki', '浜松': 'hamamatsu',\
              '飯塚': 'iiduka', '山陽': 'sanyo'}

class Race(Scrape, RaceUrls):

  def tuple_string_for_copy(self, s):
    # ("20210606", "飯塚") を作成
    tuple_string = ""
    if s[:2] == "20":
      kdate = s.split("(")[0]
      place = s.split()[1]
      date = datetime.datetime.strptime(kdate, "%Y年%m月%d日")
      sdate = str(date.year) + str(date.month).rjust(2, "0") + str(date.day).rjust(2, "0")
      tuple_string = "(" + "'" + sdate + "','" + place + "'" + ")"
    return tuple_string


  def kaisaiRaces(self):
    soup = self.get_soup(self.url_kaisai)
    atags = soup.find("table").find_all("a")
    links = [a.get("href") for a in atags if a.get("href") != None]
    links.sort()
    pre_link = ""
    new_links = []
    for link in links:
      if pre_link != link:
          new_links.append(link)
      pre_link = link
    days = [link[9:] for link in new_links if link[10:16] == "OneDay"]
    races = []
    for day in days:
      url = self.url_oddspark + day
      soup = self.get_soup(url)
      # 年月日 + レース場
      kaisai_day = soup.find("title").text.split("｜")[0]
      # 1Rの発走時間
      time = "??:??"
      start_time = soup.find("span", class_="start-time")
      if start_time:
          time = soup.find("span", class_="start-time").text.replace("発走時間\xa0", "")
      # ("20210606", "飯塚")
      tps4cp = self.tuple_string_for_copy(kaisai_day)
      # 今日のraceに * 
      date_str = re.sub("=|&", " ", day).split()[1]
      today_str = datetime.datetime.now().strftime("%Y%m%d")
      tomorrow_str = self.tomorrow()
      mark = ""
      if date_str == today_str:
        mark = " *"
      if date_str == tomorrow_str:
        mark = " $"
      kaisai = kaisai_day + " " + time + " " + tps4cp + mark
      races.append(kaisai)
    
    return races
          
  def p_kaisai(self):
    races = self.kaisaiRaces()
    for race in races:
      # if race[-1:] == "*":
      print(race)

  def kaisai_today(self):
    races = self.kaisaiRaces()
    lst = [r for r in races if r[-1] == "*"]
    if not lst:
      lst = [r for r in races if r[-1] == "$"]
    return lst

  def tomorrow(self):
    dt_now = datetime.datetime.now()
    oneday = datetime.timedelta(days=1)
    if dt_now.hour > 12: dt_now += oneday
    yyyymmdd = dt_now.strftime('%Y%m%d')
    
    return yyyymmdd

  def entries(self, tpl_race=None):
    if tpl_race:
      yyyymmdd = tpl_race[0]
      place = tpl_race[1]
    else:
      races = self.kaisai_today()
      race = races[0]
      date_str = race.split()[0][:-3]
      place = race.split()[1]
      date_dt = datetime.datetime.strptime(date_str, "%Y年%m月%d日")
      yyyymmdd = date_dt.strftime("%Y%m%d")
    pcd = self.placeCd_d[place]
    url = self.url_oneday + f"raceDy={yyyymmdd}&placeCd={pcd}"
    soup = self.get_soup(url)
    held = soup.title.string.split("｜")[0]
    r_names = soup.select("[class='w380px bl-left'] a") # 1R 一般戦B 3100m
    s_times = soup.select("[class='w380px bl-left'] [class='start-time'] strong")
    titles = [re.sub("\xa0", " ", r.text) + " " + t.text for r, t in zip(r_names, s_times)]
    dfs = self.get_dfs(soup)
    
    return held, titles, dfs

if __name__ == '__main__':

  r = Race()
  r.p_kaisai()
  print(r.kaisai_today())
  race = ("20210814", "伊勢崎")
  # held, titles, dfs = r.entries(race)
  # print(held)
  # print(titles[0])
  # print(dfs[0])
