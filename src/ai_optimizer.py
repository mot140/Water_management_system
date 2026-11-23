import pandas as pd

pd_conect_csv = pd.read_csv("experiments.csv")  # index_col=0 は外すと exp_id も残せます
all_data = []
cat_col = ["furrow_type", "field_shape"]


# csv_path と その行の条件データ(row_data) をセットで回す
def read_csv_path(df_exp=pd_conect_csv):
    for _, row_data in df_exp.iterrows():
        read_data(row_data["csv_path"], row_data)  # 2つとも渡す！
    df = pd.concat(all_data, ignore_index=True)
    df = category(df)
    return df  # 完成したdfを返す


def read_data(csv_path, row_data):
    data_read = pd.read_csv(csv_path)
    for col in pd_conect_csv.columns:
        if col != "csv_path":
            data_read[col] = row_data[col]  # 変数名を row_data に統一！
    all_data.append(data_read)
    return data_read


def category(data, cat=cat_col):
    for c in cat:
        data[c] = data[c].astype("category")
    return data


if __name__ == "__main__":
    print(read_csv_path())