import numpy as np
import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

url1 = "https://docs.google.com/spreadsheets/d/1i27F6-m9R0VrA27TxZtgfuIV1StvkOFw1v6ewPrgrWs/edit?usp=sharing"
url2 = "https://docs.google.com/spreadsheets/d/1nBT6MEtra_IkoIinBisgNgsn2TiS-NsTtcMdrO1Y2EE/edit?usp=sharing"
url3 = "https://docs.google.com/spreadsheets/d/1Lp-k_DSKNLQ58xxC3ST7aert508402zVKC6Z4cgvjv8/edit?usp=sharing"

# Choose gsheet files
activity = []
opt1 = "นำเสนอภาคบรรยายระดับชาติ"
opt2 = "นำเสนอภาคบรรยายระดับปริญญาตรี"
opt3 = "นำเสนอโปสเตอร์"
activity.append(opt1)
activity.append(opt2)
activity.append(opt3)

st.title(":rainbow[การประเมินผลการนำเสนอผลงานทางวิชาการ FENETT 2025]")
opt = st.selectbox("", activity, label_visibility="collapsed")

if opt == opt1:
    url = url1
if opt == opt2:
    url = url2
if opt == opt3:
    url = url3

# Create a connection object
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(
    spreadsheet=url,
    ttl="0",
    usecols=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
)
df.columns = ['Timestamp', 'Assessor_code', 'Article_code', 'Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7']
#print(df)

st.subheader(":blue[คะแนนการนำเสนอ]")
st.dataframe(df)

df_arr = df.to_numpy()
score_arr = df_arr[:, 3:10]
rows = np.size(score_arr, 0)
cols = np.size(score_arr, 1) 
#print(score_arr)

assessor = []
article = []
article_arr = []

for row in df.itertuples():
    #print(row)
    article_arr.append(row.Article_code)
    if row.Article_code not in article:
        article.append(row.Article_code)
    if row.Assessor_code not in assessor:
        assessor.append(row.Assessor_code)

print(assessor)
print(article)
numOfassessors = len(assessor)
numOfarticles = len(article)

# calculate mean and sd, and convert to zscore
score = np.zeros((numOfassessors,numOfarticles))
zscore = np.zeros((numOfassessors,numOfarticles))
assessor_mean = []
assessor_sd = []

for i in range(numOfassessors):
    r = -1
    for row in df.itertuples():
        r = r + 1
        if row.Assessor_code == assessor[i]:
            s = 0
            for c in range(cols):
                s = s + score_arr[r,c]
            article_name = row.Article_code
            k = article.index(article_name)
            score[i,k] = s
    
    # eliminate zero in score
    buf = []
    for m in range(numOfarticles):
        if score[i,m] != 0:
            buf.append(score[i,m])
    #print(buf)
    #mean = np.mean(np.array(buf))
    #sd = np.std(np.array(buf))
    mean = np.mean(buf)
    sd = np.std(buf)
    #print(sd)
    #if sd == 0:
        #print("sd = 0")
    assessor_mean.append(mean)
    assessor_sd.append(sd)

    for n in range(numOfarticles):
        if score[i,n] != 0:
            if sd != 0:
                zscore[i,n] = (score[i,n] - mean) / sd

print(assessor_mean)
print(assessor_sd)
#print(zscore)

st.subheader(":blue[Score]")
mean_arr = np.array(assessor_mean)
mean_arr = mean_arr.reshape(numOfassessors, 1)
sd_arr = np.array(assessor_sd)
sd_arr = sd_arr.reshape(numOfassessors, 1)
score_buf = score
score_buf = np.append(score_buf, mean_arr, axis=1)
score_buf = np.append(score_buf, sd_arr, axis=1)

score_sum = np.sum(score_buf, axis=0)
score_sum = score_sum.reshape(1,len(score_sum))
score_buf = np.append(score_buf, score_sum, axis=0)

assessor_buf = assessor[:]
assessor_buf.append('Sum')
article_buf = article[:]
article_buf.append('Mean')
article_buf.append('SD')
df_score = pd.DataFrame(score_buf, index=assessor_buf, columns=article_buf)
st.dataframe(df_score)

# mask missing value
#print(score)
#mask = np.where(score==0)
#print(mask)

st.subheader(":blue[Z-score]")
zscore_buf = zscore
zscore_sum = np.sum(zscore_buf, axis=0)
zscore_sum = zscore_sum.reshape(1,len(zscore_sum))

#print(score)
#print(zscore)
zscore_avg = []
for i in range(numOfarticles):
    z = 0
    cnt = 0
    for j in range(numOfassessors):
        if score[j,i] != 0:
            cnt = cnt + 1
            z = z + zscore[j,i]
    zscore_avg.append(z / cnt)

#print(zscore_avg)
zscore_avg = np.array(zscore_avg)
mean_zscore = zscore_avg
zscore_avg = zscore_avg.reshape(1,len(zscore_avg))

zscore_buf = np.append(zscore_buf, zscore_sum, axis=0)
zscore_buf = np.append(zscore_buf, zscore_avg, axis=0)

assessor_buf.append('Average')
df_zscore = pd.DataFrame(zscore_buf, index=assessor_buf, columns=article)
st.dataframe(df_zscore)

# summation of score for each article 
total_zscore = np.sum(zscore, axis=0)

# sorting
sort_index = np.argsort(total_zscore)
#print(sort_index)
sort_index2 = np.argsort(mean_zscore)
#print(sort_index2)

col = st.columns(2)
col[0].subheader(":blue[เรียงคะแนนตาม total z-score]")
col[1].subheader(":blue[เรียงคะแนนตาม average z-score]")

sort_len = len(sort_index)
for i in range(sort_len):
    k = sort_len - i - 1
    idx = sort_index[k]
    col_2nd = col[0].columns(2)
    col_2nd[0].markdown(article[idx])
    col_2nd[1].markdown(total_zscore[idx])

    idx = sort_index2[k]
    col_2nd = col[1].columns(2)
    col_2nd[0].markdown(article[idx])
    col_2nd[1].markdown(mean_zscore[idx])
