import csv
import io
import re
import os

# --- MÓDULO DE METADADOS (Mantido igual) ---
def separar_metadados_do_texto(linha_bruta):
    if "/pdf/" not in linha_bruta: return None, None
    f = io.StringIO(linha_bruta)
    leitor = csv.reader(f)
    try: colunas = next(leitor)
    except StopIteration: return None, None
    if len(colunas) < 2: return linha_bruta, ""
    lista_metadados = colunas[:-1] 
    inicio_texto = colunas[-1] 
    output = io.StringIO()
    escritor = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
    escritor.writerow(lista_metadados)
    return output.getvalue().strip(), inicio_texto

# --- Função Auxiliar de Diálogos ---
def separar_dialogos_colados(texto):
    # Procura por: Dois pontos (:) + espaços opcionais (\s*) + Travessão (—)
    # Substitui por: Dois pontos + Quebra de linha (\n) + Travessão
    return re.sub(r':\s*—', ':\n—', texto)

# --- Detecta Capítulos (Mantido o seu original) ---
def verificar_se_eh_capitulo(linha):
    # Adicionamos "parecer" na lista de palavras que funcionam como Título/Capítulo
    termos_estruturais = r'índice|sumário|prólogo|prefácio|introdução|fim|parecer'
    
    # A regex agora pega:
    # 1. Capítulo numérico/romano (CAPÍTULO IV, III)
    # 2. Palavras estruturais isoladas ou seguidas de texto (PARECER SOBRE...)
    
    # Nota: adicionei ".*" depois de termos_estruturais para pegar "Parecer sobre..."
    padrao = f'^(capítulo\s+([ivxlcdm]+|\d+)|[ivxlcdm]+|({termos_estruturais}).*)$'
    
    return bool(re.match(padrao, linha.strip(), re.IGNORECASE))

def verificar_inicio_maiusculo(linha):
    # Aceita Maiúscula ou Número
    return bool(re.match(r'^[“"\'\-\—]*\s*([A-Z]|[0-9])', linha))

def organizar_paragrafos(texto_bruto):
    # 1. APLICA A CORREÇÃO DE DIÁLOGOS ANTES DE DIVIDIR AS LINHAS
    texto_bruto = separar_dialogos_colados(texto_bruto)
    
    linhas = texto_bruto.split('\n')
    paragrafos_processados = []
    buffer = []
    
    dentro_de_poesia = False

    i = 0
    while i < len(linhas):
        linha_atual = linhas[i].strip()
        
        # --- LIMPEZA ---
        if linha_atual == '"': 
            i += 1; continue

        linha_atual = linha_atual.replace('–', '—') 
        linha_atual = re.sub(r'\.{4,}', ' ', linha_atual).strip()

        if not linha_atual: 
            i += 1; continue
            
        # --- POESIA ---
        if "<POESIA>" in linha_atual:
            if buffer: 
                paragrafos_processados.append(re.sub(r'\s+', ' ', " ".join(buffer)).strip())
                buffer = [] 
            dentro_de_poesia = True
            paragrafos_processados.append(linha_atual); i += 1; continue

        if "<\POESIA>" in linha_atual or "</POESIA>" in linha_atual:
            dentro_de_poesia = False
            paragrafos_processados.append(linha_atual); i += 1; continue

        if dentro_de_poesia:
            paragrafos_processados.append(linha_atual); i += 1; continue

        # --- CAPÍTULOS ---
        if verificar_se_eh_capitulo(linha_atual):
            if buffer:
                paragrafos_processados.append(re.sub(r'\s+', ' ', " ".join(buffer)).strip())
                buffer = []
            paragrafos_processados.append(linha_atual)
            i += 1
            continue

        buffer.append(linha_atual)
        
        # --- DECISÃO DE JUNTAR ---
        termina_pontuacao = linha_atual.endswith(('.', '!', '?', '...'))
        termina_dois_pontos = linha_atual.endswith(':') # <--- NOVO CHECK
        
        proxima_comeca_maiuscula = False
        proxima_eh_tag = False
        proxima_eh_capitulo = False
        proxima_comeca_travessao = False # <--- NOVO CHECK

        if i + 1 < len(linhas):
            prox_raw = linhas[i+1].strip()
            prox_clean = re.sub(r'\.{4,}', ' ', prox_raw).strip()
            
            if prox_clean and prox_clean != '"':
                if "<POESIA>" in prox_clean:
                    proxima_eh_tag = True
                
                elif verificar_se_eh_capitulo(prox_clean):
                    proxima_eh_capitulo = True
                
                else:
                    proxima_comeca_maiuscula = verificar_inicio_maiusculo(prox_clean)
                    # Verifica se a próxima linha é fala de personagem
                    if prox_clean.startswith('—'):
                        proxima_comeca_travessao = True

        # CONDIÇÕES PARA QUEBRAR O PARÁGRAFO:
        # 1. Padrão: Ponto + Maiúscula/Número
        # 2. Diálogo: Dois Pontos + Travessão na próxima linha
        # 3. Estrutural: Tags ou Capítulos vindo a seguir
        
        caso_ponto_maiuscula = (termina_pontuacao and proxima_comeca_maiuscula)
        caso_dialogo_introduzido = (termina_dois_pontos and proxima_comeca_travessao)

        if caso_ponto_maiuscula or caso_dialogo_introduzido or proxima_eh_tag or proxima_eh_capitulo:
            texto_limpo = re.sub(r'\s+', ' ', " ".join(buffer)).strip()
            paragrafos_processados.append(texto_limpo)
            buffer = [] 

        i += 1
    
    if buffer:
        paragrafos_processados.append(re.sub(r'\s+', ' ', " ".join(buffer)).strip())
    
    return paragrafos_processados

# --- EXECUTOR (Mantido Igual) ---
def processar_dataset_final(arquivo_entrada, arquivo_saida):
    if not os.path.exists(arquivo_entrada):
        print(f"Erro: '{arquivo_entrada}' não encontrado.")
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
                    texto = "".join(buffer_obra_atual)
                    f_out.write("\n\n".join(organizar_paragrafos(texto)))
                    f_out.write("\n\n" + ("="*60) + "\n\n") 
                    buffer_obra_atual = [] 
                meta, _ = separar_metadados_do_texto(linha)
                if meta: f_out.write(f"METADADOS: {meta}\n\n")
            else:
                buffer_obra_atual.append(linha)
        if buffer_obra_atual:
            f_out.write("\n\n".join(organizar_paragrafos("".join(buffer_obra_atual))))
    print(f"Concluído! Salvo em '{arquivo_saida}'.")

processar_dataset_final('teste.csv', 'machado_processado_v5.txt')