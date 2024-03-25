import basedosdados as bd
import pandas as pd
import numpy as np

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
        df = pd.read_csv(f"../data/{table}.csv")

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

        # Fluviometria
        elif table == 'rj-rioaguas.saneamento_drenagem.nivel_reservatorio':
            df = df[['nome_reservatorio', 'data_particao', 'horario', 'altura_agua']]
            df['data_medicao'] = pd.to_datetime(df['data_particao'] + ' ' + df['horario'])
            df['data_medicao'] = pd.to_datetime(df['data_medicao'])
            altura_maxima = {
                "Bandeira": 18,
                "Varnhagen": 21.5,
                "Niteroi": 22.25
            }
            df = df[df['altura_agua'] <= 23]
            df = df.dropna(how="any")
            df['altura_maxima'] = df['nome_reservatorio'].map(altura_maxima)
            df['altura_ocupada'] = df['altura_agua'] / df['altura_maxima'] * 100
            df = df.sort_values('data_medicao').reset_index()
            df = df[['nome_reservatorio', 'data_medicao', 'altura_ocupada']]
        elif table == 'rj-rioaguas.saneamento_drenagem.qualidade_agua':
            df = df[[
                'coleta',
                "data_medicao",
                "ph",
                "temperatura_da_agua",
                "oxigenio_dissolvido",
                "coliformes_totais",
                "nitrogenio_amoniacal",
                "fosforo_total_mg_l",
                "turbidez"
            ]]
            df = df[df['coleta'] == 'Regular']
            df['data_medicao'] = pd.to_datetime(df['data_medicao'], errors='coerce')
            df = df.dropna(subset=['data_medicao'])
            df = df.dropna(how='all')
            colunas = list(df.columns)
            colunas.remove('data_medicao')
            for coluna in colunas:
                df[coluna] = pd.to_numeric(df[coluna], errors='coerce')

            df = df.set_index('data_medicao')
            df = df.interpolate(method='time').reset_index()

            df = df.fillna(df.mean(numeric_only=True))
            pesos = {
                "od": 0.17,
                "coliformes": 0.15,
                "ph": 0.12,
                "temperatura": 0.10,
                "nitrogenio_total": 0.10,
                "fosforo_total": 0.10,
                "turbidez": 0.08,
            }
            df['q_ph_val'] = 100 - 40 * abs(df['ph'] - 7)
            df['q_od_val'] = 93.70 * np.exp(-0.0091 * df['oxigenio_dissolvido'])
            df['q_coliformes_val'] = np.vstack([100 - np.log10(df['coliformes_totais'] + 1)*5, np.zeros(df.shape[0])]).max(axis=0)
            df['q_nitrogenio_total_val'] = np.vstack([100 * np.exp(-0.1 * df['nitrogenio_amoniacal']), np.zeros(df.shape[0])]).max(axis=0)
            df['q_fosforo_total_val'] = np.vstack([100 * np.exp(-0.5 * df['fosforo_total_mg_l']), np.zeros(df.shape[0])]).max(axis=0)
            df['q_turbidez_val'] = np.vstack([100 - df['turbidez'], np.zeros(df.shape[0])]).max(axis=0)
            df['q_temperatura_val'] = 106.43 * np.exp(-((df['temperatura_da_agua'] - 10)**2) / (2 * 5.85**2))
            df['IQA'] = (df['q_ph_val'] ** pesos["ph"]) * \
                        (df['q_od_val'] ** pesos["od"]) * \
                        (df['q_coliformes_val'] ** pesos["coliformes"]) * \
                        (df['q_temperatura_val'] ** pesos["temperatura"]) * \
                        (df['q_nitrogenio_total_val'] ** pesos["nitrogenio_total"]) * \
                        (df['q_fosforo_total_val'] ** pesos["fosforo_total"]) * \
                        (df['q_turbidez_val'] ** pesos["turbidez"])
            df = df.sort_values('data_medicao')
            df = df.set_index('data_medicao')
            df = df.resample('d').mean()
            df = df.dropna(how='all').reset_index()

        return df
