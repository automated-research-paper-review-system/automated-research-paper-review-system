import pandas as pd
from pandas import DataFrame
from pandas.errors import InvalidIndexError
import os
import json
from preprocess_text import preprocess_reviews_dataframe

def read_reviews_from_json(path_to_json):
    try:
        df = pd.read_json(open(path_to_json))
        # df["id"] = int(df["int"])
    except:
        # df = pd.read_json(open(path_to_json), orient='table')
        with open(path_to_json) as json_data:
            data = json.load(json_data)
            # if "." in str(data["id"]):
                # string_id = str(data["id"]).split('.')[1]
                # data["id"] = int(string_id)
                # data["id"] = int(data["id"])
            if "accepted" in data:
                df = pd.DataFrame({"id": [data['id']], "title": [data['title']], "abstract": [data['abstract']], "reviews": [data['reviews']], "accepted": [data['accepted']]})
            else:
                df = pd.DataFrame({"id": [data['id']], "title": [data['title']], "abstract": [data['abstract']], "reviews": [data['reviews']]})
                # df["id"] = int(data["id"])
    return df

def create_reviews_dataframe():
    rootdir = '/home/kapil/SJSU-Acad/MastersProject/codebase/data'
    columns_list = ["id", "title", "abstract", "reviews", "accepted"]
    df = pd.DataFrame(columns=columns_list)
    count = 0
    valueErrorCount = 0
    indexErrorCount = 0
    for subdir, dirs, files in os.walk(rootdir):
        if subdir.endswith('train/reviews'):
            for x, y, filenames in os.walk(subdir):
                for filename in filenames:
                    try:
                        df1 = read_reviews_from_json(subdir + '/' + filename)
                        df = df.append(df1[df1.columns & columns_list], ignore_index=True)
                        # df = df.append(df1)
                        count += 1
                        print('Added in reviews dataframe: ', count)
                    except InvalidIndexError:
                        valueErrorCount += 1
                        print('Value Error count: ', valueErrorCount)
                        continue
                    except IndexError:
                        indexErrorCount += 1
                        print('Index Error count: ', indexErrorCount)
                        continue
    df = df.rename({'abstract': 'abstractText'}, axis=1)
    preprocess_reviews_dataframe(df)
    return df

if __name__ == '__main__':
    df = create_reviews_dataframe()
    print(len(pd.unique(df['id'])))
    print(len(pd.unique(df['title'])))
    print(len(pd.unique(df['abstract'])))
    df = df.sort_values(by=['id'],)
    print(df.count())
    print(df.accepted.value_counts())
    # print(len(pd.unique(df['id'])))
    print()