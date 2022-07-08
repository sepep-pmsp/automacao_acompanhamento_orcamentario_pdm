#COMO A PRINCIPIO VAMOS CRIAR APENAS .CSVS, O LOADER É BEM SIMPLES

from .config import FINAL_DATAFILE_NAME, REPORT_NAME, ORIGINAL_COLUMNS
from .transform_data import Transformer

#por enquanto vamos rodar apenas com as configuraçoes padrão do transformer
class Loader:

    def __init__(self, data_file_name = FINAL_DATAFILE_NAME,
                        report_file_name = REPORT_NAME):

        self.transform = Transformer()
        self.data_file = data_file_name
        self.report_file = report_file_name

    def save_file(self, df, report = False):

        if report:
            df.to_excel(self.report_file)
        else:
            columns = [col+'_final' for col in ORIGINAL_COLUMNS.values()]
            columns = columns + ['checagem_final', 'orgao', 'periodo']
            df = df[columns]

            df.to_excel(self.data_file)
            
        
    def __call__(self):

        df = self.transform()

        self.save_file(df, report=True)
        self.save_file(df, report=False)