# MachadoGPT: Um Modelo de Linguagem no Estilo de Machado de Assis 🎩

Este repositório contém os códigos utilizados para realizar o fine-tuning do modelo GPT-2 Small em toda a obra literária de Machado de Assis. O objetivo foi criar uma IA capaz de gerar textos imitando o estilo, vocabulário e sintaxe do autor brasileiro.

## 📂 Download e Instalação do Modelo

Como o GitHub possui limite de tamanho de arquivos, o modelo treinado está hospedado externamente.

### Passo 1: Baixar
👉 **[CLIQUE AQUI PARA BAIXAR O MODELO (Google Drive)](https://drive.google.com/file/d/1IxI2T9obotUj95ks53MYMfrTa167Cg_8/view?usp=sharing)**

### Passo 2: Organizar a Pasta
Após baixar o arquivo `.zip`, extraia o conteúdo. Você deve garantir que a pasta descompactada (vamos chamá-la de `ModeloFinal`) contenha os seguintes arquivos essenciais:

```text
ModeloFinal/
├── config.json              (Configuração da arquitetura)
├── generation_config.json   (Parâmetros de geração)
├── model.safetensors        (Os pesos da Rede Neural - Aprox. 500MB)
├── vocab.json               (O vocabulário do modelo)
└── merges.txt               (Regras de tokenização)