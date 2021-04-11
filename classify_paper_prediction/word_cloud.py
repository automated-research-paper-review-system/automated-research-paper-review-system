import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud

def realdata(papertexts):
    s = ""
    for i in range(len(papertexts)):
        w_list = papertexts[i].split()
        indexvalue= w_list.index("abstract")+1 if "abstract" in w_list else 0
        s = s+ " ".join( w_list[indexvalue: ] )
    return s

def each_column_word_cloud(df):
    completestring = realdata(df['abstractText'])
    x, y = np.ogrid[:750, :750]
    mask = (x - 375) ** 2 + (y - 375) ** 2 > 390 ** 2
    mask = 255 * mask.astype(int)
    wordcloud = WordCloud(background_color="rgba(255, 255, 255, 0)",
                          mode="RGBA",
                          width=800,
                          height=400,
                          max_words=100,
                          mask=mask
                          ).generate(completestring)
    plt.figure(figsize=(20, 10))
    plt.imshow(wordcloud)
    plt.show()
    plt.axis('off')