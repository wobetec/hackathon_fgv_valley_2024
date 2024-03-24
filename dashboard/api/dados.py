import basedosdados as bd
import pandas as pd

MAP_BOUNDS = {"west": -43.800734, "east": -43.094862, "south": -23.088019, "north": -22.795882}


class Datalake:

    ID = 'dados-rio-417800'

    TABLES_INFO = pd.DataFrame([
        {'Tabela': 'datario.adm_central_atendimento_1746.chamado'},
        {'Tabela': 'datario.dados_mestres.bairro'},
        {'Tabela': 'rj-cor.adm_cor_comando.ocorrencias'},
        {'Tabela': 'rj-cor.adm_cor_comando.procedimento_operacional_padrao'},
        {'Tabela': 'rj-cor.clima_fluviometro.lamina_agua_inea'},

        {'Tabela': 'rj-cor.clima_pluviometro.estacoes_alertario'},
        {'Tabela': 'rj-cor.clima_pluviometro.estacoes_cemaden'},
        {'Tabela': 'rj-cor.clima_pluviometro.estacoes_inea'},
        {'Tabela': 'rj-cor.clima_pluviometro.estacoes_websirene'},

        {'Tabela': 'rj-cor.clima_pluviometro.taxa_precipitacao_alertario_5min'},
        {'Tabela': 'rj-cor.clima_pluviometro.taxa_precipitacao_cemaden'},
        {'Tabela': 'rj-cor.clima_pluviometro.taxa_precipitacao_inea'},
        {'Tabela': 'rj-cor.clima_pluviometro.taxa_precipitacao_websirene'},

        {'Tabela': 'rj-cor.clima_radar.taxa_precipitacao_guaratiba'},
        {'Tabela': 'rj-cor.dados_mestres.h3_grid_res8'},
        {'Tabela': 'rj-rioaguas.dados_mestres.sub_bacias'},
        {'Tabela': 'rj-rioaguas.saneamento_drenagem.nivel_lamina_agua_via'},
        {'Tabela': 'rj-rioaguas.saneamento_drenagem.nivel_reservatorio'},
        {'Tabela': 'rj-rioaguas.saneamento_drenagem.ponto_supervisionado_alagamento'},
        {'Tabela': 'rj-rioaguas.saneamento_drenagem.qualidade_agua'},

        {'Tabela': 'datario.clima_pluviometro.taxa_precipitacao_alertario'},
    ])

    def __new__(cls, *args, **kwargs):
        raise Exception("This class can't be instantiated")

    @classmethod
    def get(self, table):
        """
        Retorna os dados de uma tabela. Posteriormente o objetivo é que ele se conecte 
        com o bigquery e já haja uma função de tratamento para cada dado
        """
        df = pd.read_csv(f"C:\Code\MyRepos\hackathon_fgv_valley_2024\data\{table}.csv")

        # Dados de estação pluviométrica/Fluviométrica
        if table == 'rj-cor.clima_pluviometro.estacoes_alertario':
            df = df[['id_estacao', 'estacao', 'latitude', 'longitude', 'endereco', 'situacao']]
        elif table == 'rj-cor.clima_pluviometro.estacoes_cemaden':
            df = df.dropna()
        elif table == 'rj-cor.clima_pluviometro.estacoes_inea':
            df = df[['id_estacao', 'estacao', 'tipo_estacao', 'regiao_hidrografica', 'bacia',
       'latitude', 'longitude']]
        elif table == 'rj-cor.clima_pluviometro.estacoes_websirene':
            pass

        # Taxas de precipitação
        elif table == 'rj-cor.clima_pluviometro.taxa_precipitacao_alertario_5min':
            df = df[['id_estacao', 'data_medicao', 'acumulado_chuva_15min']]
        elif table == 'rj-cor.clima_pluviometro.taxa_precipitacao_cemaden':
            df = df[['id_estacao', 'data_medicao', 'acumulado_chuva_10_min']]
            df = df.rename(columns={'acumulado_chuva_10_min': 'acumulado_chuva_10min'})
        elif table == 'rj-cor.clima_pluviometro.taxa_precipitacao_inea':
            df = df[['id_estacao', 'data_medicao', 'acumulado_chuva_15_min']]
            df = df.rename(columns={'acumulado_chuva_15_min': 'acumulado_chuva_15min'})
        elif table == '':
            df['data_medicao'] = pd.to_datetime(df['data_particao'] + ' ' + df['horario'])
            df = df[['id_estacao', 'data_medicao', 'acumulado_chuva_15_min']]
            df = df.rename(columns={'acumulado_chuva_15_min': 'acumulado_chuva_15min'})
        
        return df
