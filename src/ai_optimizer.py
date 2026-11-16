import pandas as pd
import numpy as np
import glob
import os

#データ取得
def data_read(csv_path:str):
    data = pd.read_csv(csv_path)
    return data

def data_split(data):
    train_data = data[:80]
    test_data = data[80:]
    return train_data , test_data

def read_dir(path='data/*'):
    csv_dir = glob.glob(path)
    dirs = [x for x in csv_dir if os.path.isdir(x)]
    return dirs

def serogate():
    data_all = data_read()
    train_data , test_data = data_split(data_all)


if __name__ == "__main__":
    print(read_dir())