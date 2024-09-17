import os
import asyncio
import time
import pickle
import psutil
import talib
import pandas as pd
from binance.client import Client
from binance.exceptions import BinanceAPIException
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, CallbackContext
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Carregar as credenciais da API de forma segura
API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Verificar se todas as variáveis de ambiente estão presentes
if not API_KEY or not API_SECRET or not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    raise ValueError("Uma ou mais variáveis de ambiente estão faltando. Verifique o arquivo .env.")

# Inicializar os clientes de Binance e Telegram
client = Client(API_KEY, API_SECRET)
bot = Bot(token=TELEGRAM_TOKEN)
app = Application.builder().token(TELEGRAM_TOKEN).build()

# Variável global para controle de análise
analise_ativa = False

# Função de monitoramento de recursos do sistema
def monitorar_recursos():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()
    print(f"Uso de CPU: {cpu_usage}% | Uso de Memória: {memory_info.percent}%")

# Função de backup do estado do bot
def salvar_estado(dados, arquivo='estado_bot.pkl'):
    with open(arquivo, 'wb') as f:
        pickle.dump(dados, f)

# Função de recuperação do estado
def carregar_estado(arquivo='estado_bot.pkl'):
    try:
        with open(arquivo, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None

# Função para garantir que o bot respeite os limites de taxa da API
def garantir_limite_de_taxa():
    time.sleep(1)  # Espera para respeitar o rate limit

# Função de envio de alertas no Telegram
async def enviar_alerta_erro(erro):
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"⚠️ Erro detectado: {erro}")

# Função para obter dados históricos da Binance
def obter_dados_históricos(symbol, intervalo='1h', limite=500):
    klines = client.get_historical_klines(symbol, intervalo, f"{limite} hours ago UTC")
    df = pd.DataFrame(klines, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df = df.astype(float)
    return df

# Função para calcular indicadores técnicos
def calcular_indicadores(df, parametros):
    df['rsi'] = talib.RSI(df['close'], timeperiod=parametros['rsi_period'])
    df['macd'], df['macd_signal'], df['macd_hist'] = talib.MACD(
        df['close'],
        fastperiod=parametros['macd_fast'],
        slowperiod=parametros['macd_slow'],
        signalperiod=parametros['macd_signal']
    )
    df['bollinger_upper'], df['bollinger_middle'], df['bollinger_lower'] = talib.BBANDS(
        df['close'],
        timeperiod=parametros['bollinger_window'],
        nbdevup=parametros['bollinger_std'],
        nbdevdn=parametros['bollinger_std'],
        matype=0
    )
    return df

# Função para identificar padrões de velas
def identificar_padroes_velas(df):
    df['doji'] = talib.CDLDOJI(df['open'], df['high'], df['low'], df['close'])
    df['martelo'] = talib.CDLMORNINGDOJISTAR(df['open'], df['high'], df['low'], df['close'])
    return df

# Função para calcular o volume médio
def calcular_volume(df):
    df['media_volume'] = df['volume'].rolling(window=20).mean()
    return df

# Função para ajustar parâmetros do bot para cada criptomoeda
def ajustar_parametros(symbol):
    return {
        'rsi_period': 7,
        'macd_fast': 8,
        'macd_slow': 17,
        'macd_signal': 9,
        'bollinger_window': 14,
        'bollinger_std': 1.5
    }

# Função para realizar análise periódica de criptomoedas
async def executar_analise_para_simbolo(symbol):
    global analise_ativa
    while True:
        if analise_ativa:
            try:
                print(f"Iniciando análise para {symbol}...")
                parametros_otimizados = ajustar_parametros(symbol)
                df = obter_dados_históricos(symbol, intervalo='1h')
                df = calcular_indicadores(df, parametros_otimizados)
                df = identificar_padroes_velas(df)
                df = calcular_volume(df)

                # Verifique se a coluna 'macd_signal' está no DataFrame
                if 'macd_signal' not in df.columns:
                    await enviar_alerta_erro(f"Coluna 'macd_signal' não encontrada no DataFrame para {symbol}.")
                    continue

                preco_atual = client.get_symbol_ticker(symbol=symbol)['price']
                ultima_linha = df.iloc[-1]
                mensagem = ""

                # Confirmação de Compra
                if (ultima_linha['rsi'] < 30 and
                    ultima_linha['macd'] > ultima_linha['macd_signal'] and
                    ultima_linha['doji'] != 0 and
                    ultima_linha['volume'] > ultima_linha['media_volume']):
                    
                    mensagem = (f"🔔 Sinal de Compra para {symbol}:\n"
                                f"Preço Atual: {preco_atual}\n"
                                f"RSI: {ultima_linha['rsi']}\n"
                                f"MACD: {ultima_linha['macd']} | Signal: {ultima_linha['macd_signal']}\n"
                                f"Bollinger Bands: {ultima_linha['bollinger_upper']} | {ultima_linha['bollinger_middle']} | {ultima_linha['bollinger_lower']}\n"
                                f"Padrão de Velas: Doji\n"
                                f"Volume: {ultima_linha['volume']} (Acima da Média)\n")
                
                # Confirmação de Venda
                elif (ultima_linha['rsi'] > 70 and
                      ultima_linha['macd'] < ultima_linha['macd_signal'] and
                      ultima_linha['martelo'] != 0 and
                      ultima_linha['volume'] > ultima_linha['media_volume']):
                    
                    mensagem = (f"🔔 Sinal de Venda para {symbol}:\n"
                                f"Preço Atual: {preco_atual}\n"
                                f"RSI: {ultima_linha['rsi']}\n"
                                f"MACD: {ultima_linha['macd']} | Signal: {ultima_linha['macd_signal']}\n"
                                f"Bollinger Bands: {ultima_linha['bollinger_upper']} | {ultima_linha['bollinger_middle']} | {ultima_linha['bollinger_lower']}\n"
                                f"Padrão de Velas: Martelo\n"
                                f"Volume: {ultima_linha['volume']} (Acima da Média)\n")

                if mensagem:
                    print(f"Enviando mensagem: {mensagem}")  # Log da mensagem
                    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=mensagem)
                else:
                    print("Nenhuma sinalização para enviar.")

                await asyncio.sleep(300)  # Espera 5 minutos para a próxima análise
            except BinanceAPIException as e:
                await enviar_alerta_erro(e)
                print(f"Erro na API da Binance: {e}")
                await asyncio.sleep(60)
            except Exception as e:
                await enviar_alerta_erro(e)
                print(f"Erro desconhecido: {e}")
                await asyncio.sleep(60)
        else:
            await asyncio.sleep(10)  # Espera e checa se a análise foi reativada

# Funções para comandos no bot
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Bem-vindo ao bot de análise de criptomoedas!")

async def iniciar_analise(update: Update, context: CallbackContext):
    global analise_ativa
    simbolo = context.args[0].upper()
    if not analise_ativa:
        analise_ativa = True
        asyncio.create_task(executar_analise_para_simbolo(simbolo))
        await update.message.reply_text(f"Análise iniciada para {simbolo}.")
    else:
        await update.message.reply_text("A análise já está em andamento.")

async def parar_analise(update: Update, context: CallbackContext):
    global analise_ativa
    if analise_ativa:
        analise_ativa = False
        await update.message.reply_text("Análise parada.")
    else:
        await update.message.reply_text("Nenhuma análise está ativa no momento.")

# Função principal para configurar e rodar o bot
def main():
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("iniciar_analise", iniciar_analise))
    app.add_handler(CommandHandler("parar_analise", parar_analise))
    
    print("Bot iniciado.")
    app.run_polling()

if __name__ == "__main__":
    main()
