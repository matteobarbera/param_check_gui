import os
import pickle
from typing import Iterator

import pandas as pd
import requests
from bs4 import BeautifulSoup, element
from numpy import nan


def parse_url(url: str) -> Iterator[pd.DataFrame]:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    return (parse_html_table(table) for table in soup.find_all('table'))


def parse_html_table(table: element.Tag) -> pd.DataFrame:
    n_columns = 0
    n_rows = 0
    column_names = []

    # Find number of rows and columns
    # we also find the column titles if we can
    for row in table.find_all('tr'):

        # Determine the number of rows in the table
        td_tags = row.find_all('td')
        if len(td_tags) > 0:
            n_rows += 1
            if n_columns == 0:
                # Set the number of columns for our table
                n_columns = len(td_tags)

        # Handle column names if we find them
        th_tags = row.find_all('th')
        if len(th_tags) > 0 and len(column_names) == 0:
            for th in th_tags:
                column_names.append(th.get_text())

    # Safeguard on Column Titles
    if len(column_names) > 0 and len(column_names) != n_columns:
        raise Exception("Column titles do not match the number of columns")

    columns = column_names if len(column_names) > 0 else range(0, n_columns)
    df = pd.DataFrame(columns=columns, index=range(0, n_rows))
    row_marker = 0
    for row in table.find_all('tr'):
        column_marker = 0
        columns = row.find_all('td')
        for column in columns:
            df.iat[row_marker, column_marker] = column.get_text()
            column_marker += 1
        if len(columns) > 0:
            row_marker += 1

    return df


def extract_param_data():
    param_data_df = pd.DataFrame(columns=["Name", "Type", "Min", "Max", "Incr", "Default", "Description"])

    for table in parse_url(px4_param_list_url):
        n_rows = table.shape[0]

        # ----------------- Extract parameter name and type ---------------------
        # Regex breakdown:
        # (?:\s*) Non-capturing group, matches zero to unlimited whitespaces, as many times as possible,
        # giving back as needed
        # (?P<Name>.+(?<!\s|\()) Named capture group, matches any character between one and unlimited times,
        # as much as possible until it encounters a whitespace or bracket
        # (?:[ \(]*) Non-capturing group, matches a whitespace or ( from zero to unlimited times, as many times as
        # possible, giving back as needed
        # (?P<Type>(?<=\()INT32|FLOAT) Named capture group, captures either INT32 or FLOAT,
        # ONLY IF the pattern is preceded by (
        name_type_regex = r"(?:\s*)(?P<Name>.+(?<!\s|\())(?:[ \(]*)(?P<Type>(?<=\()INT32|FLOAT)"
        name_type_df = table["Name"].str.extract(name_type_regex, expand=True)

        # ------------- Extract parameter min, max and increment ----------------
        # Regex pattern matches all groups of digits, ., ?, - and unstack the result to remove the MultiIndex
        min_max_incr_regex = r"([\d.?-]+)"
        min_max_incr_df = table["Min > Max (Incr.)"].str.extractall(min_max_incr_regex).unstack(level=-1)

        # Populate all rows with no matches with NaN
        min_max_incr_df = min_max_incr_df.reindex(range(n_rows))

        # If less than three matches were found, add columns to bring the shape of the DF to (n_rows, 3)
        while min_max_incr_df.shape[1] < 3:
            min_max_incr_df[min_max_incr_df.shape[1]] = nan

        # A single match refers refers to the parameter increment, which we want on the third column
        # Find the rows with two occurrences of NaN and switch the values of the first and third column
        two_null_subset = min_max_incr_df.isnull().sum(axis=1)[min_max_incr_df.isnull().sum(axis=1) == 2]
        min_max_incr_df.iloc[two_null_subset.index.tolist(), [0, 2]] = \
            min_max_incr_df.iloc[two_null_subset.index.tolist(), [2, 0]].values
        min_max_incr_df.columns = ["Min", "Max", "Incr"]

        tmp_table = pd.concat([name_type_df, min_max_incr_df, table[["Default", "Description"]]], axis=1)
        param_data_df = pd.concat([param_data_df, tmp_table], axis=0, ignore_index=True)

    param_data_df.set_index("Name", inplace=True, drop=False)
    min_mask = param_data_df["Min"] == "?"
    param_data_df.loc[min_mask, "Min"] = nan
    max_mask = param_data_df["Max"] == "?"
    param_data_df.loc[max_mask, "Max"] = nan
    param_data_df[["Default", "Min", "Max", "Incr"]] = \
        param_data_df[["Default", "Min", "Max", "Incr"]].apply(pd.to_numeric)
    save_to_pickle(param_data_df)


def save_to_pickle(data: pd.DataFrame):
    with open(pickle_file_name, 'wb') as f:
        pickle.dump(data, f)


def load_param_df() -> pd.DataFrame:
    pickle_f_exists = os.path.isfile(".//" + pickle_file_name)
    if not pickle_f_exists:
        extract_param_data()
    with open(pickle_file_name, 'rb') as f:
        return pickle.load(f)


pickle_file_name = "parameter_data_from_html.dat"
px4_param_list_url = "https://docs.px4.io/v1.9.0/en/advanced_config/parameter_reference.html"

if __name__ == "__main__":
    extract_param_data()
