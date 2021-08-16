import pandas as pd
import re
import json
import copy
import seaborn as sns
from racers import Racers
# pd.set_option('display.max_columns', 22)
# from race import Scrape, RaceUrls
from racers import Racers

class OneRace(Racers):

  def __init__(self, date: str, place: str, race_no: int):

    self.json_path = "../../ruby/gosu/gosu_race/test_new.json"

    self.race_no = race_no
    self.p_race = f"raceDy={date}&placeCd={self.placeCd_d[place]}&raceNo={str(race_no)}"
    self.p_pred = f"/{self.placeEn_d[place]}/{date[:4]}/{date[4:]}.html"
    self.p_predai = f"/ai/OneDayRaceList.do?raceDy={date}&placeCd={self.placeCd_d[place]}&aiId=1"
    
    self.entry_soup = self.get_soup(self.url_racelist + self.p_race)
    self.result_soup = self.get_soup(self.url_result + self.p_race)
    
    self.pred_soup = ""
    self.predai_soup = ""
    self.row_size = len(self.entry_soup.find_all("td", class_="showElm racer"))
    self.odds_d = { n : ("") for n in range(1, self.row_size + 1)}
    self.pred_d = { n : ("", "", "") for n in range(1, self.row_size + 1)}
    self.predai_d = { n : ("", "", "") for n in range(1, self.row_size + 1)}
    self.sohyo = ""

    self.racetitle = self.raceTitle()
    # print(self.racetitle)


  def raceTitle(self):
    # 一般戦 2021年6月25日(金) 伊勢崎 3R 15:21
    soup = self.entry_soup
    shubetsu, race = "OddsPark AutoRace", ""
    res = soup.find("title")
    if res and res.text != "オッズパークオートレース":
        shubetsu, race = res.text.split("｜")[:2] # race: 日程 場所 レース
        shubetsu = shubetsu.strip('【レース別出走表】') # 種別
    stm = soup.select_one(".RCstm")
    stm_txt = "spam ??:??" if not stm else stm.text
    start_time = stm_txt.split()[1] # 発走時刻
    dst = soup.select_one(".RCdst")
    dst_txt = "天候：?? 走路状況：?? spam" if not dst else dst.text
    weather, surface = dst_txt.split()[:2]
    surface = "(" + surface.strip("走路状況：") + ")"
    title = " ".join([shubetsu, race, start_time, weather, surface])
    return title
      
  def entry(self):

    df = self.get_dfs(self.entry_soup)[0]
    if df.empty: 
        return df
    sr_lst = []
    for n in range(len(df)):
      sr = self.sr_racer()
      racer_l = df.values[n][:7]
      racer = [re.sub("  |\u3000", " ", r) for r in racer_l if type(r) == str]
      # print(racer)
      # -> ['城戸 徹 41歳/27期 V0/0回/V1 ヤブキ３７３/1', '飯 塚', 
      # -> '0m 3.89 0.073', 'B-43 (B-46) 53.433', '3.39 3.463 3.423', '着順：0-0-0-7 0.16 ..']
      fstname, lstname, age, v, machine = racer[0].split()
      name = fstname + " " + lstname
      lg = racer[1].replace(" ", "")
      racer2s = racer[2].split()
      if "再" in racer2s: racer2s.remove("再") 
      handicap, tryLap, tryDev = racer2s # ハンデ、試走タイム、試走偏差
      rank, prvRank, point = racer[3].split() # ランク、(前ランク)、審査ポイント
      avgTry, avgLap, fstLap = racer[4].split() # 良10走lap
      # print(tryLap)
      last10, ast = racer[5].split()[:2] # 近10走着順、平均ST
      sr["no"] = str(n + 1)
      sr["name"] = name
      sr["age"] = re.sub("/", "-", age)
      sr["lg"] = lg
      sr["rank"] = rank
      sr["prank"] = prvRank
      sr["hand"] = handicap
      sr["machine"] = re.sub("/1", "", machine)
      sr["vc"] = re.sub("/", "-", v)
      sr["point"] = float(point)
      sr["last"] = last10.strip("着順：")
      sr['ast'] = ast
      if self.is_num(tryLap):
        sr["try"] = float(tryLap)
        sr["prd"] = round(float(tryLap) + float(tryDev), 3)
      sr["avt"] = float(avgTry)
      sr["avg"] = float(avgLap)
      sr["fst"] = float(fstLap)
      sr.name = n
      sr_lst.append(sr)

    hands = [sr["hand"] for sr in sr_lst]
    # avtLaps = [sr["avt"] for sr in sr_lst] 
    avgLaps = [sr["avg"] for sr in sr_lst]
    fstLaps = [sr["fst"] for sr in sr_lst]
    prdLaps = [sr["prd"] for sr in sr_lst]
    # avtDifs = self.calc_goalDifs(avtLaps, hands)
    avgDifs = self.calc_goalDifs(avgLaps, hands)
    fstDifs = self.calc_goalDifs(fstLaps, hands)
    prdDifs = self.calc_goalDifs(prdLaps, hands)
    for sr, avgDif, fstDif, prdDif in zip(sr_lst, avgDifs, fstDifs, prdDifs):
        # sr["atm"] = avtDif
        sr["avm"] = round(avgDif, 1)
        sr["fsm"] = round(fstDif, 1)
        sr["pdm"] = round(prdDif, 1)
    
    entry_df = pd.DataFrame(sr_lst).dropna(how="all", axis=1)
    
    return entry_df

  def dspEntry(self):
    df = self.entry().dropna(how="all", axis=1)
    cm = sns.light_palette("green", as_cmap=True)
    # print(self.racetitle)
    # display(df.style.background_gradient(cmap=cm))
    print(df)

  def result(self):

    df = self.get_dfs(self.result_soup)[0]
    if df.empty: 
      return df
    s_df = df.sort_values('車')
    sr_odr, sr_fav = s_df["着"], s_df["人気"]
    odrs = [str(int(odr)) if self.is_num(odr) else odr for odr in sr_odr]
    favs = [str(int(fav)) if self.is_num(fav) else fav for fav in sr_fav]
    laps = list(s_df["競走タイム"])
    hands = list(s_df["ハンデ"])
    goalDiffs = self.calc_goalDifs(laps, hands)

    result_df = self.entry()
    for n in range(len(result_df)): 
      result_df.loc[n, "run"] = laps[n]
      result_df.loc[n, "rnm"] = goalDiffs[n]
      result_df.loc[n, "odr"] = odrs[n]
      result_df.loc[n, "fav"] = favs[n]
    
    return result_df
      
  def dspResult(self):
    df = self.result()
    cm = sns.light_palette("green", as_cmap=True)
    print(self.racetitle)
    # display(df.style.background_gradient(cmap=cm).hide_index())

  def saveDf2json(self, df: pd.DataFrame):
    if df.empty:
      print("a dataframe is empty.")
      return
    j = df.to_json(force_ascii=False)
    dic = json.loads(j)
    title = self.racetitle
    dic["title"] = title
    j_with_title = json.dumps(dic, ensure_ascii=False)
    # p = "../../ruby/gosu/gosu_race/test_new.json"
    p = self.json_path
    with open(p, "w", encoding="utf-8") as f:
      f.write(j_with_title)
    print(f"saved dataframe: '{title}' to json")

  def savEntry(self):
    df = self.entry()
    self.saveDf2json(df)

  def savResult(self):
    df = self.result()
    self.saveDf2json(df)

  def reqPrediction(self):
    url = self.url_pred + self.p_pred
    soup = self.get_soup(url)
    lst = soup.find_all("p", class_="sohyo")
    sohyo = "総評:" + lst[self.race_no - 1].find("strong").text.strip("（総評）")
    dfs = self.get_dfs(soup)
    _df = dfs[self.race_no - 1].dropna(thresh=9)
    pred_df = _df.fillna("")
    lst = []
    for e in pred_df.itertuples():
      lst.append([e.晴, e.スタート, e.コメント])
        
    return pd.DataFrame(lst, columns=["晴", "ST", "Commnet"]) #, sohyo

if __name__=='__main__':

  race = OneRace('20210815','伊勢崎', 10)
  print(race.racetitle)
  # df = race.entry()
  df = race.reqPrediction()
  print(df)
  # race.savResult()
  # print(df)
    
  # sr = race.srPayout()
  # print(sr)
  # race.bet([1, 2, 3])
  # race.balance()
  