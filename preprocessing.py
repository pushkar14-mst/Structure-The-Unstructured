import pandas as pd
from sklearn.impute import SimpleImputer
# from sklearn.preprocessing import MinMaxScaler
from sklearn.pipeline import Pipeline


def preprocess_data(df, numeric_cols):
    pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='mean')),
        # ('scaler', MinMaxScaler())
    ])

    df_processed = pipeline.fit_transform(df[numeric_cols])
    df[numeric_cols] = df_processed
    return df



