Main bot. Example usage:
- Discord: type `!analyze PETR4` or `!analyze_fii KNRI11`
- Telegram: send `/analyze PETR4`

Bot will:
1) fetch data
2) compute metrics
3) create a natural-language explanation via Gemini
4) send verdict + short Gemini paragraph

import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

from fetcher import fetch_stock, fetch_fii
from analyzer import compute_pl, compute_pvp, compute_dividend_yield, compute_roe, compute_debt_ebitda, compute_cagr, decision_stock
from gcloud_client import summarize_analysis

USE_DISCORD = os.getenv('USE_DISCORD','True') == 'True'
USE_TELEGRAM = os.getenv('USE_TELEGRAM','False') == 'True'

# ===== Discord implementation (recommended) =====
if USE_DISCORD:
    import discord
    from discord.ext import commands

    intents = discord.Intents.default()
    bot = commands.Bot(command_prefix='!', intents=intents)

    @bot.event
    async def on_ready():
        print(f'Logged in as {bot.user}')

    @bot.command(name='analyze')
    async def analyze(ctx, ticker: str):
        await ctx.reply('Analisando...')
        data = fetch_stock(ticker)
        # compute some metrics
        price = data.get('price')
        # placeholders for LPA, patrimonial etc: try to extract from data
        lpa = data.get('raw_info', {}).get('regularMarketEPS')
        book = data.get('raw_info', {}).get('bookValue')
        dividend = data.get('dividendPerShare') or data.get('raw_info', {}).get('trailingAnnualDividendRate')

        pl = compute_pl(price, lpa)
        pvp = compute_pvp(price, book)
        dy = compute_dividend_yield(dividend, price)

        metrics = {'pl': pl, 'pvp': pvp, 'dividend_yield': dy}
        verdict, explanation = decision_stock(metrics)

        # synthesize with Gemini
        prompt = f"Analise resumida para {ticker}: metrics={metrics}; verdict={verdict}; reasons={explanation}."
        summary = summarize_analysis(prompt)

        embed = discord.Embed(title=f'Análise — {ticker}', description=f'Verdict: **{verdict}**')
        embed.add_field(name='Resumo Gemini', value=summary[:1024], inline=False)
        embed.add_field(name='Detalhes', value=explanation or 'Sem dados suficientes', inline=False)
        await ctx.send(embed=embed)

    # start bot
    if __name__ == '__main__':
        TOKEN = os.getenv('DISCORD_TOKEN')
        bot.run(TOKEN)

# ===== Telegram implementation (optional) =====
if USE_TELEGRAM and not USE_DISCORD:
    from telegram import Update
    from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

    async def analyze_telegram(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text('Use: /analyze TICKER')
            return
        ticker = context.args[0]
        await update.message.reply_text('Analisando...')
        data = fetch_stock(ticker)
        price = data.get('price')
        lpa = data.get('raw_info', {}).get('regularMarketEPS')
        book = data.get('raw_info', {}).get('bookValue')
        dividend = data.get('dividendPerShare')

        pl = compute_pl(price, lpa)
        pvp = compute_pvp(price, book)
        dy = compute_dividend_yield(dividend, price)

        metrics = {'pl': pl, 'pvp': pvp, 'dividend_yield': dy}
        verdict, explanation = decision_stock(metrics)
        prompt = f"Analise resumida para {ticker}: metrics={metrics}; verdict={verdict}; reasons={explanation}."
        summary = summarize_analysis(prompt)

        text = f"{ticker}\nVerdict: {verdict}\n\n{explanation}\n\nGemini:\n{summary[:1000]}"
        await update.message.reply_text(text)

    if __name__ == '__main__':
        TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
        app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        app.add_handler(CommandHandler('analyze', analyze_telegram))
        app.run_polling()
