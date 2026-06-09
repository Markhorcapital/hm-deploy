# PMM Dynamic Configuration Tool (DEX/CEX)

Create, preview, backtest (CEX approximation), and save configurations for the **DEX/CEX asymmetric** PMM Dynamic strategy.

## Strategy Overview

The controller quotes on a CEX using two price anchors:

- **cex_mid** — mid of the market-making pair (e.g. ALI-USDT on MEXC)
- **dex_fair** — Uniswap V3 pool TWAP × CEX ETH/USDT mid

When `dex_cex_log_only` is **false**, Regime A/B quoting is active:

| Regime | Condition | Buy anchor | Sell anchor |
|--------|-----------|------------|-------------|
| **A** | `cex_mid > dex_fair` | `dex_fair` | `cex_mid` |
| **B** | `dex_fair > cex_mid` | `cex_mid` | `dex_fair` |

Spreads are decimals (e.g. `0.001` = 0.1%): `buy = anchor × (1 - spread)`, `sell = anchor × (1 + spread)`.

## Configuration Sections

### General (shared)

- Connector, trading pair, leverage, total quote amount
- Executor refresh / cooldown
- Triple-barrier risk management (stop loss, take profit, time limit, trailing stop)

### DEX Price Feed

- **Ethereum RPC URL** — or set `DEX_RPC_URL` / `WEB3_PROVIDER` on the bot container
- **Pool & token addresses** — Uniswap V3 pool and base/quote tokens
- **CEX ETH/USDT pair** — conversion leg on the same connector
- **Poll interval, TWAP window, stale timeout, sanity divergence**

### Regime A/B

- **Hysteresis (bps)** — minimum |basis| to switch regime (50 = 0.5%)
- **Confirm ticks** — consecutive polls beyond threshold before switching
- **Log-only mode** — CEX mid ± spreads while logging dex_fair/regime (soak phase)
- **Debug logging** — verbose DEX/CEX feed and order-path logs

### Spreads & Amounts

- Buy/sell spread levels as **decimals** (same as PMM Simple)
- Per-level amount percentages

## Page Features

1. **Load default / existing config** from the Backend API
2. **Regime quote preview** — enter hypothetical cex_mid and dex_fair to see inferred regime and L0 prices
3. **CEX candle chart** — historical reference for the MM pair
4. **Executor distribution** — visualize spread levels and capital allocation
5. **Backtesting** — CEX-only approximation (does not simulate on-chain DEX TWAP)
6. **Save config** for deployment via Bot Orchestration

## Deployment Notes

- Ensure the bot image includes the DEX/CEX controller and `dex_price_feed` dependencies (web3).
- Set `DEX_RPC_URL` in the bot environment if you leave RPC URL blank in the saved config.
- Start with `dex_cex_log_only: true` to validate the feed before enabling live Regime quoting.
