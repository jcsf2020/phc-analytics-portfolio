import pandas as pd

df = pd.read_csv("fact_venda.csv")
print(df.head())
print("rows, cols =", df.shape)
