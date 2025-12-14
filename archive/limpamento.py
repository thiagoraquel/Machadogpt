import pandas as pd
import sklearn
from sklearn.model_selection import train_test_split
import re
import json
import os

# --- CONFIGURAÇÃO ---
# Substitua pelo nome exato do seu arquivo que você fez upload no Colab
NOME_ARQUIVO_CSV = 'obras_machado_de_assis.csv' 
COLUNA_TEXTO = 'texto' # Nome da coluna que contém o texto no seu CSV

def preparar_dataset_machado():
    print("--- 1. Carregando o Dataset ---")
    if not os.path.exists(NOME_ARQUIVO_CSV):
        print(f"ERRO: O arquivo '{NOME_ARQUIVO_CSV}' não foi encontrado. Faça o upload primeiro.")
        return

    # Lê o CSV lidando com aspas e linhas múltiplas
    # Tenta utf-8, se falhar (comum em arquivos antigos), tenta latin-1
    try:
        df = pd.read_csv(NOME_ARQUIVO_CSV, quotechar='"', on_bad_lines='skip', encoding='utf-8')
    except UnicodeDecodeError:
        print("Aviso: UTF-8 falhou, tentando latin-1...")
        df = pd.read_csv(NOME_ARQUIVO_CSV, quotechar='"', on_bad_lines='skip', encoding='latin-1')

    print(f"Total de registros carregados: {len(df)}")

    # --- 2. Limpeza e Formatação para GPT-2 ---
    print("--- 2. Limpando e Formatando ---")

    def limpar_texto(texto):
        if not isinstance(texto, str):
            return ""

        # 1. REMOÇÃO DE CABEÇALHOS E METADADOS
        padroes_para_remover = [
            r"Texto-Fonte:.*",
            r"Publicado originalmente.*",
            r"Publicado na.*",
            r"Obra Completa de Machado de Assis.*",
            r"Rio de Janeiro:.*",
            r"vol\. [IVX]+, \d{4}\.",
            r"Garnier editor, \d{4}\.",
            r"^ÍNDICE.*"
        ]
        for padrao in padroes_para_remover:
            texto = re.sub(padrao, "", texto, flags=re.IGNORECASE | re.MULTILINE)

        # 2. LIMPEZA DE LINHAS "LIXO"
        linhas = texto.split('\n')
        linhas_limpas = []
        for linha in linhas:
            l = linha.strip()
            if l.isupper() and len(l) < 50: continue # Títulos soltos
            if l.isdigit(): continue # Números de página
            linhas_limpas.append(linha)
        texto = '\n'.join(linhas_limpas)

        # 3. TRATAMENTO DE QUEBRAS DE LINHA
        texto = texto.replace('\n\n', '<<PARAGRAFO>>')
        texto = texto.replace('\n', ' ')
        texto = texto.replace('<<PARAGRAFO>>', '\n\n')

        # --- NOVO: REMOÇÃO DE PONTILHADOS ---
        # Remove sequências de 4 ou mais pontos (ex: ".......") substituindo por espaço
        # Preserva as reticências estilísticas (...)
        texto = re.sub(r'\.{4,}', ' ', texto) 

        # 4. LIMPEZA FINAL
        texto = re.sub(r' +', ' ', texto).strip()
        
        if len(texto) > 0:
            texto = texto + " <|endoftext|>"
        
        return texto

    # Aplica a limpeza
    df['texto_processado'] = df[COLUNA_TEXTO].apply(limpar_texto)

    # Remove textos muito curtos (ex: linhas vazias ou erros de metadados)
    # <|endoftext|> tem 13 caracteres, então filtramos o que for menor que 50
    df = df[df['texto_processado'].str.len() > 50]
    
    print(f"Registros válidos após limpeza: {len(df)}")

    # --- 3. Divisão (Train / Val / Test) ---
    print("--- 3. Dividindo o Dataset ---")
    
    # 80% Treino, 20% Resto
    train, resto = train_test_split(df, test_size=0.2, random_state=42)
    # O Resto divide em 50/50 (10% Validação, 10% Teste do total original)
    val, test = train_test_split(resto, test_size=0.5, random_state=42)

    print(f"Tamanho Treino: {len(train)} obras")
    print(f"Tamanho Validação: {len(val)} obras")
    print(f"Tamanho Teste: {len(test)} obras")

    # --- 4. Salvando em JSONL ---
    def salvar_jsonl(dataframe, nome_saida):
        with open(nome_saida, 'w', encoding='utf-8') as f:
            for texto in dataframe['texto_processado']:
                # Formato padrão para datasets HuggingFace: {"text": "conteudo..."}
                linha_json = json.dumps({"text": texto}, ensure_ascii=False)
                f.write(linha_json + '\n')
        print(f"Salvo: {nome_saida}")

    salvar_jsonl(train, 'train_machado.jsonl')
    salvar_jsonl(val, 'validation_machado.jsonl')
    salvar_jsonl(test, 'test_machado.jsonl')

    print("\n--- SUCESSO! ---")
    print("Arquivos prontos para o treinamento.")
    print("Próximo passo: Carregar 'train_machado.jsonl' no script de fine-tuning.")

# Executa a função
preparar_dataset_machado()