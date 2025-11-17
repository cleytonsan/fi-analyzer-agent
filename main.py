import os
import discord
from discord.ext import commands
from google import genai
from google.genai import types

# 1. Variáveis de Ambiente (Keys)
# Substitua os placeholders abaixo pelas suas chaves!
# Mantenha as chaves secretas, nunca suba a chave real para o GitHub.
# Para este guia inicial, vamos colocá-las aqui, mas o ideal é usar um arquivo .env.
DISCORD_TOKEN = "SEU_TOKEN_DO_BOT_DISCORD"  # Token do Passo 2.1
GEMINI_API_KEY = "SUA_CHAVE_DE_API_GEMINI"  # Chave do Passo 3

# 2. Configuração do Bot Discord
intents = discord.Intents.default()
intents.message_content = True # Permite ler o conteúdo das mensagens
bot = commands.Bot(command_prefix='!', intents=intents)

# 3. Configuração do Cliente Gemini
genai.configure(api_key=GEMINI_API_KEY)
client = genai.Client()
model_name = 'gemini-2.5-flash'

# 4. Prompt de Sistema (A "Personalidade" do Agente)
# Este é o texto que define o que a IA deve fazer, incluindo as regras de análise que você forneceu.
SYSTEM_PROMPT = """
Você é um 'Agente de Análise de Investimentos'. Sua função é analisar ações (stocks) e Fundos de Investimento Imobiliário (FIIs) com base nos critérios que o usuário fornecer e em dados financeiros que você pode buscar.

O usuário irá enviar uma sigla (ticker) e perguntar se é bom para comprar.

**Sua Resposta deve ser estruturada e objetiva:**
1.  **Buscar dados financeiros e de mercado** atuais para a sigla fornecida (como P/L, P/VP, Dividend Yield, Endividamento, etc.). Use sua função de busca para isso.
2.  **Análise de Ações:**
    * **Preço e Indicadores:** P/L (quanto menor, melhor), P/VP (quanto mais baixo, melhor), DIVIDEND YIELD (constância e valor em relação ao preço).
    * **Saúde Financeira:** Lucratividade (ROE alto e consistente), Endividamento (Dívida Líquida/EBITDA, idealmente abaixo de 3x).
    * **Crescimento:** CARG Lucro (crescimento com juros compostos).
    * **Governança:** Mencionar a importância da Resolução CVM 44 (executivos comprando/vendendo).
3.  **Análise de FIIs:**
    * **Patrimônio:** Patrimônio Líquido > R$ 1 Bilhão.
    * **P/VP:** Quanto mais baixo, melhor (indica que está barato).
    * **Dividendos:** Pagamento constante.
    * **Diversificação:** Multi-imóveis, multi-estados, multi-inquilinos.
4.  **Conclusão:** Termine com uma resposta clara: **"De acordo com a análise, [SIGLA] é uma [BOA/MÁ] oportunidade de compra no momento."** e uma breve justificativa.

**IMPORTANTE:** Você deve sempre usar sua ferramenta de busca para obter informações atuais sobre o ativo antes de analisar.
"""

# 5. Evento de Inicialização do Bot
@bot.event
async def on_ready():
    print(f'🤖 Bot conectado como {bot.user}')
    # Define o status do bot no Discord
    await bot.change_presence(activity=discord.Game(name="Analisando Ativos 📈"))

# 6. Comando Principal de Análise
@bot.command(name='analisar')
async def analisar(ctx, sigla: str):
    """Analisa uma sigla de ação ou FII usando a IA Gemini."""
    
    # Informa ao usuário que a análise começou
    await ctx.send(f"⏳ **{ctx.author.name}**, estou buscando e analisando os dados de **{sigla.upper()}**... Aguarde um momento. ")
    
    try:
        # Cria a requisição com o prompt e a ferramenta de busca (Google Search)
        response = client.models.generate_content(
            model=model_name,
            contents=f"Analise o ativo **{sigla.upper()}** de acordo com as regras de análise que me foram dadas. A pergunta do usuário é: 'Essa sigla {sigla.upper()} é boa para comprar?'. Use a ferramenta de busca para encontrar os dados necessários.",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                tools=[{"google_search": {}}] # Ativa a busca do Google
            ),
        )

        # Envia a resposta da IA de volta para o Discord
        await ctx.send(f"📈 **Análise de {sigla.upper()}**\n\n{response.text}")

    except Exception as e:
        print(f"Erro na análise: {e}")
        await ctx.send("❌ **Ocorreu um erro ao processar a análise.** Certifique-se de que a sigla está correta e que minhas chaves de API estão configuradas corretamente. (Erro: {e})")

# 7. Inicializa o Bot
if __name__ == "__main__":
    # Garante que as chaves foram substituídas antes de rodar.
    if DISCORD_TOKEN == "SEU_TOKEN_DO_BOT_DISCORD" or GEMINI_API_KEY == "SUA_CHAVE_DE_API_GEMINI":
        print("\n!!! ATENÇÃO: Substitua DISCORD_TOKEN e GEMINI_API_KEY no arquivo main.py antes de executar. !!!\n")
    else:
        bot.run(DISCORD_TOKEN)
      
