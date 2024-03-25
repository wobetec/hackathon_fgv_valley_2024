from operator import index
import basedosdados as bd
import pandas as pd
import numpy as np
import datetime
import os
import json
from time import perf_counter

MAP_BOUNDS = {"west": -43.800734, "east": -43.094862, "south": -23.088019, "north": -22.795882}
CACHE_DIR = "./cache"
TIMEOUT_FILE = os.path.join(CACHE_DIR, 'timeout.json')
DEFAULT_TIMEOUT = 10000 * 60


if not os.path.exists(CACHE_DIR):
    os.mkdir(CACHE_DIR)


class Datalake:

    ID = 'dados-rio-417800'

    TABLES_COLUMNS = {
        'datario.adm_central_atendimento_1746.chamado':{
            'colunas': [
            ],
            'timeout': DEFAULT_TIMEOUT
        },
        'datario.dados_mestres.bairro':{
            'colunas': [
            ],
            'timeout': DEFAULT_TIMEOUT
        },
        'rj-cor.adm_cor_comando.ocorrencias':{
            'colunas': [
            ],
            'timeout': DEFAULT_TIMEOUT
        },
        'rj-cor.adm_cor_comando.procedimento_operacional_padrao':{
            'colunas': [
            ],
            'timeout': DEFAULT_TIMEOUT
        },
        'rj-cor.clima_fluviometro.lamina_agua_inea':{
            'colunas': [
            ],
            'timeout': DEFAULT_TIMEOUT
        },
        'rj-cor.clima_pluviometro.estacoes_alertario':{
            'colunas': [
                'id_estacao',
                'estacao',
                'latitude',
                'longitude',
                'endereco',
                'situacao'
            ],
            'timeout': DEFAULT_TIMEOUT
        },
        'rj-cor.clima_pluviometro.estacoes_cemaden':{
            'colunas': [
                'id_estacao',
                'estacao',
                'latitude',
                'longitude',
            ],
            'timeout': DEFAULT_TIMEOUT
        },
        'rj-cor.clima_pluviometro.estacoes_inea':{
            'colunas': [
                'id_estacao',
                'estacao',
                'tipo_estacao',
                'regiao_hidrografica',
                'bacia',
                'latitude',
                'longitude'
            ],
            'timeout': DEFAULT_TIMEOUT
        },
        'rj-cor.clima_pluviometro.estacoes_websirene':{
            'colunas': [
                'id_estacao',
                'estacao',
                'latitude',
                'longitude',
            ],
            'timeout': DEFAULT_TIMEOUT
        },
        'rj-cor.clima_pluviometro.taxa_precipitacao_alertario_5min':{
            'colunas': [
                'id_estacao',
                'data_medicao',
                'acumulado_chuva_15min'
            ],
            'timeout': DEFAULT_TIMEOUT
        },
        'rj-cor.clima_pluviometro.taxa_precipitacao_cemaden':{
            'colunas': [
                'id_estacao',
                'data_medicao',
                'acumulado_chuva_10_min'
            ],
            'timeout': DEFAULT_TIMEOUT
        },
        'rj-cor.clima_pluviometro.taxa_precipitacao_inea':{
            'colunas': [
                'id_estacao',
                'data_medicao',
                'acumulado_chuva_15_min'
            ],
            'timeout': DEFAULT_TIMEOUT
        },
        'rj-cor.clima_pluviometro.taxa_precipitacao_websirene':{
            'colunas': [
                'id_estacao',
                'horario',
                'data_particao',
                'acumulado_chuva_15_min'
            ],
            'timeout': DEFAULT_TIMEOUT
        },
        'rj-cor.clima_radar.taxa_precipitacao_guaratiba':{
            'colunas': [
            ],
            'timeout': DEFAULT_TIMEOUT
        },
        'rj-cor.dados_mestres.h3_grid_res8':{
            'colunas': [
            ],
            'timeout': DEFAULT_TIMEOUT
        },
        'rj-rioaguas.dados_mestres.sub_bacias':{
            'colunas': [
            ],
            'timeout': DEFAULT_TIMEOUT
        },
        'rj-rioaguas.saneamento_drenagem.nivel_lamina_agua_via':{
            'colunas': [
            ],
            'timeout': DEFAULT_TIMEOUT
        },
        'rj-rioaguas.saneamento_drenagem.nivel_reservatorio':{
            'colunas': [
                'nome_reservatorio',
                'data_particao',
                'horario',
                'altura_agua'
            ],
            'timeout': DEFAULT_TIMEOUT
        },
        'rj-rioaguas.saneamento_drenagem.ponto_supervisionado_alagamento':{
            'colunas': [
            ],
            'timeout': DEFAULT_TIMEOUT
        },
        'rj-rioaguas.saneamento_drenagem.qualidade_agua':{
            'colunas': [
                'coleta',
                'data_medicao',
                'ph',
                'temperatura_da_agua',
                'oxigenio_dissolvido',
                'coliformes_totais',
                'nitrogenio_amoniacal',
                'fosforo_total_mg_l',
                'turbidez'
            ],
            'timeout': DEFAULT_TIMEOUT
        },
        'datario.clima_pluviometro.taxa_precipitacao_alertario':{
            'colunas': [
            ],
            'timeout': DEFAULT_TIMEOUT
        },
    }

    def __new__(cls, *args, **kwargs):
        raise Exception("This class can't be instantiated")
    
    @classmethod
    def __exists(cls, table):
        timeout = cls.TABLES_COLUMNS[table]['timeout']
        if not os.path.exists(TIMEOUT_FILE):
            return False
        if not os.path.exists(os.path.join(CACHE_DIR, table+'.csv')):
            return False
        with open(TIMEOUT_FILE, 'r') as f:
            data = json.load(f)
            time = data[table]
            if perf_counter() - time < timeout:
                return True
        return False
    
    @classmethod
    def __save(cls, table, df):
        df.to_csv(os.path.join(CACHE_DIR, table+'.csv'), index=False)
        try:
            with open(TIMEOUT_FILE, "r") as f:
                data = json.load(f)
        except:
            data = {}
        data[table] = perf_counter()
        with open(TIMEOUT_FILE, 'w') as f:
            json.dump(data, f)
    
    @classmethod
    def __load(cls, table):
        df = pd.read_csv(os.path.join(CACHE_DIR, table+'.csv'))
        return df

    @classmethod
    def __get(cls, table):
        if len(cls.TABLES_COLUMNS[table]) == 0:
            return pd.DataFrame()
        if cls.__exists(table):
            return cls.__load(table)
        query = f"SELECT {', '.join(cls.TABLES_COLUMNS[table]['colunas'])} FROM {table}"
        df = bd.read_sql(query, billing_project_id=cls.ID)
        cls.__save(table, df)
        return df

    @classmethod
    def get(cls, table):
        """
        Retorna os dados de uma tabela já previamente tratados  
        """

        # Para garantir que não será feita uma query gigante sem dados
        df = cls.__get(table)

        # Tratamento especial para algumas tabelas
        if table == 'rj-cor.clima_pluviometro.taxa_precipitacao_alertario_5min':
            df['data_medicao'] = pd.to_datetime(df['data_medicao'])

        elif table == 'rj-cor.clima_pluviometro.taxa_precipitacao_cemaden':
            df['acumulado_chuva_15min'] = (df['acumulado_chuva_10_min'] / 2).rolling(3).sum()
            df['data_medicao'] = pd.to_datetime(df['data_medicao'])
            df = df.dropna(subset=['data_medicao']).sort_values('data_medicao')
            df = df[['id_estacao', 'data_medicao', 'acumulado_chuva_15min']]

        elif table == 'rj-cor.clima_pluviometro.taxa_precipitacao_inea':
            df = df.rename(columns={'acumulado_chuva_15_min': 'acumulado_chuva_15min'})

        elif table == 'rj-cor.clima_pluviometro.taxa_precipitacao_websirene':
            df['data_medicao'] = pd.to_datetime(df['data_particao'] + ' ' + df['horario'])
            df = df.rename(columns={'acumulado_chuva_15_min': 'acumulado_chuva_15min'})
            df = df[['id_estacao', 'data_medicao', 'acumulado_chuva_15min']]

        elif table == 'rj-rioaguas.saneamento_drenagem.nivel_reservatorio':
            df['data_medicao'] = pd.to_datetime(df['data_particao'] + ' ' + df['horario'])
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

        elif table == 'rj-rioaguas.saneamento_drenagem.nivel_lamina_agua_via':
            estacoes = {
                1: "Catete",
                2: "Bangu - Rua da Feira",
                3: "Bangu - Rua do Açudes",
                4: "Rio Maracanã - Visc Itamarati",
                5: "Itanhangá",
                6: "Bangu - Av Santa Cruz",
                7: "Lagoa",
                8: "Rio Maracanã - R: Uruguai",
            }
            df['id_estacao'] = df['primary_key'].str[0]
            df['id_estacao'] = df['id_estacao'].astype(int)
            df['estacao'] = df['id_estacao'].map(estacoes)
            df['data_medicao'] = pd.to_datetime(df['data_particao'] + ' ' + df['horario'])

            df = df.sort_values('data_medicao').reset_index()
            df = df[['estacao', 'data_medicao', 'altura_agua']]
        

        return df
