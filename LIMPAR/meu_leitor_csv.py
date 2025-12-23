import csv
import io
import re
import os

# --- 1. MÓDULO DE METADADOS ---
def separar_metadados_do_texto(linha_bruta):
    # Filtro de segurança para identificar linhas de cabeçalho
    if "/pdf/" not in linha_bruta:
        return None, None

    f = io.StringIO(linha_bruta)
    leitor = csv.reader(f)
    try:
        colunas = next(leitor)
    except StopIteration:
        return None, None

    # Proteção para linhas incompletas
    if len(colunas) < 2: return linha_bruta, ""
    
    # Separa tudo o que é metadado (colunas[:-1]) do texto vazado (colunas[-1])
    lista_metadados = colunas[:-1] 
    inicio_texto = colunas[-1] 

    # Reconstrói a linha de metadados para formato CSV
    output = io.StringIO()
    escritor = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
    escritor.writerow(lista_metadados)
    
    # Retorna (metadados_limpos, texto_inicial_descartado)
    return output.getvalue().strip(), inicio_texto

# --- 2. MÓDULO DE LÓGICA DE PARÁGRAFOS (Atualizada com Poesia Manual) ---
def verificar_inicio_maiusculo(linha):
    # Retorna True se a linha começa com letra Maiúscula (ignora aspas/travessão)
    return bool(re.match(r'^[“"\'\-\—]*\s*[A-Z]', linha))

def organizar_paragrafos(texto_bruto):
    linhas = texto_bruto.split('\n')
    paragrafos_processados = []
    buffer = []
    
    dentro_de_poesia = False

    i = 0
    while i < len(linhas):
        linha_atual = linhas[i].strip()
        
        # --- LIMPEZA PRÉVIA (Resolvendo seus dois problemas) ---

        # 1. Remove linhas que são apenas uma aspas solitária (Sobras do CSV)
        if linha_atual == '"':
            i += 1
            continue

        # 2. Remove sequências de 4 ou mais pontos (................)
        # Substitui por espaço para evitar colar palavras caso estejam no meio do texto
        linha_atual = re.sub(r'\.{4,}', ' ', linha_atual).strip()

        # Se depois de limpar os pontos a linha ficou vazia, pula ela
        if not linha_atual: 
            i += 1
            continue
            
        # --------------------------------------------------------

        # --- A: DETECÇÃO DAS TAGS ---
        
        if "<POESIA>" in linha_atual:
            if buffer:
                texto_unificado = " ".join(buffer)
                texto_limpo = re.sub(r'\s+', ' ', texto_unificado).strip()
                paragrafos_processados.append(texto_limpo)
                buffer = [] 

            dentro_de_poesia = True
            paragrafos_processados.append(linha_atual) 
            i += 1
            continue

        if "<\POESIA>" in linha_atual or "</POESIA>" in linha_atual:
            dentro_de_poesia = False
            paragrafos_processados.append(linha_atual) 
            i += 1
            continue

        # --- B: DENTRO DE POESIA ---
        if dentro_de_poesia:
            paragrafos_processados.append(linha_atual)
            i += 1
            continue

        # --- C: PROSA NORMAL ---
        buffer.append(linha_atual)
        
        termina_pontuacao = linha_atual.endswith(('.', '!', '?', '...'))
        
        proxima_comeca_maiuscula = False
        if i + 1 < len(linhas):
            # Pega a próxima linha ORIGINAL para checar, mas aplica a limpeza de pontos nela
            # temporariamente só para ver se ela não vira vazia
            prox_linha_raw = linhas[i+1].strip()
            prox_linha_limpa = re.sub(r'\.{4,}', ' ', prox_linha_raw).strip()
            
            # Se a próxima linha for só aspas ou pontos, ela "não existe" para a lógica
            if prox_linha_limpa and prox_linha_limpa != '"':
                if "<POESIA>" not in prox_linha_limpa:
                    proxima_comeca_maiuscula = verificar_inicio_maiusculo(prox_linha_limpa)

        proxima_eh_tag = False
        if i + 1 < len(linhas):
             if "<POESIA>" in linhas[i+1]:
                 proxima_eh_tag = True

        if (termina_pontuacao and proxima_comeca_maiuscula) or proxima_eh_tag:
            texto_unificado = " ".join(buffer)
            texto_limpo = re.sub(r'\s+', ' ', texto_unificado).strip()
            paragrafos_processados.append(texto_limpo)
            buffer = [] 

        i += 1
    
    if buffer:
        texto_unificado = " ".join(buffer)
        texto_limpo = re.sub(r'\s+', ' ', texto_unificado).strip()
        paragrafos_processados.append(texto_limpo)
    
    return paragrafos_processados

# --- 3. EXECUTOR PRINCIPAL ---
def processar_dataset_final(arquivo_entrada, arquivo_saida):
    if not os.path.exists(arquivo_entrada):
        print(f"Erro: Arquivo '{arquivo_entrada}' não encontrado.")
        return

    print(f"Processando '{arquivo_entrada}'...")

    with open(arquivo_entrada, 'r', encoding='utf-8') as f_in, \
         open(arquivo_saida, 'w', encoding='utf-8') as f_out:
        
        linhas_arquivo = f_in.readlines()
        buffer_obra_atual = [] 
        
        if linhas_arquivo:
            f_out.write("=== DADOS DO DATASET ===\n")
            f_out.write(linhas_arquivo[0].strip() + "\n\n")

        for linha in linhas_arquivo[1:]:
            
            if "/pdf/" in linha:
                if buffer_obra_atual:
                    texto_bruto_completo = "".join(buffer_obra_atual)
                    paragrafos_finais = organizar_paragrafos(texto_bruto_completo)
                    
                    f_out.write("\n\n".join(paragrafos_finais))
                    f_out.write("\n\n" + ("="*60) + "\n\n") 
                    buffer_obra_atual = [] 

                meta, _ = separar_metadados_do_texto(linha)
                if meta:
                    f_out.write(f"METADADOS: {meta}\n\n")
            else:
                buffer_obra_atual.append(linha)

        if buffer_obra_atual:
            texto_bruto_completo = "".join(buffer_obra_atual)
            paragrafos_finais = organizar_paragrafos(texto_bruto_completo)
            f_out.write("\n\n".join(paragrafos_finais))

    print(f"Concluído! Resultado salvo em '{arquivo_saida}'.")

# --- RODAR ---
processar_dataset_final('teste.csv', 'machado_processado.txt')