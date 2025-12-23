import re

texto_sujo = """
CAPÍTULO I

Havia naquelas paragens uma certa incom-
preensão sobre o que se passava. O tempo
corria devagar.

CAPÍTULO II

Mas a verdade é que Machado, ou melhor,
o Bruxo do Cosme Velho, sabia das coi-
sas.
"""

print("--- TEXTO ORIGINAL ---")
print(texto_sujo)
print("----------------------\n")

# --- INÍCIO DA LIMPEZA PASSO A PASSO ---

# PASSO 1: Remover linhas de Títulos (Caixa Alta e curtas)
# Como você pediu: remover nomes de capítulos.
linhas = texto_sujo.split('\n')
linhas_filtradas = []

for linha in linhas:
    linha_limpa = linha.strip() # Remove espaços extras nas pontas
    
    # Se for vazia, mantemos (por enquanto) para saber onde são os parágrafos
    if not linha_limpa:
        linhas_filtradas.append("")
        continue
        
    # A Lógica do Filtro: Se for TUDO MAIÚSCULA e menor que 50 chars -> Lixo
    if linha_limpa.isupper() and len(linha_limpa) < 50:
        print(f"-> Removendo título detectado: {linha_limpa}")
        continue # Pula essa linha, não adiciona na lista final
        
    linhas_filtradas.append(linha)

# Junta tudo de volta com \n para continuar processando o texto inteiro
texto = '\n'.join(linhas_filtradas)

# PASSO 2: Corrigir Hifenização (O pesadelo do PDF)
# Regex explicada:
# (\w+)  -> Pega uma palavra (Grupo 1)
# -\s*\n -> Pega um hífen seguido de possível espaço e quebra de linha
# \s* -> Pega possíveis espaços no início da próxima linha
# (\w+)  -> Pega a continuação da palavra (Grupo 2)
# Substitui por: \1\2 (Junta Grupo 1 e 2 sem nada no meio)
texto = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', texto)

# PASSO 3: Arrumar os parágrafos (Juntar linhas quebradas)
# Truque: Geralmente parágrafos reais são separados por uma linha vazia (\n\n)
# Mas frases quebradas no PDF são separadas por apenas um enter (\n)

# Marcamos onde são os parágrafos REAIS com uma tag temporária
texto = re.sub(r'\n\s*\n', '<<PARAGRAFO>>', texto)

# Agora, qualquer \n que sobrou é "falso" (quebra de linha do PDF). Trocamos por espaço.
texto = texto.replace('\n', ' ')

# Removemos espaços duplos que podem ter surgido
texto = re.sub(r' +', ' ', texto)

# Restauramos os parágrafos.
# AQUI ESTÁ SUA ESCOLHA DE ESTILO:
# Opção A: Para leitura humana (com linha em branco entre eles) use '\n\n'
# Opção B: Para "uma linha por parágrafo" (dataset puro) use '\n'
texto_final = texto.replace('<<PARAGRAFO>>', '\n\n').strip()

print("\n--- RESULTADO FINAL ---")
print(texto_final)