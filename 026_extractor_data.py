import json
import csv

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


def plot_graph(pg_df, pg_title_text, pg_plane=True):
    fig = plt.figure(figsize=(10, 6))
    if pg_plane:
        ax = fig.add_subplot()
        pg_df.plot(ax=ax)
        _ = ax.set_title(pg_title_text)
        _ = ax.grid(True)
        _ = ax.legend()
    else:
        ax = fig.subplots(3, 3)
        plt.suptitle(pg_title_text)
        ax_f = ax.flatten()
        for i, m in enumerate(pg_df):
            ax_f[i].plot(pg_df[m])
            _ = ax_f[i].set_title(m)
            _ = ax_f[i].grid(True)
        # グラフの重なりをなくす為に必要
        plt.tight_layout()
    plt.show()


def main():

    # パラメータの取り出し
    with open("setting.json", "r", encoding="utf-8") as setting:
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

    # カラム名をcsvから取得して変更する
    with open(single_file_names[0], "r") as csv_file:
        csv_reader = csv.reader(csv_file)
        for i, row in enumerate(csv_reader):
            if i == 40:
                df_csv_label = row
    df_csv.columns = ["date", "sec"] + df_csv_label[2:len(df_csv_label)]

    # 処理するデータを選択する
    process_label = setting_dict["label"]["01"]["00"]

    # 参考データを取り出す
    reference_data = list(setting_dict["label"]["01"].keys())[2:]
    
    # 生データの表示
    print("読み込んだデータの一部（0～200000）を表示")
    plot_graph(df_csv[0:200000][process_label],
               "読み込んだデータの一部（0～200000）を表示")

    # 閾値用の差分作成
    # NaNは0埋め
    delta_period = setting_dict["period"]["step"]
    temp = pd.DataFrame(df_csv[process_label].diff(delta_period).fillna(0))
    temp.columns = ["delta"]
    df_delta = pd.merge(df_csv, temp, left_index=True, right_index=True)

    # データの差分量を見る
    print("データの差分量（0～200000）を表示")
    plot_graph(df_delta[0000:200000]["delta"],
               "データの差分量（0～200000）を表示")

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
    print("切り出した区間の長さをプロット:おかしな値が無いかここで確認する")
    plot_graph(df_extract["period"],
               "切り出した区間の長さをプロット:おかしな値が無いかここで確認する")

    # 一部の切り出した波形を表示
    df_plot_temp = pd.DataFrame(index=[])
    for i, (m, n) in enumerate(zip(df_extract["start"], df_extract["end"])):
        if 1000 < i < 1010:
            temp = df_delta[m:n][process_label]
            temp = temp.reset_index()
            df_plot_temp[str(i)] = temp[process_label]
    print("おかしなグラフが無いか確認する")
    plot_graph(df_plot_temp,
               "おかしなグラフが無いか確認する",
               pg_plane=False)

    # 切り取りタイミングの設定
    extract_time = []
    for i in ["01", "02", "03", "04"]:
        extract_time.append(setting_dict["extract"][i])

    # 抽出データをリストに仮保存
    temp_data = [[] for i in range(4)]
    for m in df_extract["start"]:
        for i, n in enumerate(extract_time):
            temp_data[i].append(df_delta.loc[m + n][process_label])
    
    # リストに仮保存したデータをデータフレームに
    for i, n in enumerate(["1st", "2nd", "3rd", "4th"]):
        df_extract[n] = temp_data[i]

    # 参照データを切り取り、データフレームに追加
    temp_data = [[] for i in range(len(reference_data))]
    for m in df_extract["start"]:
        for i, n in enumerate(reference_data):
            temp_data[i].append(df_delta.loc[m][setting_dict["label"]["01"][n]])
    for i, n in enumerate(reference_data):
        df_extract[setting_dict["label"]["01"][n]] = temp_data[i]

    # 抽出データのプロット
    print("抽出したデータをプロット")
    plot_graph(df_extract.loc[:, "1st":setting_dict["label"]["01"][reference_data[-1]]],
               "抽出したデータをプロット",
               pg_plane=False)

    # エクセルに結果を書き込み
    print("output.xlsxに書き込みました")
    df_extract.to_excel("output.xlsx", sheet_name=process_label)


if __name__ == "__main__":
    main()
