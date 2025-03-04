import pandas as pd

def encode_sex_onehot(df):
    for index,row in df.iterrows():
        if not pd.isna(row['sex']):
            if row['sex'] == 'M':
                df.at[index, 'sex'] = 1
            else:   
                df.at[index, 'sex'] = 0
    return df


def encode_race_onehot(df):
    for index,row in df.iterrows():
        if not pd.isna(row['race']):
            if row['race'] == 'w':
                df.at[index, 'race'] = 1
            else:   
                df.at[index, 'race'] = 0
    return df


def encode_etiology(df):
    for index,row in df.iterrows():
        if not pd.isna(row['etiology']):
            if 'Large-artery atherosclerosis (e.g., carotid or basilar artery stenosis)' in row['etiology']:
                df.at[index, 'etiology'] = 1
            elif 'Cardioembolism (e.g., atrial fibrillation/flutter, prosthetic heart valve, recent MI)' in row['etiology']:
                df.at[index, 'etiology'] = 2
            elif 'Small-vessel disease (e.g., Subcortical or brain stem lacunar infarction <1.5 cm)' in row['etiology']:
                df.at[index, 'etiology'] = 3
            elif 'Stroke of other determined etiology' in row['etiology']:
                df.at[index, 'etiology'] = 4
            else:
                df.at[index, 'etiology'] = 5
    return df

def encode_wab_type(df):
    for index,row in df.iterrows():
        if not pd.isna(row['wab_type']):
            if row['wab_type'] == 'Anomic':
                df.at[index, 'wab_type'] = 0
            elif row['wab_type'] == 'Broca':   
                df.at[index, 'wab_type'] = 1
            elif row['wab_type'] == 'Conduction':
                df.at[index, 'wab_type'] = 2
            elif row['wab_type'] == 'Global':
                df.at[index, 'wab_type'] = 3
            elif row['wab_type'] == 'TranscorticalMotor':
                df.at[index, 'wab_type'] = 4
            elif row['wab_type'] == 'Wernicke':
                df.at[index, 'wab_type'] = 5
            else:
                df.at[index, 'wab_type'] = 6
    return df

def encode_APOE_rs(df, apoe_rs):
    for index,row in df.iterrows():
        if not pd.isna(row[apoe_rs]):
            if row[apoe_rs] == 'C/C':
                df.at[index, apoe_rs] = 0
            elif row[apoe_rs] == 'C/T':   
                df.at[index, apoe_rs] = 1
            elif row[apoe_rs] == 'T/C':
                df.at[index, apoe_rs] = 2
            else:
                df.at[index, apoe_rs] = 3
    return df

def encode_APOE_halotype(df):
    for index,row in df.iterrows():
        if not pd.isna(row['APOE_haplotype']):
            if row['APOE_haplotype'] == 'ε2/ε2':
                df.at[index, 'APOE_haplotype'] = 0
            elif row['APOE_haplotype'] == 'ε2/ε3':   
                df.at[index, 'APOE_haplotype'] = 1
            elif row['APOE_haplotype'] == 'ε2/ε4':
                df.at[index, 'APOE_haplotype'] = 2
            elif row['APOE_haplotype'] == 'ε3/ε2':
                df.at[index, 'APOE_haplotype'] = 3
            elif row['APOE_haplotype'] == 'ε3/ε3':
                df.at[index, 'APOE_haplotype'] = 4
            elif row['APOE_haplotype'] == 'ε3/ε4':
                df.at[index, 'APOE_haplotype'] = 5
            elif row['APOE_haplotype'] == 'ε4/ε2':
                df.at[index, 'APOE_haplotype'] = 6
            elif row['APOE_haplotype'] == 'ε4/ε3':
                df.at[index, 'APOE_haplotype'] = 7
            else:
                df.at[index, 'APOE_haplotype'] = 8
    return df

def encode_PICALM_rs3851179(df):
    for index,row in df.iterrows():
        if not pd.isna(row['PICALM_rs3851179']):
            if row['PICALM_rs3851179'] == 'A/A':
                df.at[index, 'PICALM_rs3851179'] = 0
            elif row['PICALM_rs3851179'] == 'A/G':   
                df.at[index, 'PICALM_rs3851179'] = 1
            elif row['PICALM_rs3851179'] == 'G/A':
                df.at[index, 'PICALM_rs3851179'] = 2
            else:
                df.at[index, 'PICALM_rs3851179'] = 3
    return df

def encode_bandwidth(df):
    for index,row in df.iterrows():
        if not pd.isna(row['bandwidth']):
            if row['bandwidth'] == '0.005-150 Hz':
                df.at[index, 'bandwidth'] = 0
            elif row['bandwidth'] == '0.0005-150 Hz':   
                df.at[index, 'bandwidth'] = 1
            else:
                df.at[index, 'bandwidth'] = 2
    return df

def encode_filtering(df):
    for index,row in df.iterrows():
        if not pd.isna(row['filtering']):
            if row['filtering'] == 'Baseline filter':
                df.at[index, 'filtering'] = 0
            elif row['filtering'] == '50 Hz notch Baseline filter':   
                df.at[index, 'filtering'] = 1
            elif row['filtering'] == '60 Hz notch Baseline filter':
                df.at[index, 'filtering'] = 2
            else:
                df.at[index, 'filtering'] = 3   
    return df