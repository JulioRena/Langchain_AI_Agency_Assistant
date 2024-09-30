import streamlit as st
import pandas as pd
import openai
import os
import glob
from dotenv import load_dotenv
import boto3
from io import BytesIO

chave_openai = os.getenv("OPENAI_API_KEY")
aws_access_key_id = os.getenv("aws_access_key_id")
aws_secret_access_key = os.getenv("aws_secret_access_key")
s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id,
                     aws_secret_access_key=aws_secret_access_key)

bucket = "ogilvy-data"
file_key = 'dados_xlsx/'
#s3.download_file(bucket, file_key, 'local_file.xlsx')


st.set_page_config(
    page_title="Ogilvy AI - Seu assistente pessoal da Ogilvy",
    page_icon="Ogilvy_logo.png",
    layout="wide",
    initial_sidebar_state="auto",
  
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

def carregar_dados_s3(pasta_s3, bucket_name):
    # Acessar as credenciais AWS armazenadas no secrets do Streamlit
    s3 = boto3.client('s3',
                      aws_access_key_id=st.secrets["aws"]["aws_access_key_id"],
                      aws_secret_access_key=st.secrets["aws"]["aws_secret_access_key"])

    # Listar os arquivos na pasta do S3
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=pasta_s3)
    
    lista_dfs = []
    
    if 'Contents' in response:
        for item in response['Contents']:
            file_key = item['Key']
            
            # Verifica se é um arquivo .xlsx
            if file_key.endswith('.xlsx'):
                # Baixar o arquivo do S3
                file_obj = s3.get_object(Bucket=bucket_name, Key=file_key)
                # Ler o conteúdo do arquivo diretamente em um DataFrame
                df = pd.read_excel(BytesIO(file_obj['Body'].read()))
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
            {"role": "system", "content": "Você é um assistente publicitário da Agência Ogilvy que ajuda a interpretar dados e responde perguntas em conversas gerais e sobre a agência. Responda com o que encontrar na base de dados"},
            {"role": "user", "content": prompt}
        ]
    )
    return response['choices'][0]['message']['content']

# Função para determinar se a pergunta é sobre dados ou genérica
def verificar_pergunta_sobre_dados(pergunta):
    palavras_chave_dados = ["Clientes","Ogilvy","tabela", "dados", "coluna", "linha", "valor", "registro", "média", "soma"]
    return any(palavra in pergunta.lower() for palavra in palavras_chave_dados)

# Interface no Streamlit
st.title("OgilvyAI Assistant")

# # Adicionando o campo na barra lateral para inserir a chave da OpenAI
# with st.sidebar:
#     st.header("Configurações da OpenAI")
#     chave_openai = st.text_input("Insira sua chave da OpenAI", type="password")

# # Verifica se a chave foi inserida
# if chave_openai:
#     st.success("Chave da OpenAI foi inserida com sucesso!")
    
    # Carregar os dados de todos os arquivos .xlsx na pasta "dados_xlsx"
dados = carregar_dados_s3(pasta_s3=file_key, bucket_name=bucket)

    # Verificar se há dados carregados
    # if not dados.empty:
    #     st.write("Aqui estão os dados combinados de todos os arquivos:")
    #     st.dataframe(dados)

    # Campo para pergunta e interação após a chave ser inserida
pergunta = st.text_input("Faça sua pergunta:")

if pergunta:
    #if verificar_pergunta_sobre_dados(pergunta):
        # Gerar o prompt com base nos dados
    prompt = gerar_prompt_dados(dados, pergunta)
    #else:
        # Usar a pergunta diretamente para uma conversa geral
        # prompt = pergunta
    
    # Obter a resposta utilizando a chave da OpenAI inserida
    resposta = responder_pergunta(prompt, chave_openai)
    
    # Mostrar a resposta
    st.write("Resposta:")
    st.write(resposta)

