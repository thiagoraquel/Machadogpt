import os

print("Iniciando limpeza de todos os arquivos .txt na pasta atual...")

# Lista todos os arquivos na pasta atual
arquivos_na_pasta = os.listdir('.')

# Passa por cada arquivo encontrado
for nome_arquivo in arquivos_na_pasta:
    # Verifica se o arquivo termina com .txt e não é um arquivo já limpo
    if nome_arquivo.endswith('.txt') and not nome_arquivo.endswith('_limpo.txt'):
        
        nome_arquivo_limpo = nome_arquivo.replace('.txt', '_limpo.txt')
        
        print(f"\nProcessando: {nome_arquivo}...")

        try:
            # Lê o conteúdo do arquivo original
            with open(nome_arquivo, 'r', encoding='utf-8') as f:
                conteudo_original = f.read()

            # Remove o caractere \f
            conteudo_limpo = conteudo_original.replace('\f', '')

            # Salva o conteúdo limpo
            with open(nome_arquivo_limpo, 'w', encoding='utf-8') as f:
                f.write(conteudo_limpo)
            
            print(f"-> Salvo como: {nome_arquivo_limpo}")

        except Exception as e:
            print(f"❌ ERRO ao processar o arquivo {nome_arquivo}: {e}")

print("\n" + "-" * 30)
print("✅ Limpeza concluída para todos os arquivos .txt!")