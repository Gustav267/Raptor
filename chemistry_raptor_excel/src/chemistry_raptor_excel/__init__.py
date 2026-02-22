import pandas as pd
import matplotlib.pyplot as plt
from chemistry_raptor import create_plot
import xlwings as xw

@xw.func
def excel_plot(vol_naoh: pd.Series, ph_werte: pd.Series) -> str:
  fig = plt.figure()
  subplots = fig.subplots()
  create_plot(vol_naoh, ph_werte, subplots)

  sheet = xw.Book().sheets[0]
  sheet.pictures.add(fig, name='Titrationskurve', update=True)
  return "Plot erfolgreich erstellt!"

