#este código reduz caracteres do tipo " ." para "."
import csv
import os
import sys

# --- CONFIGURAÇÕES ---
# O arquivo que saiu do passo anterior (sem asteriscos)
ARQUIVO_ENTRADA = 'machado_sem_asteriscos.csv' 
# O novo arquivo corrigido
ARQUIVO_SAIDA = 'machado_pontuacao_corrigida.csv'

# Aumenta o limite para ler células gigantes (Compatível com Windows)
csv.field_size_limit(2147483647)

def corrigir_pontuacao_texto(texto):
    """
    Substitui " ." por "." em todo o texto.
    """
    if not texto:
        return ""
    
    texto = texto.replace(" ,", ",")

    texto = texto.replace(" .", ".")
    
    # Dica extra: Se quiser fazer o mesmo para vírgulas, descomente abaixo:
    # texto_corrigido = texto_corrigido.replace(" ,", ",")
    
    return texto

def executar_correcao():
    if not os.path.exists(ARQUIVO_ENTRADA):
        print(f"Erro: '{ARQUIVO_ENTRADA}' não encontrado.")
        return

    print(f"Lendo '{ARQUIVO_ENTRADA}' e corrigindo espaços antes de pontos...")

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
                # Aplica a correção em cada célula
                coluna_limpa = corrigir_pontuacao_texto(coluna)
                linha_tratada.append(coluna_limpa)
            
            escritor.writerow(linha_tratada)
            contador += 1

    print(f"Sucesso! {contador} obras processadas.")
    print(f"Arquivo salvo em: {ARQUIVO_SAIDA}")

if __name__ == "__main__":
    executar_correcao()