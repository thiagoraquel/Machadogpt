import csv
import os

# Nome do seu arquivo de teste
ARQUIVO_ENTRADA = 'teste.csv'
ARQUIVO_SAIDA = 'raio_x_quebras.txt'

def gerar_raio_x():
    if not os.path.exists(ARQUIVO_ENTRADA):
        print(f"Erro: Crie o arquivo '{ARQUIVO_ENTRADA}' primeiro.")
        return

    print("Lendo o CSV...")
    
    with open(ARQUIVO_ENTRADA, 'r', encoding='utf-8') as f_in, \
         open(ARQUIVO_SAIDA, 'w', encoding='utf-8') as f_out:
        
        # Usamos o leitor de CSV para ele entender que quebras de linha DENTRO de aspas
        # fazem parte do texto, e não são novas linhas da tabela.
        leitor = csv.reader(f_in)
        
        try:
            for i, linha in enumerate(leitor):
                # Pega a última coluna (assumindo que é onde está o texto)
                if not linha: continue
                texto = linha[-1] 

                f_out.write(f"--- LINHA DO CSV {i} ---\n")
                
                # A MÁGICA:
                # Substitui o "Enter" invisível pelo texto visível "\n"
                # Usamos repr() que mostra a string "crua" (raw)
                texto_visivel = repr(texto)
                
                # Escreve no arquivo
                f_out.write(texto_visivel)
                f_out.write("\n\n") # Pula duas linhas reais para separar no visual
                
            print(f"Sucesso! Abra o arquivo '{ARQUIVO_SAIDA}' para ver os símbolos.")
            
        except csv.Error as e:
            print(f"Erro ao ler CSV: {e}")

gerar_raio_x()