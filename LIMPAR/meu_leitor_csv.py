import csv
import io
import re
import os

# --- MÓDULO DE METADADOS (Inalterado) ---
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

# --- NOVO: Detecta Capítulos (Numerais Romanos ou "CAPÍTULO X") ---
def verificar_se_eh_capitulo(linha):
    # Regex para pegar:
    # 1. Numerais Romanos sozinhos: ^[IVXLCDM]+$ (ex: "III", "IV")
    # 2. Palavra Capítulo + Numeral: ^CAPÍTULO\s+[IVXLCDM]+ (ex: "CAPÍTULO IV")
    # 3. Palavra Capítulo + Número: ^CAPÍTULO\s+\d+
    # Ignora espaços no começo/fim e é Case Insensitive (re.IGNORECASE)
    padrao = r'^(capítulo\s+([ivxlcdm]+|\d+)|[ivxlcdm]+)$'
    return bool(re.match(padrao, linha.strip(), re.IGNORECASE))

def verificar_inicio_maiusculo(linha):
    # Antes era: ...[A-Z]
    # Agora é:   ...([A-Z]|[0-9])
    # Isso diz: "Se começar com Letra Maiúscula OU Número, é início de bloco novo"
    return bool(re.match(r'^[“"\'\-\—]*\s*([A-Z]|[0-9])', linha))

def organizar_paragrafos(texto_bruto):
    linhas = texto_bruto.split('\n')
    paragrafos_processados = []
    buffer = []
    
    dentro_de_poesia = False

    i = 0
    while i < len(linhas):
        linha_atual = linhas[i].strip()
        
        # --- LIMPEZA INICIAL ---
        if linha_atual == '"': # Remove aspas órfãs
            i += 1; continue

        # Normaliza travessões (Transforma en-dash – em em-dash —)
        linha_atual = linha_atual.replace('–', '—') 
        
        # Remove excesso de pontos
        linha_atual = re.sub(r'\.{4,}', ' ', linha_atual).strip()

        if not linha_atual: 
            i += 1; continue
            
        # --- TAGS DE POESIA ---
        if "<POESIA>" in linha_atual:
            if buffer: # Salva prosa pendente
                paragrafos_processados.append(re.sub(r'\s+', ' ', " ".join(buffer)).strip())
                buffer = [] 
            dentro_de_poesia = True
            paragrafos_processados.append(linha_atual); i += 1; continue

        if "<\POESIA>" in linha_atual or "</POESIA>" in linha_atual:
            dentro_de_poesia = False
            paragrafos_processados.append(linha_atual); i += 1; continue

        if dentro_de_poesia:
            paragrafos_processados.append(linha_atual); i += 1; continue

        # --- LÓGICA DE PROSA ---
        
        # Se a LINHA ATUAL for um título de capítulo, salvamos o buffer anterior e salvamos ela isolada
        if verificar_se_eh_capitulo(linha_atual):
            if buffer:
                paragrafos_processados.append(re.sub(r'\s+', ' ', " ".join(buffer)).strip())
                buffer = []
            
            # Salva o capítulo isolado (sem juntar com nada)
            paragrafos_processados.append(linha_atual)
            i += 1
            continue

        buffer.append(linha_atual)
        
        # --- DECISÃO DE JUNTAR ---
        termina_pontuacao = linha_atual.endswith(('.', '!', '?', '...'))
        
        proxima_comeca_maiuscula = False
        proxima_eh_tag = False
        proxima_eh_capitulo = False # Nova flag

        if i + 1 < len(linhas):
            prox_raw = linhas[i+1].strip()
            # Aplica a mesma limpeza básica na próxima linha para checar
            prox_clean = re.sub(r'\.{4,}', ' ', prox_raw).strip()
            
            if prox_clean and prox_clean != '"':
                if "<POESIA>" in prox_clean:
                    proxima_eh_tag = True
                
                # Checa se a próxima linha é um capítulo (ex: "IV")
                # Se for, temos que fechar o parágrafo atual AGORA.
                elif verificar_se_eh_capitulo(prox_clean):
                    proxima_eh_capitulo = True
                
                else:
                    proxima_comeca_maiuscula = verificar_inicio_maiusculo(prox_clean)

        # Regras para FECHAR o parágrafo:
        # 1. Pontuação + Maiúscula (Padrão)
        # 2. Próxima linha é TAG de poesia
        # 3. Próxima linha é um CAPÍTULO/TÍTULO (Isso impede de colar texto no título)
        if (termina_pontuacao and proxima_comeca_maiuscula) or proxima_eh_tag or proxima_eh_capitulo:
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