"""Pure helpers for DEX/CEX regime preview on the config page (no Hummingbot imports)."""
from __future__ import annotations

from decimal import Decimal
from typing import Literal, Optional

Regime = Literal["A", "B"]


def compute_basis_pct(cex_mid: Decimal, dex_fair: Decimal) -> Optional[Decimal]:
    if dex_fair is None or dex_fair <= 0:
        return None
    return (cex_mid - dex_fair) / dex_fair


def infer_regime(basis_pct: Optional[Decimal], hysteresis_bps: int) -> Optional[Regime]:
    if basis_pct is None:
        return None
    threshold = Decimal(hysteresis_bps) / Decimal(10000)
    if basis_pct > threshold:
        return "A"
    if basis_pct < -threshold:
        return "B"
    if basis_pct > 0:
        return "A"
    if basis_pct < 0:
        return "B"
    return None


def compute_regime_order_price(
    regime: Regime,
    is_buy: bool,
    spread: Decimal,
    cex_mid: Decimal,
    dex_fair: Decimal,
) -> Decimal:
    if regime == "A":
        anchor = dex_fair if is_buy else cex_mid
    else:
        anchor = cex_mid if is_buy else dex_fair
    side_mult = Decimal("-1") if is_buy else Decimal("1")
    return anchor * (1 + side_mult * spread)


def compute_level_prices(
    cex_mid: Decimal,
    dex_fair: Decimal,
    buy_spreads: list,
    sell_spreads: list,
    regime: Optional[Regime],
) -> dict:
    if regime is None:
        return {}
    result = {}
    for i, spread in enumerate(buy_spreads):
        result[f"L{i} buy"] = compute_regime_order_price(
            regime, True, Decimal(str(spread)), cex_mid, dex_fair
        )
    for i, spread in enumerate(sell_spreads):
        result[f"L{i} sell"] = compute_regime_order_price(
            regime, False, Decimal(str(spread)), cex_mid, dex_fair
        )
    return result
