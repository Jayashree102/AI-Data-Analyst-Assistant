import pandas as pd

def load_data(file):
    """Loads a CSV or Excel file into a pandas DataFrame."""
    try:
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file)
        else:
            return None, "Unsupported file format. Please upload a CSV or Excel file."
        return df, None
    except Exception as e:
        return None, f"Error loading file: {str(e)}"

def get_data_summary(df):
    """Returns a basic summary of the dataframe."""
    summary = {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "missing_values": int(df.isnull().sum().sum()),
        "duplicates": int(df.duplicated().sum()),
        "numeric_cols": list(df.select_dtypes(include='number').columns),
        "categorical_cols": list(df.select_dtypes(exclude='number').columns)
    }
    return summary
