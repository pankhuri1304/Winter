import pandas as pd


def preprocess(df, region):

    # Merge with region
    df = df.merge(region, on='NOC', how='left')

    # Dropping duplicates
    df.drop_duplicates(inplace=True)

    # One hot encoding medals
    df = pd.concat([df, pd.get_dummies(df['Medal'])], axis=1)
    return df