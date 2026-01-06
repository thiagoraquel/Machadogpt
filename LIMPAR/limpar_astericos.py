import csv
import re
import os
import sys

# --- CONFIGURAÇÕES ---
ARQUIVO_ENTRADA = 'obras_machado_de_assis.csv' 
ARQUIVO_SAIDA = 'machado_sem_asteriscos.csv'

# Aumenta o limite para ler células gigantes (Compatível com Windows)
csv.field_size_limit(2147483647)

def limpar_asteriscos_do_texto(texto):
    """
    Remove asteriscos e conserta os espaços resultantes.
    """
    if not texto:
        return ""

    linhas = texto.split('\n')
    linhas_limpas = []

    for linha in linhas:
        # REGRA 0: Se a linha for vazia, mantém ela vazia e passa pra próxima
        if not linha.strip():
            linhas_limpas.append(linha)
            continue

        # REGRA DE PROTEÇÃO: Se a linha for apenas uma aspas, mantém.
        if linha.strip() == '"':
            linhas_limpas.append(linha)
            continue

        # REGRA 1: Se a linha tiver APENAS asteriscos (e espaços), ela é deletada.
        if re.match(r'^\s*\*+\s*$', linha):
            continue 

        # REGRA 2 (MELHORADA): Asterisco vira espaço + Correção imediata
        
        # Passo A: Troca asterisco por espaço (evita colar palavras)
        temp = linha.replace('*', ' ')
        
        # Passo B: O "Algoritmo de Conserto"
        # 1. re.sub(r'\s+', ' ', temp): Transforma "   " em " " (tira os buracos no meio)
        # 2. .strip(): Tira os espaços que sobraram nas pontas (traz a frase pra frente)
        nova_linha = re.sub(r'\s+', ' ', temp).strip()

        if nova_linha:
            linhas_limpas.append(nova_linha)

    return '\n'.join(linhas_limpas)

def executar_limpeza():
    if not os.path.exists(ARQUIVO_ENTRADA):
        print(f"Erro: '{ARQUIVO_ENTRADA}' não encontrado.")
        return

    print(f"Lendo '{ARQUIVO_ENTRADA}' e corrigindo espaços...")

    with open(ARQUIVO_ENTRADA, 'r', encoding='utf-8', newline='') as f_in, \
         open(ARQUIVO_SAIDA, 'w', encoding='utf-8', newline='') as f_out:
        
        leitor = csv.reader(f_in)
        escritor = csv.writer(f_out, quoting=csv.QUOTE_MINIMAL)

        try:
            cabecalho = next(leitor)
            escritor.writerow(cabecalho)
        except StopIteration:
            return

        contador = 0
        for linha_csv in leitor:
            linha_tratada = []
            for coluna in linha_csv:
                coluna_limpa = limpar_asteriscos_do_texto(coluna)
                linha_tratada.append(coluna_limpa)
            
            escritor.writerow(linha_tratada)
            contador += 1

    print(f"Sucesso! {contador} obras processadas.")
    print(f"Arquivo limpo salvo em: {ARQUIVO_SAIDA}")

if __name__ == "__main__":
    executar_limpeza()