import streamlit as st
import pandas as pd
import openai
import os
import glob
from dotenv import load_dotenv

chave_openai = os.getenv("OPENAI_API_KEY")

st.set_page_config(
    page_title="Ogilvy AI - Seu assistente pessoal da Ogilvy",
    page_icon="Ogilvy_logo.png",
    layout="wide",
    initial_sidebar_state="auto",
  
)

# Tema customizado com cores da Ogilvy
st.markdown(
    """
    <style>
    .css-18e3th9 {
        background-color: #FF0000;
    }
    .css-1cpxqw2 {
        color: #FFFFFF;
    }
    header, footer {
        visibility: hidden;
    }
    .css-145kmo2 {
        color: #000000;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Insert custom CSS for glowing effect
st.markdown(
    """
    <style>
    .cover-glow {
        width: 100%;
        height: auto;
        padding: 3px;
        box-shadow: 
            0 0 5px #330000,
            0 0 10px #660000,
            0 0 15px #990000,
            0 0 20px #CC0000,
            0 0 25px #FF0000,
            0 0 30px #FF3333,
            0 0 35px #FF6666;
        position: relative;
        z-index: -1;
        border-radius: 45px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Função para carregar todos os arquivos .xlsx de uma pasta
def carregar_dados_pasta(pasta):
    arquivos = glob.glob(os.path.join(pasta, "*.xlsx"))
    lista_dfs = []
    for arquivo in arquivos:
        df = pd.read_excel(arquivo)
        lista_dfs.append(df)
    if lista_dfs:
        dados_combinados = pd.concat(lista_dfs, ignore_index=True)
    else:
        dados_combinados = pd.DataFrame()
    return dados_combinados

# Função para criar o prompt com base nos dados
def gerar_prompt_dados(dados, pergunta):
    dados_string = dados.to_string(index=False)
    prompt = f"""
    Eu tenho os seguintes dados em formato de tabela:
    {dados_string}
    
    Com base nesses dados, responda à seguinte pergunta:
    {pergunta}
    """
    return prompt

# Função para interagir com a API da OpenAI via LangChain
def responder_pergunta(prompt, chave_openai, modelo="gpt-3.5-turbo"):
    openai.api_key = chave_openai
    response = openai.ChatCompletion.create(
        model=modelo,
        messages=[
            {"role": "system", "content":"""Você é um assistente publicitário da Agência Ogilvy que ajuda a
             interpretar dados e responde perguntas em conversas gerais e sobre a agência.
             Responda com o que encontrar na base de dados. Caso você não encontre resposta na base de dados,
             tente argumentar e ajudar a responder com sua base de conhecimento."""},
            {"role": "user", "content": prompt}
        ]
    )
    return response['choices'][0]['message']['content']

# Função para determinar se a pergunta é sobre dados ou genérica
def verificar_pergunta_sobre_dados(pergunta):
    palavras_chave_dados = ["Clientes","Ogilvy","tabela", "dados", "coluna", "linha", "valor", "registro", "média", "soma"]
    return any(palavra in pergunta.lower() for palavra in palavras_chave_dados)

# Interface no Streamlit
st.image("AI.png", width=300)

# Histórico de perguntas e respostas
if 'historico' not in st.session_state:
    st.session_state.historico = []

with st.container():
    st.header("Este é seu assistente de IA da Ogilvy")
    st.markdown("""
    Faça perguntas como:
    - Quais são os principais clientes da agência?
    - Há quanto tempo o cliente x está na Ogilvy?
    - Quem é responsável pela área de Data Intelligence?
    - O que faz a área de planejamento da Ogilvy?
    - Quem são os C-levels da Ogilvy?
    - Qual é a politica da Ogilvy sobre "assunto x"
    """)
    st.markdown("""
    <small><i>Obs: Este é um modelo inicial, foi treinado com uma pequena base de dados, e algumas informações são genéricas ou aleatórias.</i></small>
    """, unsafe_allow_html=True)

    dados = carregar_dados_pasta("dados_xlsx")

    pergunta = st.text_input("Faça sua pergunta:")

    if pergunta:
        with st.spinner('Processando sua pergunta...'):
            prompt = gerar_prompt_dados(dados, pergunta)
            resposta = responder_pergunta(prompt, chave_openai)
        
        # Adicionar ao histórico
        st.session_state.historico.append(f"**Pergunta:** {pergunta}\n**Resposta:** {resposta}")
        
        # Mostrar a resposta
        st.write("Resposta:")
        st.write(resposta)

    # Exibir o histórico
    st.write("### Histórico de Perguntas e Respostas")
    for item in st.session_state.historico:
        st.write(item)

# Estilizando o footer
footer_image = "download.png"
st.image(footer_image, width=10, use_column_width=True, output_format='auto')
st.markdown(
    """
    <style>
    footer {
        visibility: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True
)
