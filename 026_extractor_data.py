import json

import glob
import pandas as pd
import matplotlib.pyplot as plt

# 日本語フォント設定
from matplotlib import rc
jp_font = "Yu Gothic"
rc('font', family=jp_font)


def delete_duplicaion_index(input_list):
    temp = 0
    index = []
    for i in input_list:
        if i - 1 == temp or i + 1 == temp:
            pass
        else:
            index.append(i)
        temp = i
    return index

def plot_graph(pg_df, pg_title_text):
    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot()
    pg_df.plot(ax=ax)
    _ = ax.set_title(pg_title_text)
    _ = ax.grid(True)
    _ = ax.legend()
    plt.show()


def main():

    # パラメータの取り出し
    setting = open("setting.json", "r", encoding="utf-8")
    setting_dict = json.load(setting)

    # 結果データの読み込み
    single_file_names = glob.glob(setting_dict["file"]["path"] + setting_dict["file"]["single"])
    double_file_names = glob.glob(setting_dict["file"]["path"] + setting_dict["file"]["double"])
    all_file_names = single_file_names + double_file_names
    temp_list = []
    for i in all_file_names:
        print(i)
        temp = pd.read_csv(i, skiprows=70, encoding="cp932")
        temp_list.append(temp)

    # データフレームの結合
    df_csv = pd.concat(temp_list, ignore_index=False)
    df_csv.reset_index(drop=True, inplace=True)

    # カラム名を変更
    df_csv.columns = ["date", "sec", "data1", "data2", "data3"]

    # 生データの表示
    plot_graph(df_csv[0:1000000]["data1"],
               "読み込んだデータの一部（0～1000000）を表示")

    # 閾値用の差分作成
    # NaNは0埋め
    delta_period = setting_dict["period"]["step"]
    temp = pd.DataFrame(df_csv["data1"].diff(delta_period).fillna(0))
    temp.columns = ["delta"]
    df_delta = pd.merge(df_csv, temp, left_index=True, right_index=True)

    # 閾値の行を取得
    delta_start_triger = setting_dict["period"]["start"]
    delta_end_triger = setting_dict["period"]["end"]
    end_duplication_index = df_delta.index[df_delta["delta"] > delta_end_triger].tolist()
    start_duplication_index = df_delta.index[df_delta["delta"] < delta_start_triger].tolist()

    # 閾値が連続している行を削除
    end_index = delete_duplicaion_index(end_duplication_index)
    start_duplication_index.reverse()
    start_index = delete_duplicaion_index(start_duplication_index)
    start_index.reverse()

    # 抽出したデータを格納するデータフレームを作る
    df_extract = pd.DataFrame(list(zip(start_index, end_index)), columns=["start", "end"])
    df_extract = df_extract.assign(period=df_extract["end"] - df_extract["start"])

    # 切り出した区間の幅を表示
    plot_graph(df_extract["period"],
               "切り出した区間の長さをプロット:おかしな値が無いかここで確認する")

    # 一部の切り出した波形を表示
    fig, ax = plt.subplots(3, 3, figsize=[10, 6])
    plt.suptitle("おかしなグラフが無いか確認する")
    ax_f = ax.flatten()
    for i, (m, n) in enumerate(zip(df_extract["start"], df_extract["end"])):
        if 1000 < i < 1010:
            ax_f[i - 1001].plot(df_delta[m:n]["data1"])
            _ = ax_f[i - 1001].set_title(i)
            _ = ax_f[i - 1001].grid(True)
    plt.show()

    # 切り取りタイミングの設定
    extract_time = []
    for i in ["01", "02", "03", "04"]:
        extract_time.append(setting_dict["extract"][i])

    # 抽出データをリストに仮保存
    temp_data = [[] for i in range(4)]
    for m in df_extract["start"]:
        for i, n in enumerate(extract_time):
            temp_data[i].append(df_delta.loc[m + n]["data1"])
    
    # リストに仮保存したデータをデータフレームに
    for i, n in enumerate(["1st", "2nd", "3rd", "4th"]):
        df_extract[n] = temp_data[i]

    # 抽出データのプロット
    plot_graph(df_extract.loc[:, "1st":"4th"], "抽出したデータをプロット")

    # エクセルに結果を書き込み
    df_extract.to_excel("output.xlsx", sheet_name="result")


if __name__ == "__main__":
    main()
