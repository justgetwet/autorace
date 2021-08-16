import tkinter as tk
from tkinter import ttk
import pandas as pd
import unicodedata
# import seaborn as sns
from onerace import OneRace

class TkRace:
  
  def __init__(self, title: str, df: pd.DataFrame):
    self.root = tk.Toplevel()
    self.root.title("tk sample")
    self.df = df
    sizes = self.column_sizes()
    w = sum(map(lambda x: x+8, sizes)) + 60
    h = 500
    self.root.geometry(f"{w}x{h}+200+50")
    self.title = title
    self.frame = tk.Frame(self.root)

  def set_toolbar_frame(self):
    f_toolbar = tk.Frame(self.frame, bg="whitesmoke", height=50, pady=10, padx=10)
    f_toolbar.pack(fill=tk.X)
    
    l_title = tk.Label(f_toolbar, text=self.title, bg="whitesmoke", anchor="w")
    l_title.pack(side=tk.LEFT, expand=True, anchor=tk.W)

    b_quit = ttk.Button(f_toolbar, text='Quit', command=lambda: self.root.quit())
    b_quit.pack(side=tk.LEFT, expand=True, anchor=tk.E)


  def set_table_on_frame(self):
    f_table = tk.Frame(self.frame, height=450, pady=10, padx=10)
    
    headingcolor = "lightgrey"
    alternatecolor = "whitesmoke"

    tree = ttk.Treeview(f_table, height=len(self.df)+1)

    def fixed_map(option):
      # Fix for setting text colour for Tkinter 8.6.9
      # From: https://core.tcl.tk/tk/info/509cafafae
      #
      # From: https://ja.stackoverflow.com/questions/64095/
      # Python ttk.Treeview python3.7でリストに割り当てたtagに対して色を設定する方法
      return [elm for elm in style.map('Treeview', query_opt=option) if elm[:2] != ('!disabled', '!selected')]	
    
    style = ttk.Style()
    style.theme_use("default")
    style.configure("Treeview.Heading", background=headingcolor)
    style.map('Treeview', foreground=fixed_map('foreground'), background=fixed_map('background'))
    
    tree["show"] = "headings"
    cols = tuple(range(1, len(self.df.columns)+1))
    tree['columns'] = cols

    sizes = self.column_sizes()
    for i, col, size in zip(cols, self.df.columns, sizes):
      tree.heading(i, text=f"{col}")
      tree.column(i, width=size+8) # 
    
    tpls = [tuple(t)[1:] for t in self.df.itertuples()]
    for i, tpl in enumerate(tpls):
      tree.insert("", "end", tags=i, values=tpl)
      if i & 1:
        tree.tag_configure(i, background=alternatecolor)
    
    tree.pack(pady=10, padx=10)
    f_table.pack(fill=tk.BOTH)

  def column_sizes(self) -> list:

    def east_asian_width_count(text):
      count = 0
      for c in text:
        if unicodedata.east_asian_width(c) in 'FWA':
          count += 2
        else:
          count += 1
      return count * 8
    
    lst_columns = [[col] + list(self.df[col]) for col in self.df.columns]
    sizes = []
    for cols in lst_columns:
      max_size = max([east_asian_width_count(str(col)) for col in cols])
      sizes.append(max_size)

    return sizes

  def run(self):
    self.set_toolbar_frame()
    self.set_table_on_frame()
    self.frame.pack()
    self.root.mainloop()

if __name__ == '__main__':
  
  race = OneRace('20210701','浜松', 3)
  title = race.racetitle
  df = race.entry()
  t = TkRace(title, df)
  t.run()