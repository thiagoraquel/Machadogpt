import re
import csv
import io

texto_base = """
O primeiro volume com que o Sr. Zaluar se estreou na poesia intitulava-se Dores e
Flores; foi justamente apreciado como um primeiro ensaio; mas desde então a
crítica reconheceu no poeta um legítimo talento e o admitiu entre as esperanças
que começavam a florir nesse tempo.
.
As torturas de Bossuet para descrever o sonho da heroína servem-me de aviso
nesta conjuntura, mas tiram-me uma das mais apropriadas figuras, com que eu
poderia definir o resultado mau e o resultado bom dessas esperanças nascentes.
Direi em prosa simples que o autor das Dores e Flores foi das esperanças que
vingaram, e pode atravessar os anos dando provas do seu talento sempre
desenvolvido.
Ela falou que o Sr.
Flávio não gostou do remédio.
"""

# lógica para lidar com o cabeçalho de metadados
def separar_metadados_do_texto(linha_bruta):
    # 1. Filtro de Segurança: Só processa se tiver o identificador de nova obra
    if "/pdf/" not in linha_bruta:
        return None, None

    # 2. Parsear a linha (O Segredo)
    # Usamos o csv.reader para ele lidar com as aspas e vírgulas dentro dos títulos
    f = io.StringIO(linha_bruta)
    leitor = csv.reader(f)
    colunas = next(leitor) # Transforma a linha em uma lista de campos

    # O dataset tem 17 colunas no total (0 a 16).
    # Da 0 até a 15 são Metadados.
    # A 16 (última) é o começo do texto.
    
    # 3. O Corte
    # Pega tudo exceto o último item
    lista_metadados = colunas[:-1] 
    
    # Pega só o último item (o texto que "vazou" na linha)
    inicio_texto = colunas[-1]

    # 4. Reconstrói a linha de metadados limpa (para CSV)
    output = io.StringIO()
    escritor = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
    escritor.writerow(lista_metadados)
    linha_metadados_limpa = output.getvalue().strip()

    return linha_metadados_limpa, inicio_texto

# testa o cabeçalho de metadados
def testar_metadados():
    linha_teste = 'revelacoes.pdf,./pdf/crítica/revelacoes.pdf,crítica,Machado de Assis,5,"Revelações. Poesias de A. E. Zaluar, Garnier editor, 1863.","Texto-Fonte: Crítica Literária de Machado de Assis, Rio de Janeiro: W. M. Jackson, 1938.","Publicado originalmente no Diário do Rio de Janeiro, março de 1863.",1863,Diário do Rio de Janeiro,Rio de Janeiro,1938,W. M. Jackson,Rio de Janeiro,Crítica Literária de Machado de Assis,,"Revelações. Poesias de A. E. Zaluar, Garnier editor, 1863.'

    meta, texto = separar_metadados_do_texto(linha_teste)

    print("--- 1. METADADOS PRESERVADOS (Sem o texto no final) ---")
    print(meta)

    print("\n--- 2. INÍCIO DO TEXTO (Que estava colado) ---")
    print(texto)

#separa parágrafos
def organizar_paragrafos(texto_bruto):
    # 1. Divide o texto em linhas individuais baseadas na quebra original
    linhas = texto_bruto.split('\n')
    
    paragrafos_processados = []
    buffer_paragrafo = [] # Uma "sacola" temporária para ir juntando as frases
    
    for linha in linhas:
        linha = linha.strip() # Remove espaços inúteis nas pontas
        if not linha: continue # Pula linhas vazias se houver
        
        # Adiciona a linha atual na sacola
        buffer_paragrafo.append(linha)
        
        # LÓGICA DE DECISÃO:
        # Se a linha termina com pontuação terminal (. ! ?), consideramos FIM de parágrafo.
        # (Nota: Machado usa muito ponto e vírgula, que NÃO encerra parágrafo, então só . ! ?)
        if linha.endswith(('.', '!', '?', '...')):
            # Junta tudo que está na sacola com espaços
            texto_completo = " ".join(buffer_paragrafo)
            paragrafos_processados.append(texto_completo)
            # Esvazia a sacola para o próximo parágrafo
            buffer_paragrafo = []
            
    # 2. O RESÍDUO (O parágrafo incompleto)
    # Se sobrou algo na sacola depois de ler todas as linhas, é o texto final cortado
    if buffer_paragrafo:
        texto_final = " ".join(buffer_paragrafo)
        paragrafos_processados.append(texto_final)
    
    return paragrafos_processados

#verifica se o inicio da linha é maiúscula (ignora travessões, aspas, etc)
def verificar_inicio_maiusculo(linha):
    return bool(re.match(r'^[“"\'\-\—]*\s*[A-Z]', linha))

#versão melhorada da separação de parágrafos (atenção, ele não completa parágrafos no meio, a versão um conta o parágrafo)
def organizar_paragrafos_v2(texto_bruto):
    linhas = texto_bruto.split('\n')
    paragrafos_processados = []
    buffer = []

    # Usamos um índice 'i' para poder espiar a linha 'i+1'
    i = 0
    while i < len(linhas):
        linha_atual = linhas[i].strip()
        
        if not linha_atual: 
            i += 1
            continue

        buffer.append(linha_atual)
        
        # --- A GRANDE LÓGICA ---
        # Definimos se DEVEMOS FECHAR o parágrafo agora.
        
        eh_ultima_linha = (i == len(linhas) - 1)
        termina_pontuacao = linha_atual.endswith(('.', '!', '?', '...'))
        
        # Olha para o futuro (se não for a última linha)
        proxima_comeca_maiuscula = False
        if not eh_ultima_linha:
            proxima_linha = linhas[i+1].strip()
            proxima_comeca_maiuscula = verificar_inicio_maiusculo(proxima_linha)

        # DECISÃO:
        # Só fechamos o parágrafo SE:
        # 1. Tiver pontuação final E a próxima linha começar com Maiúscula
        # 2. OU se for a última linha absoluta do texto
        if (termina_pontuacao and proxima_comeca_maiuscula) or eh_ultima_linha:
            texto_completo = " ".join(buffer)
            paragrafos_processados.append(texto_completo)
            buffer = [] # Limpa o buffer para o próximo
            
        # Se não cair no IF acima, o loop continua e a próxima linha 
        # será adicionada ao mesmo buffer (juntando as linhas)
        
        i += 1
    
    return paragrafos_processados

def organizar_paragrafos_v3(texto_bruto):
    linhas = texto_bruto.split('\n')
    paragrafos_processados = []
    buffer = []

    i = 0
    while i < len(linhas):
        linha_atual = linhas[i].strip()
        
        # Se a linha for vazia, pula, mas NÃO limpa o buffer
        # (isso permite que parágrafos atravessem linhas vazias acidentais se necessário)
        if not linha_atual: 
            i += 1
            continue

        buffer.append(linha_atual)
        
        # --- LÓGICA DE DECISÃO ---
        termina_pontuacao = linha_atual.endswith(('.', '!', '?', '...'))
        
        # Lógica de Lookahead (Olhar o futuro)
        proxima_comeca_maiuscula = False
        
        # Só olhamos a próxima se não formos a última linha da lista
        if i + 1 < len(linhas):
            proxima_linha = linhas[i+1].strip()
            # Se a próxima linha não for vazia, verificamos a maiúscula
            if proxima_linha:
                proxima_comeca_maiuscula = verificar_inicio_maiusculo(proxima_linha)

        # SE tiver pontuação final E a próxima começar com maiúscula, FECHA o parágrafo.
        # Note que removi a checagem de "ultima_linha" daqui de dentro.
        # Deixamos o final do arquivo para ser tratado fora do loop.
        if termina_pontuacao and proxima_comeca_maiuscula:
            texto_completo = " ".join(buffer)
            paragrafos_processados.append(texto_completo)
            buffer = [] # Esvazia a sacola para começar um novo

        i += 1
    
    # --- A CORREÇÃO: O RESIDUAL ---
    # Acabou o loop. Sobrou algo na sacola?
    # Isso pega o último parágrafo, seja ele um parágrafo normal 
    # ou um trecho cortado pela metade no fim do arquivo.
    if buffer:
        texto_final = " ".join(buffer)
        paragrafos_processados.append(texto_final)
    
    return paragrafos_processados

# --- TESTE ---
resultado = organizar_paragrafos_v3(texto_base)

for k, p in enumerate(resultado):
    print(f"[{k+1}] {p}")
    print("-" * 10)