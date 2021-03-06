import json
import csv

import glob
import pandas as pd
from pandas.core.series import Series
from pandas.core.frame import DataFrame
import matplotlib.pyplot as plt
from matplotlib import cm

# 日本語フォント設定
from matplotlib import rc
jp_font = "Yu Gothic"
rc('font', family=jp_font)


def delete_duplicaion_index(input_list):
    """delete consecutive numbers in the list.

    Args:
        input_list (list): A continuous number exists.

    Returns:
        list: There is no continuous number.
    """
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
    """plot pandas DataFrame on the graph(s).

    Args:
        pg_df (pandas.DataFrame or pandas.Series): Data to be graphed.
        pg_title_text (str): title
        pg_plane (bool, optional): Choose between a single graph or multiple graphs.
                                   Defaults to True.
    """
    fig = plt.figure(figsize=(10, 6))
    if pg_plane:
        if type(pg_df) == DataFrame:
            ax_1 = fig.add_subplot()
            ax_2 = ax_1.twinx()
            # 色の設定
            color_1 = cm.Set1.colors[1]
            color_2 = cm.Set1.colors[4]
            # 表示
            # 色はcm, 前後の指示はzorder, 線幅はlinewidth
            # エラーが発生した場合はグラフは1個のみ表示
            pg_df.iloc[:, 0].plot(ax=ax_1, color=color_1, zorder=-2, linewidth=2)
            pg_df.iloc[:, 1].plot(ax=ax_2, color=color_2, zorder=-1, linewidth=0.5)
            # グラフの凡例をまとめる
            handler_1, label_1 = ax_1.get_legend_handles_labels()
            handler_2, label_2 = ax_2.get_legend_handles_labels()
            _ = ax_2.legend(handler_1 + handler_2, label_1 + label_2)
            # タイトルとグリッド表示
            _ = ax_1.set_title(pg_title_text)
            _ = ax_1.grid(True)
        elif type(pg_df) == Series:
            ax = fig.add_subplot()
            pg_df.plot(ax=ax)
            _ = ax.legend()
            # タイトルとグリッド表示
            _ = ax.set_title(pg_title_text)
            _ = ax.grid(True)
        else:
            raise Exception("pandasの型式ではありません。")
        
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


class ExtractorData():
    """concatenate csv files, extract specific data and save the results to excel.
    """
    def __init__(self, json_file_path):
        """read json, set the variables, concatenate csv files and make dataframe.

        Args:
            json_file_path (str): path of the json file.
        """
        # パラメータの取り出し
        with open(json_file_path, "r", encoding="utf-8") as setting:
            self._setting_dict = json.load(setting)
        # 設定jsonから変数へ読み込み
        # ファイル名
        single_file_names = glob.glob(self._setting_dict["file"]["path"] + self._setting_dict["file"]["single"])
        double_file_names = glob.glob(self._setting_dict["file"]["path"] + self._setting_dict["file"]["double"])
        all_file_names = single_file_names + double_file_names
        # ラベル
        self._label_dict = self._setting_dict["label"]
        # 閾値
        self._period_step = self._setting_dict["period"]["step"]
        self._period_start = self._setting_dict["period"]["start"]
        self._period_end = self._setting_dict["period"]["end"]
        # 初回プロットの範囲
        self._1st_plot_range_start = self._setting_dict["1st_plot"]["start"]
        self._1st_plot_range_end = self._setting_dict["1st_plot"]["end"]
        # 抽出タイミング
        self._extract_dict = self._setting_dict["extract"]
        # 参照データの切り取りタイミング
        self._referance_1st = self._setting_dict["reference"]["1st"]
        # 結果データの読み込み
        temp_list = []
        for i in all_file_names:
            print(i)
            temp = pd.read_csv(i, skiprows=70, encoding="cp932")
            temp_list.append(temp)
        # データフレームの結合
        self._df_csv = pd.concat(temp_list, ignore_index=False)
        self._df_csv.reset_index(drop=True, inplace=True)
        # カラム名をcsvから取得して変更する
        with open(single_file_names[0], "r") as csv_file:
            csv_reader = csv.reader(csv_file)
            for i, row in enumerate(csv_reader):
                if i == 40:
                    df_csv_label = row
        self._df_csv.columns = ["date", "sec"] + df_csv_label[2:len(df_csv_label)]
        # ラベル名のリストを戻す
        self.label_index = list(self._label_dict.keys())

    def confirm_data(self, label_number, display_graph=True):
        """confirm data

        Args:
            label_number (str): the label indicating the target data.
            display_graph (bool, optional): graph display on/off. Defaults to True.
        """
        # 処理するデータを選択する
        self._process_label = self._setting_dict["label"][label_number]["00"]
        # 参考データを取り出す
        self._reference_data = list(self._setting_dict["label"][label_number].keys())[2:]
        # プロットする参照データを選択する
        self._reference_label = self._setting_dict["label"][label_number]["01"]
        # 生データの表示
        if display_graph:
            print(f"読み込んだデータの一部（{self._1st_plot_range_start}～{self._1st_plot_range_end}）を表示")
            plot_graph(self._df_csv.loc[self._1st_plot_range_start:self._1st_plot_range_end,
                                        [self._process_label, self._reference_label]],
                       f"読み込んだデータの一部（{self._1st_plot_range_start}～{self._1st_plot_range_end}）を表示")

    def generate_differences(self, display_graph=True):
        """generate differences and make dataframe of results.

        Args:
            display_graph (bool, optional): graph display on/off. Defaults to True.
        """
        # 閾値用の差分作成
        # NaNは0埋め
        self._delta_period = self._setting_dict["period"]["step"]
        temp = pd.DataFrame(self._df_csv[self._process_label].diff(self._delta_period).fillna(0))
        temp.columns = ["delta"]
        self._df_delta = pd.merge(self._df_csv, temp, left_index=True, right_index=True)
        # データの差分量を見る
        if display_graph:
            print(f"読み込んだデータの一部（{self._1st_plot_range_start}～{self._1st_plot_range_end}）を表示")
            plot_graph(self._df_delta.loc[self._1st_plot_range_start:self._1st_plot_range_end,
                                          ["delta", self._process_label]],
                       f"読み込んだデータの一部（{self._1st_plot_range_start}～{self._1st_plot_range_end}）を表示")

    def cut_out_data(self, display_graph=True):
        """cut out the data which you need.

        Args:
            display_graph (bool, optional): graph display on/off. Defaults to True.
        """
        # 閾値の行を取得
        self._delta_start_triger = self._setting_dict["period"]["start"]
        self._delta_end_triger = self._setting_dict["period"]["end"]
        self._end_duplication_index = self._df_delta.index[self._df_delta["delta"] > self._delta_end_triger].tolist()
        start_duplication_index = self._df_delta.index[self._df_delta["delta"] < self._delta_start_triger].tolist()
        # 閾値が連続している行を削除
        self._end_index = delete_duplicaion_index(self._end_duplication_index)
        start_duplication_index.reverse()
        self._start_index = delete_duplicaion_index(start_duplication_index)
        self._start_index.reverse()
        # 最初にエンドトリガーが来る場合、カットする必要がある
        if self._start_index[0] > self._end_index[0]:
            self._end_index.pop(0)
        # 抽出したデータを格納するデータフレームを作る
        self._df_extract = pd.DataFrame(list(zip(self._start_index, self._end_index)), columns=["start", "end"])
        self._df_extract = self._df_extract.assign(period=self._df_extract["end"] - self._df_extract["start"])
        # 切り出した区間の幅を表示
        if display_graph:
            print("切り出した区間の長さをプロット:おかしな値が無いかここで確認する")
            plot_graph(self._df_extract["period"],
                       "切り出した区間の長さをプロット:おかしな値が無いかここで確認する")

    def confirm_graphs(self, display_graph=True):
        """confirm graphs to see if there is some problems.

        Args:
            display_graph (bool, optional): graph display on/off. Defaults to True.
        """
        # データの一部を切り出し
        df_plot_temp = pd.DataFrame(index=[])
        for i, (m, n) in enumerate(zip(self._df_extract["start"], self._df_extract["end"])):
            if 1000 < i < 1010:
                temp = self._df_delta[m:n][self._process_label]
                temp = temp.reset_index()
                df_plot_temp[str(i)] = temp[self._process_label]
        # 一部の切り出した波形を表示
        if display_graph:
            print("おかしなグラフが無いか確認する")
            plot_graph(df_plot_temp,
                       "おかしなグラフが無いか確認する",
                       pg_plane=False)

    def output_results(self, label_number, display_graph=True):
        """confirm results to see if there is some problems.

        Args:
            label_number (str): the label indicating the target data.
            display_graph (bool, optional): graph display on/off. Defaults to True.
        """
        # 切り取りタイミングの設定
        extract_time = []
        for i in list(self._setting_dict["extract"].keys())[1:]:
            extract_time.append(self._setting_dict["extract"][i])
        # 抽出データをリストに仮保存
        temp_data = [[] for i in range(len(extract_time))]
        for m in self._df_extract["start"]:
            for i, n in enumerate(extract_time):
                temp_data[i].append(self._df_delta.loc[m + n][self._process_label])
        # リストに仮保存したデータをデータフレームに
        for i, n in enumerate(list(self._setting_dict["extract"].keys())[1:]):
            self._df_extract[n] = temp_data[i]
        # 参照データを切り取り、データフレームに追加
        temp_data = [[] for i in range(len(self._reference_data))]
        for m in self._df_extract["start"]:
            for i, n in enumerate(self._reference_data):
                temp_data[i].append(self._df_delta.loc[m + self._referance_1st][self._setting_dict["label"][label_number][n]])
        for i, n in enumerate(self._reference_data):
            self._df_extract[self._setting_dict["label"][label_number][n]] = temp_data[i]
        # 抽出データのプロット
        if display_graph:
            print("抽出したデータをプロット")
            plot_graph(self._df_extract.loc[:,
                                            list(self._setting_dict["extract"].keys())[1]:
                                            self._setting_dict["label"][label_number][self._reference_data[-1]]],
                       "抽出したデータをプロット",
                       pg_plane=False)

    def write_xlsx(self, write_mode="w"):
        """write xlsx file.

        Args:
            write_mode (str, optional): ExcelWriter's option. Defaults to "w".
        """
        # エクセルに結果を書き込み
        print(f"output.xlsxに『{self._process_label}』を書き込みました")
        with pd.ExcelWriter("output.xlsx", mode=write_mode) as writer:
            self._df_extract.to_excel(writer, sheet_name=self._process_label)


def main():
    data = ExtractorData("setting.json")
    for i, n in enumerate(data.label_index):
        data.confirm_data(n, display_graph=True)
        data.generate_differences(display_graph=True)
        data.cut_out_data(display_graph=True)
        data.confirm_graphs(display_graph=True)
        data.output_results(n, display_graph=True)
        if i == 0:
            data.write_xlsx()
        else:
            data.write_xlsx(write_mode="a")


if __name__ == "__main__":
    main()
