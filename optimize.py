import sys
import os
import shutil
import pandas as pd
from matching.games import StableMarriage
import csv

sys.setrecursionlimit(10000)


def calc_male_value(
    male_idx: int,
    female_idx: int,
    data_male: pd.DataFrame,
    data_female: pd.DataFrame,
    debug=False,
):
    v_apr = data_male["V_apr"][male_idx]
    v_inc = data_male["V_inc"][male_idx]
    v_age = -1 * abs(data_male["V_age"][male_idx] - data_female["V_age"][female_idx])
    v_per = -1 * abs(data_male["V_per"][male_idx] - data_female["V_per"][female_idx])
    w_apr = data_female["W_apr"][female_idx]
    w_inc = data_female["W_inc"][female_idx]
    w_age = data_female["W_age"][female_idx]
    w_per = data_female["W_per"][female_idx]
    if debug:
        print(
            f"v_apr: {v_apr}, v_inc: {v_inc}, v_age: {v_age}, v_per: {v_per}, w_apr: {w_apr}, w_inc: {w_inc}, w_age: {w_age}, w_per: {w_per}\n"
            f"apr: {v_apr * w_apr}, inc: {v_inc * w_inc}, age: {v_age * w_age}, per: {v_per * w_per}",
        )
    return v_apr * w_apr + v_inc * w_inc + v_age * w_age + v_per * w_per


def calc_female_value(
    male_idx: int,
    female_idx: int,
    data_male: pd.DataFrame,
    data_female: pd.DataFrame,
    debug=False,
):
    v_apr = data_female["V_apr"][female_idx]
    v_inc = data_female["V_inc"][female_idx]
    v_age = -1 * data_female["V_age"][female_idx]
    v_per = -1 * abs(data_male["V_per"][male_idx] - data_female["V_per"][female_idx])
    w_apr = data_male["W_apr"][male_idx]
    w_inc = data_male["W_inc"][male_idx]
    w_age = data_male["W_age"][male_idx]
    w_per = data_male["W_per"][male_idx]
    if debug:
        print(
            f"v_apr: {v_apr}, v_inc: {v_inc}, v_age: {v_age}, v_per: {v_per}, w_apr: {w_apr}, w_inc: {w_inc}, w_age: {w_age}, w_per: {w_per}\n"
            f"apr: {v_apr * w_apr}, inc: {v_inc * w_inc}, age: {v_age * w_age}, per: {v_per * w_per}",
        )
    return v_apr * w_apr + v_inc * w_inc + v_age * w_age + v_per * w_per


def calc_pref_rank(pair_idx: int, pref_list: list):
    for i, idx in enumerate(pref_list):
        if idx == pair_idx:
            return i + 1
    return -1


# save result
def save_matching_result_to_csv(matchings, file_path):
    with open(file_path, "w", newline="") as csvfile:
        fieldnames = ["Male_idx", "Female_idx"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for male, female in matchings.items():
            writer.writerow({"Male_idx": male, "Female_idx": female})


def optimize(
    data_male: pd.DataFrame,
    data_female: pd.DataFrame,
    dir: str,
):
    size = len(data_male)
    # 男性の選好を計算
    male_pref = {}
    for male_idx in range(size):
        val_idx_list = []
        for i in range(size):
            value = calc_female_value(male_idx, i, data_male, data_female)
            val_idx_list.append((value, i))
        val_idx_list.sort(reverse=True)
        idx_ranking = [i for _, i in val_idx_list]
        male_pref[male_idx] = idx_ranking

    # 女性の選好を計算
    female_pref = {}
    for female_idx in range(size):
        val_idx_list = []
        for i in range(size):
            value = calc_male_value(i, female_idx, data_male, data_female)
            val_idx_list.append((value, i))
        val_idx_list.sort(reverse=True)
        idx_ranking = [i for _, i in val_idx_list]
        female_pref[female_idx] = idx_ranking

    game = StableMarriage.create_from_dictionaries(male_pref, female_pref)
    results = game.solve()

    # Calculate the rank of the matched partner
    male_pref_rank_idx = []
    male_pref_rank_value = []
    for result in results.items():
        male_idx = result[0].name
        pair_idx = result[1].name
        pref_list = male_pref[male_idx]
        pref_rank = calc_pref_rank(pair_idx, pref_list)
        male_pref_rank_idx.append(male_idx)
        male_pref_rank_value.append(pref_rank)
    male_pref_rank = pd.DataFrame(
        {"Male_idx": male_pref_rank_idx, "Male_pref_rank": male_pref_rank_value}
    )
    male_pref_rank.to_csv(f"results/{dir}/male_pref_rank.csv", index=False)

    female_pref_rank_idx = []
    female_pref_rank_value = []
    for result in results.items():
        female_idx = result[1].name
        pair_idx = result[0].name
        pref_list = female_pref[female_idx]
        pref_rank = calc_pref_rank(pair_idx, pref_list)
        female_pref_rank_idx.append(female_idx)
        female_pref_rank_value.append(pref_rank)
    female_pref_rank = pd.DataFrame(
        {"Female_idx": female_pref_rank_idx, "Female_pref_rank": female_pref_rank_value}
    )
    female_pref_rank.to_csv(f"results/{dir}/female_pref_rank.csv", index=False)

    save_matching_result_to_csv(results, f"results/{dir}/matching_result.csv")


if __name__ == "__main__":
    shutil.rmtree("results")
    os.mkdir("results")
    dirs = os.listdir("dataset")
    dirs.sort()
    for dir in dirs:
        print(dir)
        data_male = pd.read_csv(os.path.join("dataset", dir, "male.csv"))
        data_female = pd.read_csv(os.path.join("dataset", dir, "female.csv"))
        os.mkdir(f"results/{dir}")
        optimize(data_male, data_female, dir)
