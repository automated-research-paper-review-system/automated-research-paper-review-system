import pandas as pd
from pandas import DataFrame
from pandas.errors import InvalidIndexError
import os


def read_json(path_to_json):
    df = pd.read_json(path_to_json)
    name = df.iloc[0]['name']
    df = df.T
    df = df.iloc[1:]
    df.insert(0, 'name', name)
    newdf = DataFrame(df.iloc[0]['sections'])
    newdf = newdf.T
    newdf.iloc[0] = newdf.iloc[0].str.replace('\d+|\.', '')
    newdf.columns = newdf.iloc[0]
    newdf = newdf.iloc[1:]
    newdf.insert(0, 'name', name)
    result = pd.merge(df, newdf, on=["name"])
    referenceMentions_count = str(list(result["referenceMentions"])[0]).lower().split().count('\'context\':')
    references_count = str(list(result["references"])[0]).lower().split().count('\'year\':')
    result['references'] = references_count
    result['referenceMentions'] = referenceMentions_count
    return result

def create_dataframe_from_parsed_pdfs():
    rootdir = '/home/kapil/SJSU-Acad/MastersProject/codebase/data'
    columns_list = ["name", "abstractText", "authors", "creator", "emails", "referenceMentions", "references", "title",
                    "year", " Introduction", " Related Work", " Experiments", " Results", " Conclusion", " Discussion", "accepted"]
    df = pd.DataFrame(columns=columns_list)
    count = 0
    invalidIndexErrorCount = 0
    indexErrorCount = 0
    for subdir, dirs, files in os.walk(rootdir):
        if subdir.endswith('/2016/train/parsed_pdfs'):
            for x, y, filenames in os.walk(subdir):
                for filename in filenames:
                    try:
                        df1 = pd.DataFrame(read_json(subdir + '/' + filename))
                        if "2019" in subdir or "2020" in subdir or "data/2016" in subdir or "data/2017" in subdir:
                            df1['accepted'] = True
                        df = df.append(df1[df1.columns & columns_list], ignore_index=True)
                        count += 1
                        print('Added in dataframe: ', count)
                    except InvalidIndexError:
                        invalidIndexErrorCount += 1
                        print('Invalid Index Error count: ', invalidIndexErrorCount)
                        continue
                    except IndexError:
                        indexErrorCount += 1
                        print('Index Error count: ', indexErrorCount)
                        continue

    return df