import pandas as pd
import logging
class ExcelWriter:
    def __init__(self, output_path):
        self.output_path = output_path
        self.writer = pd.ExcelWriter(self.output_path, engine='xlsxwriter')

    def new_sheet(self, df, sheet_name, index=False):
        df.to_excel(self.writer, sheet_name=sheet_name, index=index)
        worksheet = self.writer.sheets[sheet_name]  # pull worksheet object
        for idx, col in enumerate(df):  # loop through all columns
            series = df[col]
            max_len = max((
                series.astype(str).map(len).max(),  # len of largest item
                len(str(series.name))  # len of column name/header
                )) + 1  # adding a little extra space
            worksheet.set_column(idx, idx, max_len)  # set column width

    def export_results(self):
        self.writer.close()
        