import json
import transformers
from transformers import AutoTokenizer

# --- CONFIGURAÇÃO ---
# Nome do modelo para carregar o tokenizador correto
MODEL_NAME = "pierreguillou/gpt2-small-portuguese"
arquivos = {
    "Treino": "train_machado.jsonl",
    "Validação": "validation_machado.jsonl",
    "Teste": "test_machado.jsonl"
}

def contar_tokens_dataset():
    print(f"Carregando tokenizador: {MODEL_NAME}...")
    try:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    except:
        # Fallback caso não tenha internet ou acesso direto, tenta usar o local se tiver
        tokenizer = AutoTokenizer.from_pretrained("./machado-gpt2-finetuned")

    total_geral = 0
    resultados = {}

    print("\nIniciando contagem (pode levar alguns segundos)...")
    print("-" * 50)

    for split, nome_arquivo in arquivos.items():
        contagem_split = 0
        try:
            with open(nome_arquivo, 'r', encoding='utf-8') as f:
                for linha in f:
                    # Lê o JSON da linha
                    obj = json.loads(linha)
                    texto = obj['text']
                    
                    # Tokeniza e conta
                    # len(tokenizer.encode(texto)) conta os tokens (palavras/subpalavras)
                    tokens = tokenizer.encode(texto)
                    contagem_split += len(tokens)
            
            resultados[split] = contagem_split
            total_geral += contagem_split
            print(f"✅ {split}: {contagem_split:,} tokens processados.")
            
        except FileNotFoundError:
            print(f"❌ {split}: Arquivo '{nome_arquivo}' não encontrado.")
            resultados[split] = 0

    print("-" * 50)
    print("\n=== RELATÓRIO FINAL DE DISTRIBUIÇÃO ===")
    
    if total_geral == 0:
        print("Nenhum dado encontrado.")
        return

    for split, qtd in resultados.items():
        porcentagem = (qtd / total_geral) * 100
        print(f"{split.ljust(10)}: {qtd:10,} tokens | {porcentagem:.2f}% do total")

    print("-" * 50)
    print(f"TOTAL GERAL: {total_geral:,} tokens")

# Executa o contador
contar_tokens_dataset()