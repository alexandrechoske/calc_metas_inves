import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from unidecode import unidecode

# Configurações da página
st.set_page_config(layout="wide", page_title='Calculadora Meta Dividendos', initial_sidebar_state='collapsed')

# Funções auxiliares
def remove_acentos(text):
    return unidecode(text)

def tableDataText(table):    
    def rowgetDataText(tr, coltag='td'):        
        return [td.get_text(strip=True) for td in tr.find_all(coltag)]    
    rows = []
    trs = table.find_all('tr')
    headerow = rowgetDataText(trs[0], 'th')
    if headerow:
        rows.append(headerow)
        trs = trs[1:]
    for tr in trs:
        rows.append(rowgetDataText(tr, 'td'))
    return rows

def extrair_tabela(table):
    list_table = tableDataText(table)
    dftable = pd.DataFrame(list_table[1:], columns=list_table[0])
    return dftable.rename(columns=lambda x: remove_acentos(x.lower().replace(' ', '_').replace('/', '_').replace('.', '_')))


headers = {
  'authority': 'www.fundamentus.com.br',
  'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
  'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
  'cache-control': 'max-age=0',
  'content-type': 'application/x-www-form-urlencoded',
  'cookie': 'PHPSESSID=28feeb76076d04aae6bbf7704d98a757; __utmc=138951332; nv_int=1; privacidade=1; __utmz=138951332.1683840672.9.3.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __utma=138951332.479766388.1682600142.1684016451.1684090807.14; __utmt=1; __cf_bm=OQE6uW6REu5Le.eMg5F0u.m3GGGjQ6fmI365pBskgMI-1684090806-0-AVeJL+N/HrXgKXE8YGxNYc1aFsBPSd/93Yvvye0/3PJWvcztHlfncrgh7HggD4VhLir6OeWUqcdtFm8JhulOpn0FMebb8+7aKIBnzuaLpxsi; __utmb=138951332.7.10.1684090807',
  'origin': 'https://www.fundamentus.com.br',
  'referer': 'https://www.fundamentus.com.br/fii_buscaavancada.php',
  'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'sec-fetch-dest': 'document',
  'sec-fetch-mode': 'navigate',
  'sec-fetch-site': 'same-origin',
  'sec-fetch-user': '?1',
  'upgrade-insecure-requests': '1',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
}

# Requests para extrair dados das tabelas de FIIs e Ações
def obter_dados_fiis():

    url = "https://www.fundamentus.com.br/fii_resultado.php"
    payload = 'ffo_y_min=&ffo_y_max=&divy_min=&divy_max=&pvp_min=&pvp_max=&mk_cap_min=&mk_cap_max=&qtd_imoveis_min=&qtd_imoveis_max=&preco_m2_min=&preco_m2_max=&aluguel_m2_min=&aluguel_m2_max=&cap_rate_min=&cap_rate_max=&vacancia_min=&vacancia_max=&setor=&negociada=ON&submit='
    response = requests.request("POST", url, headers=headers, data=payload)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.select('#tabelaResultado')[0]

    tableFiis = extrair_tabela(table)

    return tableFiis

def obter_dados_acoes():

    url = "https://www.fundamentus.com.br/resultado.php"
    payload = 'pl_min=&pl_max=&pvp_min=&pvp_max=&psr_min=&psr_max=&divy_min=&divy_max=&pativos_min=&pativos_max=&pcapgiro_min=&pcapgiro_max=&pebit_min=&pebit_max=&fgrah_min=&fgrah_max=&firma_ebit_min=&firma_ebit_max=&firma_ebitda_min=&firma_ebitda_max=&margemebit_min=&margemebit_max=&margemliq_min=&margemliq_max=&liqcorr_min=&liqcorr_max=&roic_min=&roic_max=&roe_min=&roe_max=&liq_min=&liq_max=&patrim_min=&patrim_max=&divliq_min=&divliq_max=&tx_cresc_rec_min=&tx_cresc_rec_max=&valor_mercado_min=&valor_mercado_max=&setor=&negociada=ON&submit='
    response = requests.request("POST", url, headers=headers, data=payload)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table')
    tableEmpresas = extrair_tabela(table)

    return tableEmpresas

# Função para calcular a meta de dividendos
def calcular_meta_dividendos(df, meta):
    df['meta_mensal_div'] = meta
    df['valor_aprox_meta'] = df['meta_mensal_div'] / (df['dividendo_mensal'] / 100)
    df['qtde_cotas_meta'] = df['valor_aprox_meta'] / df['cotacao']
    return df

# Página inicial
if st.button('Começar'):
    # Seção de filtros
    st.header("Calculadora de Metas de Dividendos")
    col1, col2 = st.columns(2)
    with col1:
        st.write("Essa calculadora ajuda a calcular as metas de dividendos para investimentos em ações.")
        st.image('https://i.imgur.com/7G6f8Zv.png', caption='Imagem de fundo')
    with col2:
        st.markdown('Você pode usar essa ferramenta para calcular suas metas de dividendos e planificar seu investimento.')
        
    # Seção de botões
    st.header("Ações")
    st.button('Ações')
    
    st.header("Metas de Dividendos")
    st.button('Metas de Dividendos')

# Página de resultados
else:
    # Interface do Streamlit
    st.title("Simulação de Metas de Dividendos")

    # Seção de filtros
    st.sidebar.header("Filtros")
    
    # Seção de filtros na sidebar
    with st.sidebar.form(key='formconfigs'):
        meta_dividendo = st.number_input('Meta mensal dividendos', min_value=0.0, step=100.0)
        qtde_cotas_aperfeiçoar_meta = st.number_input('Cotas Mensais para Atingir a Meta', min_value=1)

        df_acoes = obter_dados_acoes()

        # Limpar e converter colunas relevantes
        df_acoes['div_yield'] = df_acoes['div_yield'].str.replace('%', '').str.replace(',', '.').astype(float)
        df_acoes['dividendo_mensal'] = df_acoes['div_yield'] / 12  # Simulação de dividendo mensal
        df_acoes['cotacao'] = df_acoes['cotacao'].str.replace(',', '.').astype(float)

        # Filtro para escolher ações
        acoes_opcoes = df_acoes['papel'].unique().tolist()
        acoes_selecionadas = st.multiselect("Selecione as Ações", acoes_opcoes, default=['ABEV3'])

        # Botão de submissão
        submit_button = st.form_submit_button(label="Calcular")

    if submit_button:
        # Filtrar o DataFrame com base nas ações selecionadas
        df_acoes_filtradas = df_acoes[df_acoes['papel'].isin(acoes_selecionadas)]
        
        # Criação de tabelas para cada ação
        for i, acao in enumerate(acoes_selecionadas):
            with st.expander(f"Resultados: {acao}"):
                # Informações gerais
                dy_mensal = df_acoes_filtradas[df_acoes_filtradas['papel'] == acao]['dividendo_mensal'].iloc[0]
                meta_div = f"R${meta_dividendo:.2f}"
                valor_aproximado = int(qtde_cotas_aperfeiçoar_meta * df_acoes_filtradas[df_acoes_filtradas['papel'] == acao]['cotacao'].iloc[0])
                qtd_cotas_meta = calcular_meta_dividendos(df_acoes_filtradas[df_acoes_filtradas['papel'] == acao], meta_dividendo)['qtde_cotas_meta'].iloc[0]

                # Resumo
                st.header("Resumo")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"Ação: {acao}")
                with col2:
                    st.write(f"Dividendo mensal: {round(dy_mensal,2)}%")
                with col3:
                    st.write(f"Meta de dividendos: {meta_div}")

                # Informações sobre a meta
                valor_aproximado = qtd_cotas_meta * df_acoes_filtradas[df_acoes_filtradas['papel'] == acao]['cotacao'].iloc[0]
                st.markdown(f"Para essa meta, o valor aproximado é de *R${valor_aproximado:.2f}* e *{round(qtd_cotas_meta,0)}* cotas.")

                # Projeção futura
                tempo_necessario = round((int(qtd_cotas_meta) / qtde_cotas_aperfeiçoar_meta))
                vlr_cotas_mensais = float(qtde_cotas_aperfeiçoar_meta * df_acoes_filtradas[df_acoes_filtradas['papel'] == acao]['cotacao'].iloc[0])
                st.header("Projeção Futura")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"Aportes de {qtde_cotas_aperfeiçoar_meta} cotas mensais.")
                with col2:
                    st.write(f"Valor aproximado do aporte: R${vlr_cotas_mensais:.2f}")

                # Tempo necessário
                with st.container():
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"Objetivo atingido em aproximadamente {tempo_necessario} meses.")

                tempo_necessario = round((int(qtd_cotas_meta) / qtde_cotas_aperfeiçoar_meta))
                fig = pd.DataFrame({
                    'Mês': range(1, tempo_necessario + 1),
                    'Qtde de Cotas': [int(qtde_cotas_aperfeiçoar_meta * i) for i in range(1, tempo_necessario + 1)],
                })
                st.bar_chart(fig)
