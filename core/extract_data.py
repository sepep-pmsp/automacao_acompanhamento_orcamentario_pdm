from openpyxl import load_workbook
import pandas as pd
import os
from .utils import list_files, solve_path
from .config import (ENVIRONMENT, ABA_DADOS_PROD, ABA_DADOS_TEST, 
                    ORIGINAL_DATA_DIR, ACCEPTED_EXTENSIONS, VERBOSE,
                    ROW_INICIAL_DADOS, MAX_ROW_DADOS, ORIGINAL_COLUMNS, 
                    CELULAS_CHECAGEM, EXTRACTED_CSV_NAME)

class Extractor:

    def __init__(self, original_data_dir = ORIGINAL_DATA_DIR, extensions = ACCEPTED_EXTENSIONS, 
                col_mapper = ORIGINAL_COLUMNS, initial_row = ROW_INICIAL_DADOS, final_row = MAX_ROW_DADOS,
                save_extraction=True, verbose=VERBOSE, env = ENVIRONMENT):
        
        self.verbose = verbose

        self.env = env
        self.sheet = self.solve_sheet()
        self.extensions = extensions

        self.data_folder = original_data_dir
        self.original_files = self.list_files()

        #col mapper must be dict in {xl_col : df_col} format
        self.col_mapper = col_mapper
        self.init_row = initial_row
        self.final_row = final_row

        self.save =  save_extraction
        
    def solve_sheet(self):

        if self.env == 'test':
            aba = ABA_DADOS_TEST
        else:
            aba = ABA_DADOS_PROD
        
        if self.verbose:
            print(f'Os dados serão lidos da aba de nome: {aba}')

        return aba

    def list_files(self):

        found_files = []
        for ext in self.extensions:
            found = list_files(folder = self.data_folder, extension=ext)
            found_files.extend(found)

        if self.verbose:
            nom_files_print = '\n'.join(found_files)
            print(f'Os seguintes arquivos de excel foram encontrados e serão lidos: {nom_files_print}')

        return found_files

    def open_xl_sheet(self, file_path):

        #data_only para garantir que nao venham as formulas mas sim os valores
        xl = load_workbook(file_path, data_only=True)
        sheet = xl[self.sheet]

        return sheet
    
    def check_sheet_integrity(self, sheet):
        
        errors = {}
        for cell, valor in CELULAS_CHECAGEM.items():
            if valor not in sheet[cell].value:
                errors[cell] = valor

        if errors:
            if self.verbose:
                print(f'Foram encontrados os seguintes valores fora do padrão: {errors}')
            return True
        return False

    def extract_sheet_range(self, sheet, col_xl):

        init = f'{col_xl}{self.init_row}'
        end = f'{col_xl}{self.final_row}'
        cell_range = sheet[f'{init}:{end}']

        return cell_range

    def parse_cell(self, cell):

        cell = cell[0]
        val = cell.value
        if pd.isnull(val) or val == '':
            return None
        
        return str(val)

    def parse_data(self, cell_range):
        
        #em um primeiro momento vamos pegar tudo como string
        return [self.parse_cell(cell) for cell in cell_range]

    def read_sheet_data(self, sheet):

        check = self.check_sheet_integrity(sheet)
        if check:
            if self.verbose:
                print('Arquivo fora do padrão. Será desconsiderado')
            return pd.DataFrame({col : [] for col in self.col_mapper.values()})

        parsed_data = {}
        for col_xl, col_df in self.col_mapper.items():
            
            cell_range = self.extract_sheet_range(sheet, col_xl)
            col_data = self.parse_data(cell_range)

            parsed_data[col_df] = col_data
        
        return pd.DataFrame(parsed_data)

    def get_secretaria_name_from_file(self, filename):

        splited = os.path.split(filename)
        file = splited[-1]

        secretaria = file.split('_')[0]

        return secretaria

    def drop_empty_rows(self, parsed_df):

        df = parsed_df.copy()

        df.dropna(how='all', inplace=True)

        return df

    def get_periodo(self):

        return self.sheet.split(' ')[-1]

    def extract_report_file(self, filename):

        sheet = self.open_xl_sheet(filename)
        secretaria = self.get_secretaria_name_from_file(filename)

        df = self.read_sheet_data(sheet)
        df = self.drop_empty_rows(df)

        if len(df)<1:
            df.append({'planilha_fora_do_padrao' : 'sim'}, ignore_index=True)
        else:
            df['vazio_ou_fora_do_padrao'] = 'não'

        df['orgao'] = secretaria
        df['arquivo_origem'] = os.path.split(filename)[-1]
        df['periodo'] = self.get_periodo()

        return df

    def extract_all_reports(self):

        dfs = []
        for file in self.original_files:
            dfs.append(self.extract_report_file(file))
        return pd.concat(dfs)

    def __call__(self):

        df = self.extract_all_reports()

        if self.save:
            df_path = EXTRACTED_CSV_NAME
            df.to_csv(df_path, sep=';', encoding='utf-8')

        return df


    


    


    

    
        