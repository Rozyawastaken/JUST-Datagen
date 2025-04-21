import pandas as pd
import re


def custom_filter(text):
    text = re.sub(r'\d+', "", text)

    text = text.strip()
    if len(text) <= 10:
        return text  # e.g. Чарівність

    text_split = text.split()
    if len(text_split) == 1:
        return text  # e.g. Прикріплення

    for t in text_split:
        if len(t) > 3:
            return t

    return None


if __name__ == '__main__':
    df = pd.read_parquet("C:\\Users\\Icem1\\PycharmProjects\\SRNEt-Datagen\\Synthtext\\files\\words\\words.parquet")
    print(df.head(50))
    print(df.info())
    df["ukrainian"] = df["ukrainian"].apply(custom_filter)
    df = df[~df["ukrainian"].isnull()]
    print(df.head(50))
    print(df.info())
    df.to_parquet("C:\\Users\\Icem1\\PycharmProjects\\SRNEt-Datagen\\Synthtext\\files\\words\\words.parquet", index=False)
