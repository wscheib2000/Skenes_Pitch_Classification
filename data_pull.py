from pybaseball import playerid_lookup, statcast, cache
import pandas as pd
import numpy as np

SKENES = playerid_lookup('skenes', 'paul')

# data = statcast(start_dt=f'2024-04-24', end_dt=f'2024-07-24')
# data.to_csv(f'./data/2024data.csv')

# cache.disable()

# for year in range(2022, 2024):
#     print(f'Year: {year}')
#     data = statcast(start_dt=f'{year}-04-24', end_dt=f'{year}-04-23')
#     data.to_csv(f'./data/{year}data.csv')
# data = statcast(start_dt=f'2024-04-24', end_dt=f'2024-07-22')
# data.to_csv(f'./data/2024data.csv')

# data = pd.read_csv('./data/2023data.csv')
# data = pd.concat([data, pd.read_csv(f'./data/2024data.csv')], axis=0, ignore_index=True)
# data.to_csv('./data/data.csv', index=False)

# Load and clean data
data = pd.read_csv('./data/data.csv')
data = data.loc[:,['player_name', 'pitcher', 'pitch_type', 'p_throws', 'release_speed', 'effective_speed', 'release_spin_rate', 'release_pos_x', 'release_pos_y', 'release_extension', 'plate_x', 'plate_z', 'pfx_x', 'pfx_z', 'vx0', 'vy0', 'vz0', 'ax', 'ay', 'az']]

print(data.loc[data.pitcher == SKENES,:].shape[0])
data = data.dropna(how='any')

print(data.loc[data.pitcher == SKENES,:].shape[0])
# Normalize speed columns by pitcher (we care about speed of a pitch relative to that pitcher's other offerings)
groups = data.groupby('pitcher')[['release_speed', 'effective_speed']]
mean, std = groups.transform('mean'), groups.transform('std')
data[mean.columns] = (data[mean.columns] - mean) / std

# Filter for only splitters and sinkers
print(data.loc[data.pitcher == SKENES,:].shape[0])
data = data.loc[(data.pitch_type == 'SI') + (data.pitch_type == 'FS') >= 1,:]

pitch_types = data.pitch_type.unique()
print(pitch_types)

# Reverse break left/right directions for lefties so all pitches break the same way regardless of handedness
data = data.assign(
                p_throws_r = data.p_throws == 'R'
            ) \
            .drop(['p_throws'], axis=1)
data = data.assign(
                pfx_x = data.pfx_x * np.where(data.p_throws_r, 1, -1),
                vx0 = data.vx0 * np.where(data.p_throws_r, 1, -1),
                ax = data.ax * np.where(data.p_throws_r, 1, -1)
            )

print(data.loc[data.pitcher == SKENES,:].shape[0])
print(data.pitch_type.unique())

data = data.dropna(how='any')
data.to_csv('./data/clean_data.csv', index=False)
pitch_types.tofile('./data/pitch_types.csv', sep=',')