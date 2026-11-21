import pandas as pd
import numpy as np
import glob
import os
import math
from sklearn.model_selection import train_test_split

# パターン定義
ROWS, COLS = 800, 400
shape_field = ["square","kawa","cross"]
slope_angle = ["1%","2%"]
groove_width = ["10cm","20cm"]
groove_shape = ["square","v"]

#データ取得
def data_read(csv_path:str):
    data = pd.read_csv(csv_path)
    return data

def data_split(data):
    train_data,test_data = train_test_split(data,test_size=0.2)
    return train_data , test_data

def read_dir(path='data/*'):
    csv_dir = glob.glob(path)
    dirs = [x for x in csv_dir if os.path.isdir(x)]
    return dirs

#畑の形状の状態定義
def field(length:int,count:int,gw:int):
    mask = np.zeros(length,dtype=np.int32)
    if count == 0:
        return mask
    if count > 1:
        for g in range(0,gw):
            mask[g] = 1
        for g in range(length-1,length-1-gw,-1):
            mask[g] = 1
        if count > 2:
            for i in range(1,count-1):
                cell = int(length/(count-1)*i)
                start = cell - int(math.floor(gw/2))
                end = cell + int(math.floor(gw/2))
                mask[start:end] = 1
    return mask

#サロゲート（代理）モデルの作成
def surrogate():
    data_all = []
    for path in read_dir():
        data_all = data_read(f"{path}/cell_lrt_summary.csv")
        train_data , test_data = 

    


if __name__ == "__main__":
    print(read_dir())