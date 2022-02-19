import glob
import pandas as pd
import matplotlib.pyplot as plt

# 日本語フォント設定
from matplotlib import rc
jp_font = "Yu Gothic"
rc('font', family=jp_font)

single_file_names = glob.glob("data/auto$0$?.csv")
double_file_names = glob.glob("data/auto$0$??.csv")


all_file_names = single_file_names + double_file_names
temp_list = []
for i in all_file_names:
    print(i)
    temp = pd.read_csv(i, skiprows=70, encoding="cp932")
    temp_list.append(temp)
df_csv = pd.concat(temp_list, ignore_index=False)

df_csv.reset_index(drop=True, inplace=True)
df_csv.columns = ["date", "sec", "data1", "data2", "data3"]

fig = plt.figure(figsize=(10, 6))
ax = fig.add_subplot()
df_csv[0:1000000]["data1"].plot(ax=ax)
_ = ax.set_title("読み込んだデータの一部（0～1000000）")
_ = ax.grid(True)
_ = ax.legend()
plt.show()

delta_period = 2
temp = pd.DataFrame(df_csv["data1"].diff(delta_period).fillna(0))
temp.columns = ["delta"]
df_delta = pd.merge(df_csv, temp, left_index=True, right_index=True)

delta_end_period = 5
delta_start_period = -5

end_duplication_index = df_delta.index[df_delta["delta"] > delta_end_period].tolist()
start_duplication_index = df_delta.index[df_delta["delta"] < delta_start_period].tolist()


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


end_index = delete_duplicaion_index(end_duplication_index)
start_duplication_index.reverse()
start_index = delete_duplicaion_index(start_duplication_index)
start_index.reverse()

df_extract = pd.DataFrame(list(zip(start_index, end_index)), columns=["start", "end"])
df_extract = df_extract.assign(period=df_extract["end"] - df_extract["start"])


fig = plt.figure(figsize=(10, 6))
ax = fig.add_subplot()
df_extract["period"].plot(ax=ax)
_ = ax.set_title("切り出した区間の長さをプロット:おかしな値が無いかここで確認する")
_ = ax.grid(True)
plt.show()


fig, ax = plt.subplots(3, 3, figsize=[12, 8])
ax_f = ax.flatten()
for i, (m, n) in enumerate(zip(df_extract["start"], df_extract["end"])):
    if 1000 < i < 1010:
        ax_f[i - 1001].plot(df_delta[m:n]["data1"])
        _ = ax_f[i - 1001].set_title(i)
        _ = ax_f[i - 1001].grid(True)
plt.show()


extract_time = [100, 200, 300, 400]
temp_data = [[] for i in range(4)]

for m in df_extract["start"]:
    for i, n in enumerate(extract_time):
        temp_data[i].append(df_delta.loc[m + n]["data1"])

for i, n in enumerate(["1st", "2nd", "3rd", "4th"]):
    df_extract[n] = temp_data[i]


fig = plt.figure(figsize=(10, 6))
ax = fig.add_subplot()
for i in ["1st", "2nd", "3rd", "4th"]:
    df_extract[i].plot(ax=ax)
_ = ax.grid(True)
_ = ax.legend()
plt.show()

df_extract.to_excel("output.xlsx", sheet_name="result")
