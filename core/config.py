import os
from .utils import solve_dir, solve_path


VERBOSE = True

ORIGINAL_DATA_DIR = solve_dir('original_data')
GENERATED_DATA_DIR = solve_dir('generated_data')

#ENVIRONMENT = os.environ.get('ENVIRONMENT') or 'test'
ENVIRONMENT = 'prod'


ABA_DADOS_TEST = 'Monitoramento 1trim_2022'
ABA_DADOS_PROD = 'EXE_acum_1trim2023'

ACCEPTED_EXTENSIONS = ('.xlsx', )

ROW_INICIAL_DADOS = 8
MAX_ROW_DADOS = 700
ORIGINAL_COLUMNS = {
    'B' : 'meta',
    'C' : 'iniciativa',
    'D' :'dotacao_orcamentaria',
    'E' : 'valor_empenhado_dotacao',
    'F' : 'valor_liquidado_dotacao',
    'I' : 'processo_sei',
    'J' : 'valor_empenhado_sei',
    'K' : 'valor_liquidado_sei',
    'N' : 'nota_de_empenho',
    'O' : 'valor_empenhado_nota',
    'P' : 'valor_liquidado_nota'
}

COLS_NUMERICAS = (
    'valor_empenhado_dotacao',
    'valor_liquidado_dotacao',
    'valor_empenhado_sei',
    'valor_liquidado_sei',
    'valor_empenhado_nota',
    'valor_liquidado_nota'
)

CELULAS_CHECAGEM = {
    f'D{ROW_INICIAL_DADOS-1}' : 'Dotação Orçamentária',
    f'I{ROW_INICIAL_DADOS-1}' : 'Processo SEI',
    f'N{ROW_INICIAL_DADOS-1}' : 'Nota de Empenho'
}

EXTRACTED_CSV_NAME = solve_path('extracao_original.csv', parent=GENERATED_DATA_DIR)

#PADROES PARA CHECAGENS

NUM_CHAR_DOTACAO = 35
NUM_CHAR_SEI = 16

FONTES_DOTACAO = {'00', '01', '02', '03', '04', '05', 
                '06', '08', '09', '10', '11', '12', '21'}

FINAL_DATAFILE_NAME = solve_path('dados_limpos.xlsx', parent=GENERATED_DATA_DIR)
REPORT_NAME = solve_path('relatoro_completo.xlsx',  parent=GENERATED_DATA_DIR)