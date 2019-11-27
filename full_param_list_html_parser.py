import requests
from bs4 import BeautifulSoup
import pandas as pd
import pickle


def parse_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    return (parse_html_table(table) for table in soup.find_all('table'))


def parse_html_table(table):
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


def save_to_pickle(data_iter: iter):
    with open(pickle_file_name, 'wb') as f:
        for data_element in data_iter:
            pickle.dump(data_element, f)


def load_from_pickle():
    with open(pickle_file_name, 'rb') as f:
        while True:
            try:
                yield pickle.load(f)
            except EOFError:
                break


pickle_file_name = "parameter_data_from_html.dat"
if __name__ == "__main__":
    px4_url = "https://docs.px4.io/v1.9.0/en/advanced_config/parameter_reference.html"
    tables = parse_url(px4_url)
    save_to_pickle(tables)

