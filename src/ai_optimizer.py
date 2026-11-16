import pandas as pd
import numpy as np

#データ取得
def data_read(csv_path:str):
    data = pd.read_csv(csv_path)
    return data

def data_split(data):
    train_data = data[:80]
    test_data = data[80:]
    return train_data , test_data








def serogate():
    data_all = data_read()
    train_data , test_data = data_split(data_all)
    