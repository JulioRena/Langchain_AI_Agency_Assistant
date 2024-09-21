import streamlit as st
import pandas as pd
import openai
import os
import glob

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
            {"role": "system", "content": "Você é um assistente que ajuda a interpretar dados e responde perguntas em conversas gerais."},
            {"role": "user", "content": prompt}
        ]
    )
    return response['choices'][0]['message']['content']

# Função para determinar se a pergunta é sobre dados ou genérica
def verificar_pergunta_sobre_dados(pergunta):
    palavras_chave_dados = ["tabela", "dados", "coluna", "linha", "valor", "registro", "média", "soma"]
    return any(palavra in pergunta.lower() for palavra in palavras_chave_dados)

# Interface no Streamlit
st.title("Chat de Análise de Dados e Conversação Geral com OpenAI")

# Adicionando o campo na barra lateral para inserir a chave da OpenAI
with st.sidebar:
    st.header("Configurações da OpenAI")
    chave_openai = st.text_input("Insira sua chave da OpenAI", type="password")

# Verifica se a chave foi inserida
if chave_openai:
    st.success("Chave da OpenAI foi inserida com sucesso!")
    
    # Carregar os dados de todos os arquivos .xlsx na pasta "dados_xlsx"
    dados = carregar_dados_pasta("dados_xlsx")

    # Verificar se há dados carregados
    # if not dados.empty:
    #     st.write("Aqui estão os dados combinados de todos os arquivos:")
    #     st.dataframe(dados)

    # Campo para pergunta e interação após a chave ser inserida
    pergunta = st.text_input("Faça sua pergunta:")

    if pergunta:
        if verificar_pergunta_sobre_dados(pergunta):
            # Gerar o prompt com base nos dados
            prompt = gerar_prompt_dados(dados, pergunta)
        else:
            # Usar a pergunta diretamente para uma conversa geral
            prompt = pergunta
        
        # Obter a resposta utilizando a chave da OpenAI inserida
        resposta = responder_pergunta(prompt, chave_openai)
        
        # Mostrar a resposta
        st.write("Resposta:")
        st.write(resposta)
else:
    st.warning("Por favor, insira sua chave da OpenAI para continuar.")
