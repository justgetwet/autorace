import tkinter as tk
import pandas as pd
import json
import datetime

class TkDf(tk.Tk):

  def __init__(self, dfs: list):
    super().__init__()
    self.title("Display DataFrame")

    self.col_line = 0
    for df in dfs:
      if type(df.columns) == pd.core.indexes.base.Index:
        for c in range(len(df.columns)):
          e = tk.Entry(self)
          e.insert(0, df.columns[c])
          e.grid(row=self.col_line, column=c)
        self.col_line += 1


      for r in range(len(df)):
        for c in range(len(df.columns)):
          e = tk.Entry(self)
          e.insert(0, df.iloc[r,c])
          e.grid(row=r+self.col_line,column=c)
      self.col_line += len(df)

if __name__=='__main__':

  pass