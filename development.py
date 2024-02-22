import pandas as pd

# create a DataFrame with datetime data
df = pd.DataFrame({'date': ['2022-06-01 12:00:00', '2022-06-02 13:00:00', '2022-06-03 14:00:00']})

# convert the date column to datetime format
df['date'] = pd.to_datetime(df['date'])

# change the datetime format
df['date_formatted'] = df['date'].dt.strftime('%H:%M:%S')

print(df)