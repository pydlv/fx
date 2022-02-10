import pandas
from pandas import DataFrame


def load_data(filename: str) -> DataFrame:
    df = pandas.read_csv(filename)
    df = df[["Date", "Close"]]
    df.columns = ["ds", "y"]

    return df[df["y"].notnull()]
