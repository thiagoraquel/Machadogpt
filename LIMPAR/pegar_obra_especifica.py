import os

ARQUIVO_CSV = 'obras_machado_de_assis.csv' # Ou o nome do seu arquivo original completo
ARQUIVO_SAIDA = 'teste.csv'

def extrair_obra_especifica(indice_alvo):
    if not os.path.exists(ARQUIVO_CSV):
        print(f"Erro: '{ARQUIVO_CSV}' não encontrado.")
        return

    print(f"Procurando a obra de índice {indice_alvo}...")

    with open(ARQUIVO_CSV, 'r', encoding='utf-8') as f_in:
        linhas = f_in.readlines()

    buffer_obra = []
    contador_encontrados = -1 # Começa em -1 para que a primeira ocorrência seja o índice 0
    capturando = False
    encontrou = False

    for linha in linhas:
        # Verifica se é uma linha de metadados (início de obra)
        eh_inicio_obra = "/pdf/" in linha

        if eh_inicio_obra:
            contador_encontrados += 1
            
            # CASO 1: Encontramos a obra que queríamos
            if contador_encontrados == indice_alvo:
                capturando = True
                encontrou = True
                buffer_obra.append(linha) # Adiciona a linha de metadados
                continue
            
            # CASO 2: Encontramos a PRÓXIMA obra (hora de parar)
            if contador_encontrados > indice_alvo:
                break # Sai do loop para economizar tempo

        # Se estamos no modo de captura, adiciona a linha
        if capturando and not eh_inicio_obra:
            buffer_obra.append(linha)

    # --- SALVANDO O RESULTADO ---
    if encontrou:
        with open(ARQUIVO_SAIDA, 'w', encoding='utf-8') as f_out:
            # Escreve exatamente como estava no CSV (com metadados e quebras originais)
            f_out.writelines(buffer_obra)
        
        print(f"--- SUCESSO! ---")
        print(f"Obra de índice {indice_alvo} extraída.")
        print(f"Total de linhas extraídas: {len(buffer_obra)}")
        print(f"Salvo em: '{ARQUIVO_SAIDA}'")
        
        # Preview do começo
        print("\n--- PREVIEW (Primeiras 3 linhas) ---")
        for l in buffer_obra[:3]:
            print(repr(l)) # repr mostra os \n invisíveis
    else:
        print(f"Erro: Índice {indice_alvo} não encontrado. O arquivo tem apenas {contador_encontrados + 1} obras.")

# --- MUDE O NÚMERO AQUI PARA ESCOLHER QUAL OBRA PEGAR ---
extrair_obra_especifica(6) # ideias teatro (número 7)