from collections import OrderedDict

import numpy as np
import pandas as pd

def check_for_any_data(data: list) -> list:
    has_any_data = []
    for element in data:
        frame_has_data = False
        for key, value in element.items():
            if key != 'image_name' and len(value) > 0:
                frame_has_data = True
                break
        has_any_data.append(frame_has_data)
    return has_any_data

def convert_data_to_df(data: list, image_names=None) -> pd.DataFrame:
    has_any_data = check_for_any_data(data)
    
    # rows = {}
    indices = []
    rows = []
    keys = []
    for i, element in enumerate(data):
        row = OrderedDict()
        if not has_any_data[i]:
            continue
        for key, value in element.items():
            if value is None or np.isnan(value).sum() > 0:
                value = [np.nan, np.nan]
                p = 0
            else:
                p = 1
            row[key + '_x'] = value[0]
            row[key + '_y'] = value[1]
            row[key + '_p'] = p
            if i == 0:
                keys.append(key + '_x')
                keys.append(key + '_y')
                keys.append(key + '_p')
        rows.append(row)
        indices.append(i)

    df = pd.DataFrame( data=rows, columns=keys, index=indices)
    if image_names is not None:
        df = df.join(pd.DataFrame(
            data=[image_names[i] for i in indices], 
            columns=['image_name'], index=indices))

    return df

def convert_row_to_dict(row) -> dict:
    N = len(row) // 3
    keys = row.keys().to_list()
    
    data = OrderedDict()
    for i in range(0, len(row), 3):
        x = row[i]
        y = row[i+1]
        p = row[i+2]
        if np.isnan(x) or np.isnan(y) or p < 1e-7:
            x = np.nan
            y = np.nan
            p = 0
        # chop off the _x, _y, or _p at the end
        key = keys[i][:-2]
        # don't do anything with p for now
        data[key] = np.array([x, y]).astype(np.float32)
    return data

def convert_df_to_data(df: pd.DataFrame, n_frames: int, empty_dict: dict) -> list:
    data = []
    
    frames_with_data = df.index.to_list()
    for i in range(n_frames):
        if i in frames_with_data:
            row = df.loc[i]
            row = convert_row_to_dict(row)
            # print(row)
            data.append(row)
        else:
            data.append(empty_dict)
    return data
    