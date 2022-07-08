import os
import pandas as pd
from .extract_data import Extractor
from .config import (VERBOSE, NUM_CHAR_DOTACAO,
                    NUM_CHAR_SEI, FONTES_DOTACAO, 
                    EXTRACTED_CSV_NAME, ORIGINAL_COLUMNS,
                    COLS_NUMERICAS)


class LengthChecker:

    def __init__(self, num_char_dotacao=NUM_CHAR_DOTACAO, num_char_sei=NUM_CHAR_SEI):

        self.num_char_dotacao = num_char_dotacao
        self.num_char_sei = num_char_sei

    def aux_len_val(self, val, length):

        if pd.isnull(val) or val=='':
            return 'vazio'
        
        teste = len(val) == length

        if teste:
            return 'ok'
        return 'errado'

    def len_sei(self, df, iter):

        col = 'processo_sei'
        if iter == 'final':
            col = col + '_final'
        new_col = f'check_tamanho_{col}'
        df[new_col] = df[col].apply(self.aux_len_val, args= [self.num_char_sei])

    def len_dotacao(self, df, iter):

        col = 'dotacao_orcamentaria'
        if iter == 'final':
            col = col + '_final'
        new_col = f'check_tamanho_{col}'

        df[new_col] = df[col].apply(self.aux_len_val, args= [self.num_char_dotacao])


    def aux_check_empenho(self, val):

        if pd.isnull(val) or val=='':
            return 'vazio'

        splited = val.split('/')
        ano = splited[-1]
        teste = len(ano)==4

        if teste:
            return 'ok'
        return 'errado'

    def len_empenho(self, df, iter):

        col = 'nota_de_empenho'
        if iter == 'final':
            col = col + '_final'
        new_col = f'check_tamanho_{col}'

        df[new_col] = df[col].apply(self.aux_check_empenho)


    def __call__(self, df, iter):

        assert iter in ('inicial', 'final'), ValueError(f'Iter must be in (inicial, final)')
        df = df.copy()

        self.len_sei(df, iter)
        self.len_dotacao(df, iter)
        self.len_empenho(df, iter)

        return df


class Transformer:

    def __init__(self, df = None, original_columns = tuple(ORIGINAL_COLUMNS.values()),
                df_path=EXTRACTED_CSV_NAME,fontes = FONTES_DOTACAO, 
                cols_numericas= COLS_NUMERICAS, verbose=VERBOSE):

        self.verbose = verbose
        self.df_path = df_path
        self.original_columns = original_columns

        self.fontes_dotacao = fontes
        self.cols_numericas = cols_numericas

        self.length_check = LengthChecker()
        self.df = self.pipeline_load_data(df)

    def pipeline_load_data(self, df):

        if df is None:
            df = self.get_df(self.df_path)

        self.drop_unnamed(df)
        self.check_df_columns(df)

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
        for col in df.columns:
            df[col] = df[col].apply(self.solve_nan)
        
        return df

    def assert_col(sef, col, df):

        assert col in df.columns, ValueError(f'Coluna {col} não encontrada no dataframe')

    def clean_sei_val(self, val):
        
        val = val.replace("'", '')
        val = val.replace('.', '')
        val = val.replace('/', '')
        val = val.replace('-', '')
        val = val.replace(" ", '')

        return val

    def clean_sei(self, df):

        col = 'processo_sei'
        self.assert_col(col, df)

        df[col+'_final'] = df[col].apply(self.clean_sei_val)

    def aux_dados_juntos_dotacao(self, val):

        splited = val.split('.')
        #item que da erro é a posição -2
        #esta errado se ele tem 7 caracteres
        if len(splited[-2]) != 7:
            return val
        item_arrumado = splited[-3] + splited[-2]

        comeco = '.'.join(splited[:-3])
        final = splited[-1]

        return comeco + '.' + item_arrumado + '.' + final
        
    
    def clean_dotacao_val(self, val):

        val = val.replace('/', '')
        val = val.replace("'", '')
        val = val.replace(" ", '')

        if len(val)<1:
            return val
        val = self.aux_dados_juntos_dotacao(val)

        return val

    def clean_dotacao(self, df):

        col = 'dotacao_orcamentaria'
        self.assert_col(col, df)

        df[col+'_final'] = df[col].apply(self.clean_dotacao_val)

    def clean_empenho(self, df):

        col = 'nota_de_empenho'
        self.assert_col(col, df)

        df[col+'_final'] = df[col].apply(lambda x: x.replace('.', '').\
                                        replace("'", "").replace(" ", ""))

    def clean_pipeline(self, df = None):

        if df is None:
            df = self.df
        
        self.clean_dotacao(df)
        self.clean_sei(df)
        self.clean_empenho(df)

        return df

    def _aux_fonte_dotacao(self, val):

        if val == '' or pd.isnull(val):
            return 'vazio'
        
        splited = val.split('.')
        final = splited[-1]

        teste = final in self.fontes_dotacao

        if teste:
            return 'ok'
        return 'errado'

    def check_fonte_dotacao(self, df):

        col = 'dotacao_orcamentaria'
        self.assert_col(col, df)

        df['check_fonte_dotacao'] = df[col].apply(self._aux_fonte_dotacao)


        return df


    def final_checks_colunas(self, df = None):

        if df is None:
            df = self.df
        
        df = self.length_check(df, iter='final')
        df = self.check_fonte_dotacao(df)

        return df

    def aux_final_check_linha(self, row):

        for col in ('dotacao_orcamentaria', 'nota_de_empenho', 'processo_sei'):
            check_tamanho = f'check_tamanho_{col}_final'
            if row[check_tamanho] == 'errado':
                return 'erro'
        else:
            if row['check_fonte_dotacao'] == 'errado':
                return 'erro'
            return 'ok'

    def check_final_linha(self, df= None):

        if df is None:
            df = self.df
        
        df['checagem_final'] = df.apply(self.aux_final_check_linha,
                                axis=1)

        return df

    def str_to_number(self, val):

        if pd.isnull(val) or val == '':
            return None
        
        val = str(val)

        if 'n/a' in val.lower():
            return None

        #caso de estar formatado como dinheiro
        val = val.replace('R$', '')
        #retirar os pontos de milhar
        if ',' in val and '.' in val:
            val = val.replace('.', '')
            val = val.replace('.', ',')
        if val.count('.') > 1:
            val = val.replace('.', '')

        val = val.replace(',', '.')

        #checagem final para ver se o valor ficou vazio
        val = val.replace(' ', '')
        val = val.replace('-', '')
        if val.encode('utf-8') == b'\xc2\xa0':
            return None
        if val == '':
            return None
        try:
            return float(val)
        except ValueError:
            print(f'Valor não previsto: {val.encode("utf-8")}')


    def convert_to_number(self, df):

        if df is None:
            df = self.df
        
        for col in self.cols_numericas:
            df[f'{col}_final'] = df[col].apply(self.str_to_number)

        return df


    def __call__(self, df=None):

        if df is None:
            df = self.df

        df = df.copy()
        
        df = self.clean_pipeline(df)
        df = self.final_checks_colunas(df)
        df = self.check_final_linha(df)
        df = self.convert_to_number(df)

        return df

        

    

    

    




