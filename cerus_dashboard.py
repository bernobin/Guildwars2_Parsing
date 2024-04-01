from PARSING.Cerus_Parser import CerusParser
from pathlib import Path
import pandas as pd

CSV_FILE = Path.cwd() / 'Outputs' / 'Cerus.csv'


def dash_example():
    try:
        df = pd.read_csv(CSV_FILE)

        c = CerusParser()
        c.generate_dash(df)

    except FileNotFoundError:
        print('csv file needs to be generated first. Please run main.py and select Cerus.')

    except Exception as e:
        print(f'{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}')


if __name__ == '__main__':
    dash_example()
