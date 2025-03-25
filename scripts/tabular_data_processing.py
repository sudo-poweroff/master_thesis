import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.preprocessing import StandardScaler
from encode_fields import *
from azure_connection import get_azure_connection
import os

def na_values_count(df, dataset):
    # Exclude participant_id column for NA analysis
    cols_excluding_id = [col for col in df.columns if col != "participant_id"]

    # Count rows with all NA values (except participant_id)
    all_na_rows_count = df[cols_excluding_id].isna().all(axis=1).sum()

    # Count rows with 50% or more NA values
    half_na_rows_count = (df[cols_excluding_id].isna().mean(axis=1) >= 0.5).sum()

    # Count columns with 50% or more NA values
    na_col_percentage = df.isna().mean()
    half_na_cols = na_col_percentage[na_col_percentage >= 0.5].index.tolist()
    half_na_cols_count = len(half_na_cols)

    # Count columns with all NA values
    all_na_cols = df.isna().all()
    all_na_cols_list = all_na_cols[all_na_cols].index.tolist()
    all_na_cols_count = len(all_na_cols_list)

    output_data = {
        "Statistic": ["All NA Rows (except participant_id)", "Rows with >= 50% NA", "Columns with >= 50% NA", "Columns with all NA"],
        "Count": [all_na_rows_count, half_na_rows_count, half_na_cols_count, all_na_cols_count],
        "Column Names": ["", "", ", ".join(half_na_cols), ", ".join(all_na_cols_list)]
    }

    output_df = pd.DataFrame(output_data)
    output_file_path = f"{dataset}/na_analysis_results.csv"
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
    output_df.to_csv(output_file_path, index=False)


def remove_all_na_rows(df):
    cols_excluding_id = [col for col in df.columns if col != "participant_id"]

    # Remove rows with all NA values (except participant_id)
    df_cleaned = df[~df[cols_excluding_id].isna().all(axis=1)]
    return df_cleaned


def remove_all_equal_cols(df):
    # Check for columns with all equal values
    equal_cols = df.columns[df.nunique() == 1].tolist()

    if equal_cols:
        df.drop(equal_cols, axis=1, inplace=True)

    return df

def remove_all_na_columns(df):
    cleaned_df = df.dropna(axis=1, how='all')
    return cleaned_df


def normalize_data(df, threshold=10):
    scaler = StandardScaler()
    continuous_cols = [col for col in df.columns 
                        if pd.api.types.is_numeric_dtype(df[col]) and df[col].nunique() > threshold]
    df[continuous_cols] = scaler.fit_transform(df[continuous_cols])
    return df


def plot_correlation(df, dataset):
    numeric_cols = df.select_dtypes(include=np.number)
    corr_matrix = numeric_cols.corr()
    os.makedirs(dataset, exist_ok=True)
    pd.DataFrame(corr_matrix).to_csv(f"{dataset}/correlation_matrix.csv")
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
    plt.title(f"{dataset} correlation matrix")
    plt.savefig(f"{dataset}/heatmap.png")
    plt.show()
    


def select_significant_features(df, target_col, threshold=0.3):
    # Select only numeric columns
    numeric_df = df.select_dtypes(include=np.number)

    # Verify if target column is numeric
    if target_col not in numeric_df.columns:
        print(f"Target column '{target_col}' is not numeric or not exists.")
        return []

    # Compute correlation with target column
    correlations = numeric_df.corr()[target_col].drop(target_col)
    significant_features = correlations[correlations.abs() >= threshold].index.tolist()
    
    print(f"Significant features for '{target_col}': {significant_features}")
    return significant_features


def estimate_missing_values(df, target_col, k=5):
    # Select significant features for target column
    feature_cols = select_significant_features(df, target_col=target_col, threshold=0.3)
    
    if not feature_cols:
        print(f"No significant features for {target_col}, KNN imputation will be used.")
        # Apply KNN imputation
        knn_imputer = KNNImputer(n_neighbors=k)
        numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
        
        if target_col in numeric_cols:
            cols_for_imputation = [col for col in numeric_cols if col != target_col]
            cols_for_imputation.append(target_col)

            # Filter rows with missing values
            mask_missing = df[target_col].isna()
            data_for_imputation = df.loc[mask_missing, cols_for_imputation]

            # Impute only if there are missing values
            if not data_for_imputation.empty:
                imputed_data = knn_imputer.fit_transform(df[cols_for_imputation])
                
                # Update DataFrame with imputed values
                df.loc[mask_missing, target_col] = imputed_data[mask_missing.values, cols_for_imputation.index(target_col)]

                print(f"KNN Imputation completed for '{target_col}'.")
                return feature_cols
        else:
            print(f"Column '{target_col}' is not numeric, KNN not applied.")

    
    else:
        data = df[feature_cols + [target_col]]
        categorical_cols = [col for col in feature_cols if df[col].dtype == 'object']
        
        # One-Hot Encoding
        encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        encoded_features = pd.DataFrame(
            encoder.fit_transform(data[categorical_cols]),
            columns=encoder.get_feature_names_out(categorical_cols)
        )
        
        numeric_features = data.drop(categorical_cols + [target_col], axis=1, errors='ignore')
        complete_data = pd.concat([numeric_features, encoded_features], axis=1)

        train_data = complete_data[~data[target_col].isna()]
        y_train = data.loc[~data[target_col].isna(), target_col]
        missing_data = complete_data[data[target_col].isna()]

        imputer = SimpleImputer()
        train_data = pd.DataFrame(imputer.fit_transform(train_data), columns=train_data.columns)
        missing_data = pd.DataFrame(imputer.transform(missing_data), columns=missing_data.columns)

        # Model training and prediction
        if not train_data.empty:
            model = LinearRegression()
            model.fit(train_data, y_train)
            predicted_target_col = model.predict(missing_data)
            
            # DataFrame update with predicted values
            df.loc[data[target_col].isna(), target_col] = predicted_target_col
            print(f"Missing values for '{target_col}' successfully predicted.")
            return feature_cols
        else:
            print("There are not enough data for model training.")

def split_alzheimer_dataset(df, second_phase, dataset):
    data = df[df['second_phase'] == second_phase]

    output_path = f"{dataset}/participants_second_phase_{second_phase}.csv"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    data.to_csv(output_path, index=False, na_rep='n/a')
    return output_path

def obtain_data(file_path):
    blob_client = source_container_client.get_blob_client(file_path)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)  
    with open(file_path, "wb") as temp_file:
        temp_file.write(blob_client.download_blob().readall())

if __name__ == "__main__":
    source_container_name = input("Insert the source container name: ")
    destination_container_name = input("Insert the destination container name: ")
    connection_string = input("Insert the connection string: ")
    source_container_client = get_azure_connection(source_container_name, connection_string)
    destination_container_client = get_azure_connection(destination_container_name, connection_string)
    dataset = input("Insert the dataset name on which apply AI data preparation: ")

    if "alzheimer_dataset" in dataset:
        file_path = 'alzheimer_dataset/participants.csv'
        obtain_data(file_path)
        df = pd.read_csv(file_path)
        if "second_phase_0" in dataset:
            file_path = split_alzheimer_dataset(df=df, second_phase=0, dataset=dataset)
        elif "second_phase_1" in dataset:
            file_path = split_alzheimer_dataset(df=df, second_phase=1, dataset=dataset)

    elif dataset == "ecg_dataset":
        file_path = 'ecg_dataset/machine_measurements.csv'
        obtain_data(file_path)
    
    else: 
        file_path = f'{dataset}/participants.csv'
        obtain_data(file_path)

    df = pd.read_csv(file_path)

    # n/a value analysis
    na_values_count(df=df, dataset=dataset)
    df = remove_all_na_rows(df=df)
    df = remove_all_equal_cols(df=df)
    df = remove_all_na_columns(df=df)

    if dataset == "stroke_dataset":
        #replace 89+ with 89 in age column
        df['age'] = df['age'].replace('89+', '89')
        df['age'] = pd.to_numeric(df['age'])
        df = encode_sex_onehot(df=df)
        df = encode_race_onehot(df=df)
        df = encode_etiology(df=df)

    elif dataset == "aphasia_dataset":
        df = encode_sex_onehot(df=df)
        df = encode_race_onehot(df=df)
        df = encode_wab_type(df=df)

    elif "alzheimer_dataset" in dataset:
        df = encode_APOE_rs(df=df, apoe_rs='APOE_rs429358')
        df = encode_APOE_rs(df=df, apoe_rs='APOE_rs7412')
        df = encode_APOE_halotype(df=df)
        df = encode_PICALM_rs3851179(df=df)

    elif dataset == "ecg_dataset":
        df.drop('report', axis=1, inplace=True)
        df = encode_bandwidth(df=df)
        df = encode_filtering(df=df)
       
    cleaned_file_path = f"{file_path.split('.')[0]}_cleaned.csv"
    df = df.map(lambda x: str(int(x)) if isinstance(x, float) and x.is_integer() else x)
    df.to_csv(cleaned_file_path, sep=',', index=False, na_rep='n/a')
    print(f"Cleaned dataframe saved in: {cleaned_file_path}")

    destination_blob_client = destination_container_client.get_blob_client(blob=cleaned_file_path.replace(cleaned_file_path.split('/')[0], 'alzheimer_dataset') if 'alzheimer_dataset' in dataset else cleaned_file_path)
    with open(cleaned_file_path, "rb") as data:
        destination_blob_client.upload_blob(data, overwrite=True)
    print(f"Cleaned dataframe uploaded to destination container.")

    df = pd.read_csv(cleaned_file_path)
    if dataset == "ecg_dataset":
        df['participant_id'] = df['participant_id'].astype(str)
        df['study_id'] = df['study_id'].astype(str)
        df['cart_id'] = df['cart_id'].astype(str)

    df = normalize_data(df)
    missing_value_cols = df.columns[df.isna().any()].tolist()
    print(f"Missing value columns: {missing_value_cols}")

    plot_correlation(df=df, dataset=dataset)

    report_data ={'Column Name':[], 'Missing Values':[], 'Feature Columns':[], 'Imputation Method':[]}
    for col in missing_value_cols:
        print(f"\n>>> Column: {col} <<<")
        missing_values = df[col].isna().sum()
        print(f"Nan values before imputation: {missing_values}")
        features = estimate_missing_values(df=df, target_col=col)
        report_data['Column Name'].append(col)
        report_data['Missing Values'].append(missing_values)
        report_data['Feature Columns'].append(features)
        report_data['Imputation Method'].append("KNN Imputation" if not features else "Linear Regression")
    report_file_path = f"{file_path.split('.')[0]}_report.csv"  
    pd.DataFrame(report_data).to_csv(report_file_path, index=False)

    final_file_path = f"{file_path.split('.')[0]}_final.csv"
    df = df.map(lambda x: str(int(x)) if isinstance(x, float) and x.is_integer() else x)
    df.to_csv(final_file_path, sep=',', index=False, na_rep='n/a')
    print(f"Final dataframe saved in: {final_file_path}")
    
    destination_blob_client = destination_container_client.get_blob_client(blob= final_file_path.replace(final_file_path.split('/')[0], 'alzheimer_dataset') if 'alzheimer_dataset' in dataset else final_file_path)
    with open(final_file_path, "rb") as data:
        destination_blob_client.upload_blob(data, overwrite=True)
    print(f"Final dataframe uploaded to destination container.")
    
    os.remove(file_path)
    os.remove(cleaned_file_path)
    os.remove(final_file_path)