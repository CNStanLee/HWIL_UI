import pandas as pd

if __name__ == '__main__':
    print("dataset explore")
    df = pd.read_csv('DoS_dataset.csv')
    print(df.columns.tolist())
    print(df.head())