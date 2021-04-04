import os

from pandas.errors import InvalidIndexError
from parsed_pdfs_to_dataframes import read_json
import pandas as pd


if __name__=="__main__":
    rootdir = '/home/kapil/SJSU-Acad/MastersProject/PeerRead/data'
    columns_list = ["name", "abstractText", "authors", "creator", "emails", "referenceMentions", "references", "title", "year", " Introduction", " Related Work", " Experiments", " Results", " Conclusion", " Discussion"]
    df = pd.DataFrame(columns= columns_list)
    count = 0
    invalidIndexErrorCount = 0
    indexErrorCount = 0
    for subdir, dirs, files in os.walk(rootdir):
        if subdir.endswith('train/parsed_pdfs'):
            for x, y, filenames in os.walk(subdir):
                for filename in filenames:
                    try:
                        df1 = pd.DataFrame(read_json(subdir+'/'+filename))
                        df =  df.append(df1[df1.columns & columns_list], ignore_index=True)
                        count += 1
                        print('Added in dataframe: ',count)
                    except InvalidIndexError:
                        invalidIndexErrorCount += 1
                        print('Invalid Index Error count: ', invalidIndexErrorCount)
                        continue
                    except IndexError:
                        indexErrorCount += 1
                        print('Index Error count: ', indexErrorCount)
                        continue

    print(df.count())
    print()
