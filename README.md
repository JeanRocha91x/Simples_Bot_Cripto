# Trader Bot Telegram

## Descrição

O Trader Bot Telegram é um bot para análise técnica de criptomoedas que utiliza a API da Binance para obter dados de mercado e a API do Telegram para enviar sinais de compra e venda para o usuário. Ele analisa indicadores técnicos como RSI, MACD, Bollinger Bands e padrões de velas para fornecer sinais de entrada e saída no mercado de criptomoedas.

## Funcionalidades

- **Análise Técnica**: Calcula RSI, MACD, Bollinger Bands e padrões de velas.
- **Sinais de Compra e Venda**: Envia sinais de compra e venda baseados na análise dos indicadores.
- **Controle de Análise**: Inicia e para a análise de criptomoedas através de comandos no Telegram.

## Requisitos

- Python 3.8 ou superior
- Conta na Binance com API Key e Secret
- Conta no Telegram para criar um bot e obter o token

## Instalação

Siga os passos abaixo para instalar e configurar o bot no Ubuntu 22.04:

### 1. Atualize o sistema

```bash
sudo apt update
```
```bash
sudo apt upgrade
```

### 2. Instale o Python e o pip

```bash
sudo apt install python3 python3-pip
```

### 3. Clone o repositório
Substitua <URL_DO_REPOSITORIO> pela URL do seu repositório GitHub.

```bash
git clone https://raw.githubusercontent.com/JeanRocha91x/Simples_Bot_Cripto/main/bot.py
```
```bash
cd <NOME_DO_REPOSITORIO>
```

### 4. Crie um ambiente virtual
```bash
python3 -m venv botenv
```
```bash
source botenv/bin/activate
```

### 5. Instale as dependências
```bash
pip install -r requirements.txt
```

### 6. Configure as variáveis de ambiente
Crie um arquivo .env na raiz do projeto com as seguintes variáveis:
```bash
BINANCE_API_KEY=YOUR_BINANCE_API_KEY
BINANCE_API_SECRET=YOUR_BINANCE_API_SECRET
TELEGRAM_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID=YOUR_TELEGRAM_CHAT_ID
```
Substitua **YOUR_BINANCE_API_KEY**, **YOUR_BINANCE_API_SECRET**, **YOUR_TELEGRAM_BOT_TOKEN** e **YOUR_TELEGRAM_CHAT_ID** pelos valores correspondentes.

### 7. Execute o bot
```bash
python bot.py
```

## Comandos do Bot

1. **Iniciar Análise**: Quando você envia o comando /iniciar_analise <SIMBOLO>, o bot começa a analisar a criptomoeda especificada. Ele realiza análises técnicas periodicamente e envia sinais de compra e venda para o chat do Telegram.

2. **Parar Análise**: O comando /parar_analise interrompe a análise em andamento.

3. **Análise Técnica**: O bot utiliza a API da Binance para obter dados históricos das criptomoedas e calcula indicadores técnicos como RSI, MACD, Bollinger Bands e padrões de velas. Com base nesses cálculos, o bot envia sinais de compra e venda quando detecta oportunidades.

4. **Envio de Alertas**: Se um erro for detectado durante a execução, o bot enviará uma mensagem de alerta para o chat do Telegram.

## Funcionamento

- **/start**: Inicia uma conversa com o bot e envia uma mensagem de boas-vindas.
- **/iniciar_analise <SIMBOLO>**: Inicia a análise para a criptomoeda especificada. Exemplo: **/iniciar_analise BTCUSDC**
- **/parar_analise**: Para a análise em andamento.

## Contribuições
Contribuições são bem-vindas! Sinta-se à vontade para enviar pull requests ou abrir issues para sugestões e melhorias.

## Licença
Este projeto está licenciado sob a MIT License.
