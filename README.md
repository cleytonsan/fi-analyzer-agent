# fi-analyzer-agent

"""
Fi Analyzer Agent
=================
Agent that analyzes Brazilian stocks (Ações) and real estate funds (FIIs) using Google Generative AI
and market data, reachable via Discord or Telegram.

Primary design decisions (opinionated):
- Use Discord as the primary channel: richer interaction, embeds, and easier moderation of rate limits.
- Use yfinance for quick market data and Alpha Vantage as a fallback for fundamental indicators.
- Use Google Generative AI (Gemini) to synthesize explanations and generate natural-language recommendations.

Setup summary (high-level):
1. Create GitHub repo and add files.
2. Fill .env with your API keys (GOOGLE_API_KEY, ALPHAVANTAGE_KEY, DISCORD_TOKEN, TELEGRAM_TOKEN optional).
3. Deploy to Railway / Replit / run locally (Termux on mobile).
