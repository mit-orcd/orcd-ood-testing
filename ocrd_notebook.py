#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import glob
from datetime import datetime, timedelta


# In[12]:


file_list = glob.glob('sacct_*.lst')
df_list = []
sum_rows = 0
print("hello")
for file in file_list:
    df = pd.read_csv(file, delimiter='|', low_memory=False,on_bad_lines='skip')
    sum_rows += df.shape[0]
    print(df.shape[0])
    df_list.append(df)
# file_path = 'sacct_2024-09-01_2024-09-02_X.lst'

print(sum_rows)
# data = pd.read_csv(file_path, delimiter='|')


# In[13]:


combined_df = pd.concat(df_list, ignore_index=True, join='outer')
summary_stats = combined_df.describe()


# In[26]:


summary_stats = combined_df.describe()
combined_df['CPUTimeRAW'] = pd.to_numeric(combined_df['CPUTimeRAW'], errors='coerce')
combined_df['AllocCPUS'] = pd.to_numeric(combined_df['AllocCPUS'], errors='coerce')
combined_df['AllocNodes'] = pd.to_numeric(combined_df['AllocNodes'], errors='coerce')

# Group by 'User' and aggregate CPUTime and WallTime (example columns)
grouped_summary = combined_df.groupby('User').agg({
    'CPUTimeRAW': 'sum',
    'AllocCPUS':'sum',
    'AllocNodes':'sum',
    'JobID': 'count'
})
grouped_summary = grouped_summary.rename(columns={'JobID': 'Total Number of Jobs'})


# In[27]:


def convert_seconds(seconds):
    days, remainder = divmod(seconds, 86400)   # 86400 seconds in a day
    hours, remainder = divmod(remainder, 3600) # 3600 seconds in an hour
    minutes, seconds = divmod(remainder, 60)   # 60 seconds in a minute
    return f"{int(days)}:{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

# Applying this to the 'CPUTimeRAW' column after summing
grouped_summary['CPUTime'] = grouped_summary['CPUTimeRAW'].apply(convert_seconds)


# In[28]:


print(grouped_summary)

