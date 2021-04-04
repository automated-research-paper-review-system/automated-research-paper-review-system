import pandas as pd
from pandas import DataFrame

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
    return result

if __name__=="__main__":
    read_json('/home/kapil/SJSU-Acad/MastersProject/PeerRead/data/conll_2016/train/parsed_pdfs/12.pdf.json')