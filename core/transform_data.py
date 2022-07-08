import os
import pandas as pd
from .extract_data import Extractor
from .config import (VERBOSE, NUM_CHAR_DOTACAO, FINAL_CSV_NAME,
                    NUM_CHAR_SEI, FONTES_DOTACAO, 
                    EXTRACTED_CSV_NAME, ORIGINAL_COLUMNS, REPORT_NAME)


class LengthChecker:

    def __init__(self, num_char_dotacao=NUM_CHAR_DOTACAO, num_char_sei=NUM_CHAR_SEI):

        self.num_char_dotacao = num_char_dotacao
        self.num_char_sei = num_char_sei

    def len_sei(self, df, iter):

        df[f'check_tamanho_sei{iter}'] = df[f'processo_sei{iter}'].str.len() == self.num_char_sei

    def len_dotacao(self, df, iter):

        df[f'check_tamanho_dotacao{iter}'] = df[f'dotacao_orcamentaria{iter}'].str.len() == self.num_char_dotacao

    def aux_check_empenho(self, val):

        splited = val.split('/')
        ano = splited[-1]
        return len(ano)==4

    def len_empenho(self, df, iter):

        df[f'check_tamanho_empenho{iter}'] = df[f'nota_de_empenho{iter}'].apply(self.aux_check_empenho)


    def __call__(self, df, iter):

        assert iter in ('inicial', 'final'), ValueError(f'Iter must be in (inicial, final)')
        df = df.copy()

        iter = '_' + iter

        self.len_sei(df, iter)
        self.len_dotacao(df, iter)
        self.len_empenho(df, iter)

        return df



class Transformer:

    def __init__(self, df = None, original_columns = tuple(ORIGINAL_COLUMNS.values()),
                df_path=EXTRACTED_CSV_NAME, save = True, filename = FINAL_CSV_NAME,
                report_name = REPORT_NAME, verbose=VERBOSE):

        self.verbose = verbose
        self.df_path = df_path
        self.original_columns = original_columns

        self.save = save
        self.final_csv_path = filename
        self.report_name = report_name
        self.length_check = LengthChecker()
        self.df = self.pipeline_load_data(df)

    def pipeline_load_data(self, df):

        if df is None:
            df = self.get_df(self.df_path)

        self.drop_unnamed(df)
        self.check_df_columns(df)
        self.save_original_data(df)

        df = self.solve_all_nan(df)
        df = self.length_check(df, iter='inicial')

        return df

    def drop_unnamed(self, df):

        for col in df.columns:
            if col.startswith('Unnamed:'):
                df.drop(col, axis=1, inplace=True)

    def get_df(self, df_path):

        if not os.path.exists(df_path):
            if self.verbose:
                print(f'Arquivo {df_path} não encontrado. Extraindo dados novamente')
            self.extract = Extractor(verbose=self.verbose)
            df = self.extract()

        else:
            df = pd.read_csv(df_path, sep=';', encoding='utf-8')
        
        return df

    def check_df_columns(self, df):

        cols = set(self.original_columns)
        cols_df = set(df.columns)

        assert not (cols - cols_df), ValueError(f'Colunas fora do padrão: {cols_df}')

    def solve_nan(self, val):

        if pd.isnull(val):
            return ''

        return str(val)

    def solve_all_nan(self, df):

        df = df.copy()
        df = df.apply(self.solve_nan)
        
        return df

    def save_original_data(self, df):

        for col in self.original_columns:
            
            df[f'{col}_inicial'] = df[col]


    def clean_sei_val(self, val):
        
        val = val.replace('.', '')
        val = val.replace('/', '')

        return val

    def aux_dados_juntos_dotacao(self, val):

        return val
    
    def clean_dotacao_val(self, val):

        val = val.replace('.', '')
        val = val.replace('/', '')

    def clean_pipeline(self):

        pass

    

    

    




