"""
Compute PL, P/VP, Dividend Yield, ROE, Debt ratios, CAGR and decision logic.
Return both numerical results and a short recommendation (BUY / AVOID / HOLD) with reasons.
"""
from typing import Dict, Tuple
import math


def safe_div(a, b):
    try:
        return None if b in (0, None) else float(a) / float(b)
    except Exception:
        return None


def compute_pl(price, lpa):
    return safe_div(price, lpa)


def compute_pvp(price, book_value_per_share):
    return safe_div(price, book_value_per_share)


def compute_dividend_yield(dividend_per_share, price):
    val = safe_div(dividend_per_share, price)
    return None if val is None else val * 100


def compute_roe(net_income, equity):
    val = safe_div(net_income, equity)
    return None if val is None else val * 100


def compute_debt_ebitda(net_debt, ebitda):
    return safe_div(net_debt, ebitda)


def compute_cagr(current, past, years):
    try:
        if past is None or past <= 0:
            return None
        return ( (current / past) ** (1/years) - 1 ) * 100
    except Exception:
        return None


def decision_stock(metrics: Dict) -> Tuple[str, str]:
    """Return (verdict, explanation)"""
    reasons = []
    score = 0

    # PL
    pl = metrics.get('pl')
    if pl is not None:
        if pl < 10:
            score += 2; reasons.append(f'P/L baixo ({pl:.2f})')
        elif pl < 20:
            score += 1; reasons.append(f'P/L moderado ({pl:.2f})')
        else:
            score -= 1; reasons.append(f'P/L alto ({pl:.2f})')

    # P/VP
    pvp = metrics.get('pvp')
    if pvp is not None:
        if pvp < 1:
            score += 2; reasons.append(f'P/VP < 1 ({pvp:.2f})')
        elif pvp < 2:
            score += 1; reasons.append(f'P/VP razoável ({pvp:.2f})')
        else:
            score -= 1; reasons.append(f'P/VP alto ({pvp:.2f})')

    # Dividend yield
    dy = metrics.get('dividend_yield')
    if dy is not None:
        if dy >= 6:
            score += 2; reasons.append(f'Dividend yield alto ({dy:.2f}%)')
        elif dy >= 3:
            score += 1; reasons.append(f'Dividend yield razoável ({dy:.2f}%)')
        else:
            reasons.append(f'Dividend yield baixo ({dy:.2f}%)')

    # ROE
    roe = metrics.get('roe')
    if roe is not None:
        if roe >= 15:
            score += 2; reasons.append(f'ROE forte ({roe:.2f}%)')
        elif roe >= 8:
            score += 1; reasons.append(f'ROE satisfatório ({roe:.2f}%)')
        else:
            reasons.append(f'ROE fraco ({roe:.2f}%)')

    # Debt / EBITDA
    debt_ebitda = metrics.get('debt_ebitda')
    if debt_ebitda is not None:
        if debt_ebitda <= 3:
            score += 2; reasons.append(f'Endividamento saudável ({debt_ebitda:.2f}x)')
        elif debt_ebitda <= 5:
            reasons.append(f'Endividamento alto ({debt_ebitda:.2f}x)')
        else:
            score -= 2; reasons.append(f'Endividamento muito alto ({debt_ebitda:.2f}x)')

    # CAGR
    cagr = metrics.get('cagr')
    if cagr is not None:
        if cagr >= 10:
            score += 2; reasons.append(f'Crescimento consistente ({cagr:.2f}%)')
        elif cagr >= 3:
            score += 1; reasons.append(f'Crescimento moderado ({cagr:.2f}%)')
        else:
            reasons.append(f'Crescimento fraco ({cagr:.2f}%)')

    # Governance and CVM insider trades are qualitative; placeholder adjustments
    if metrics.get('insider_buyers'):
        score += 1; reasons.append('Executivos comprando ações (sinal positivo)')
    if metrics.get('insider_sellers'):
        score -= 1; reasons.append('Executivos vendendo ações (atenção)')

    # final mapping
    if score >= 5:
        verdict = 'STRONG BUY'
    elif score >= 2:
        verdict = 'BUY'
    elif score >= 0:
        verdict = 'HOLD'
    else:
        verdict = 'AVOID'

    explanation = '; '.join(reasons)
    return verdict, explanation

