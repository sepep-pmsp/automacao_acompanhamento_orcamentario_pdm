from core.load_data import Loader

if __name__ == "__main__":

    print('Iniciando ETL')
    load = Loader()
    load()
    print('ETL finalizado')