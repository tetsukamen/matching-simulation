"""
データセットの作成
"""
import random
import numpy as np
import pandas as pd

appearance_distb = pd.DataFrame(
    {
        "rate": [0.5, 1.2, 5.6, 19.3, 31.4, 25.0, 11.3, 4.0, 1.3, 0.4],
        "value": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    }
)

income_distb = pd.DataFrame(
    {
        "男": [5.5, 36.9, 28.8, 22.4, 6.1, 0.4],
        "女": [16.3, 54.3, 20.2, 7.9, 1.2, 0.1],
        "賃金階級": [
            "120.0万円 ~ 216.0万円",
            "216.0万円 ~ 336.0万円",
            "336.0万円 ~ 456.0万円",
            "456.0万円 ~ 720.0万円",
            "720.0万円 ~ 1440.0万円",
            "1440.0万円 ~",
        ],
        "value": [1, 2, 4, 6, 8, 10],
    }
)


age_distb = pd.DataFrame(
    {
        "男": [2, 27, 23, 18, 9, 16, 4],
        "女": [1, 32, 22, 24, 9, 11, 1],
        "年齢層": ["10代", "20代前半", "20代後半", "30代前半", "30代後半", "40代", "50代以上"],
        "value": [1, 2, 3, 4, 6, 8, 10],
    }
)

personality_range = [0, 10]

weight_mean = pd.DataFrame(
    {
        "男": [0.7, 0.3, 0.7, 0.8],
        "女": [0.3, 0.7, 0.5, 0.8],
        "label": ["容姿", "収入", "年齢", "性格"],
    }
)

# 人物の特徴の形式
# V_apr: 外見の特徴
# V_inc: 収入の特徴
# V_age: 年齢の特徴
# V_per: 性格の特徴
# W_apr: 外見の重視度
# W_inc: 収入の重視度
# W_age: 年齢の重視度
# W_per: 性格の重視度


def generate_appearance(size: int):
    return appearance_distb.sample(n=size, weights="rate", replace=True)["value"].values


def generate_income(size: int, gender: str):
    return income_distb.sample(n=size, weights=gender, replace=True)["value"].values


def generate_age(size: int, gender: str):
    return age_distb.sample(n=size, weights=gender, replace=True)["value"].values


def generate_personality(size: int):
    return [
        personality_range[0]
        + (personality_range[1] - personality_range[0]) * random.random()
        for _ in range(size)
    ]


def generate_weight(size: int, gender: str, label: str):
    mean = weight_mean[weight_mean["label"] == label][gender]
    random_numbers = np.random.normal(loc=mean, scale=0.1, size=size)
    random_numbers = np.clip(random_numbers, 0, 1)
    return random_numbers


def generate_data(size: int, gender: str):
    return pd.DataFrame(
        {
            "V_apr": generate_appearance(size),
            "V_inc": generate_income(size, "男"),
            "V_age": generate_age(size, "男"),
            "V_per": generate_personality(size),
            "W_apr": generate_weight(size, "男", "容姿"),
            "W_inc": generate_weight(size, "男", "収入"),
            "W_age": generate_weight(size, "男", "年齢"),
            "W_per": generate_weight(size, "男", "性格"),
        }
    )


size = 50
generate_data(size, "男").to_csv("male.csv", index=False)
generate_data(size, "女").to_csv("female.csv", index=False)
