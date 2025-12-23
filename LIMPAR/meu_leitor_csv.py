import csv
import io
import re
import os

# --- SUAS FUNÇÕES (Lógica Preservada) ---

def separar_metadados_do_texto(linha_bruta):
    # 1. Filtro de Segurança
    if "/pdf/" not in linha_bruta:
        return None, None

    # 2. Parsear a linha
    f = io.StringIO(linha_bruta)
    leitor = csv.reader(f)
    try:
        colunas = next(leitor)
    except StopIteration:
        return None, None

    # 3. O Corte
    if len(colunas) < 2: return linha_bruta, "" # Proteção contra linhas quebradas
    
    lista_metadados = colunas[:-1] 
    inicio_texto = colunas[-1] # Texto "vazado" (Geralmente duplica o título)

    # 4. Reconstrói a linha de metadados limpa
    output = io.StringIO()
    escritor = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
    escritor.writerow(lista_metadados)
    linha_metadados_limpa = output.getvalue().strip()

    return linha_metadados_limpa, inicio_texto

def verificar_inicio_maiusculo(linha):
    return bool(re.match(r'^[“"\'\-\—]*\s*[A-Z]', linha))

def organizar_paragrafos_v3(texto_bruto):
    linhas = texto_bruto.split('\n')
    paragrafos_processados = []
    buffer = []

    i = 0
    while i < len(linhas):
        linha_atual = linhas[i].strip()
        
        if not linha_atual: 
            i += 1
            continue

        buffer.append(linha_atual)
        
        # --- LÓGICA DE DECISÃO ---
        termina_pontuacao = linha_atual.endswith(('.', '!', '?', '...'))
        
        proxima_comeca_maiuscula = False
        if i + 1 < len(linhas):
            proxima_linha = linhas[i+1].strip()
            if proxima_linha:
                proxima_comeca_maiuscula = verificar_inicio_maiusculo(proxima_linha)

        if termina_pontuacao and proxima_comeca_maiuscula:
            texto_completo = " ".join(buffer)
            paragrafos_processados.append(texto_completo)
            buffer = [] 

        i += 1
    
    if buffer:
        texto_final = " ".join(buffer)
        paragrafos_processados.append(texto_final)
    
    return paragrafos_processados

# --- PROGRAMA PRINCIPAL ---

def processar_arquivo_csv(arquivo_entrada, arquivo_saida):
    if not os.path.exists(arquivo_entrada):
        print(f"Erro: Arquivo '{arquivo_entrada}' não encontrado.")
        return

    print(f"Iniciando processamento de '{arquivo_entrada}'...")

    with open(arquivo_entrada, 'r', encoding='utf-8') as f_in, \
         open(arquivo_saida, 'w', encoding='utf-8') as f_out:
        
        # Lê todas as linhas brutas (incluindo \n)
        linhas_arquivo = f_in.readlines()
        
        buffer_texto_obra_atual = [] # Vai guardar as linhas de texto da obra sendo lida
        primeira_obra = True

        # 1. Processa o Cabeçalho (Primeira Linha)
        if linhas_arquivo:
            header = linhas_arquivo[0]
            f_out.write("=== CABEÇALHO DO ARQUIVO ===\n")
            f_out.write(header)
            f_out.write("\n" + ("="*40) + "\n\n")

        # 2. Loop pelas linhas (começando da segunda)
        for linha in linhas_arquivo[1:]:
            
            # Checa se é uma linha de METADADOS (Nova Obra)
            if "/pdf/" in linha:
                
                # --- PASSO A: Salvar a obra ANTERIOR (se houver) ---
                if buffer_texto_obra_atual:
                    # Junta tudo para enviar para a função de parágrafos
                    # Usamos "".join para manter os \n originais que o readlines pegou
                    texto_completo_bruto = "".join(buffer_texto_obra_atual)
                    
                    paragrafos_limpos = organizar_paragrafos_v3(texto_completo_bruto)
                    
                    # Escreve os parágrafos no arquivo com linha em branco entre eles
                    f_out.write("\n\n".join(paragrafos_limpos))
                    f_out.write("\n\n" + ("#"*50) + "\n\n") # Separador visual de fim de obra
                    
                    buffer_texto_obra_atual = [] # Limpa para a nova obra

                # --- PASSO B: Processar os metadados da NOVA obra ---
                meta_limpa, inicio_texto_vazado = separar_metadados_do_texto(linha)
                
                if meta_limpa:
                    f_out.write(meta_limpa + "\n\n")
                    # Nota: Ignoramos o 'inicio_texto_vazado' aqui porque você mencionou
                    # que ele é duplicado do título. O texto real virá nas próximas linhas.
            
            else:
                # É linha de texto (corpo da obra)
                buffer_texto_obra_atual.append(linha)

        # --- PASSO FINAL: Salvar a ÚLTIMA obra (que sobrou no buffer ao fim do arquivo) ---
        if buffer_texto_obra_atual:
            texto_completo_bruto = "".join(buffer_texto_obra_atual)
            paragrafos_limpos = organizar_paragrafos_v3(texto_completo_bruto)
            f_out.write("\n\n".join(paragrafos_limpos))

    print(f"Sucesso! Resultado salvo em '{arquivo_saida}'")

# Executa
processar_arquivo_csv('teste.csv', 'resultado_teste.txt')