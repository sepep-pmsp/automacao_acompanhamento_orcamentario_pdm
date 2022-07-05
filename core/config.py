import os
from .utils import solve_dir


VERBOSE = True

ORIGINAL_DATA_DIR = solve_dir('original_data')
GENERATED_DATA_DIR = solve_dir('generated_data')

ENVIRONMENT = os.environ.get('ENVIRONMENT') or 'test'


ABA_DADOS_TEST = 'Monitoramento 1trim_2022'
ABA_DADOS_PROD = 'Monitoramento 2trim_2022'

ACCEPTED_EXTENSIONS = ('.xlsx', )

ROW_INICIAL_DADOS = 7
MAX_ROW_DADOS = 1000
ORIGINAL_COLUMNS = {
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

CELULAS_CHECAGEM = {
    'D6' : 'Dotação Orçamentária',
    'I6' : 'Processo SEI',
    'N6' : 'Nota de Empenho'
}