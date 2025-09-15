import streamlit as st

# -------------------
# Page Config
# -------------------
st.set_page_config(page_title="Pip & Profit Calculator", page_icon="💹", layout="centered")
st.title("💹 Forex, Gold & Crypto Profit Calculator")


# -------------------
# Inputs
# -------------------

cola, colb = st.columns(2)
with cola:
    opening_price = st.number_input("Enter the opening price:", min_value=0.0, format="%.5f")
with colb:
    closing_price = st.number_input("Enter the closing price:", min_value=0.0, format="%.5f")


lot_size = st.number_input("Enter the Lot Size (standard lot = 1 = 100,000 units):", min_value=0.0, format="%.4f")
trade_type = st.radio("Select Trade Type:", ["Buy", "Sell"])

pairs = [
    "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "USDCAD", "AUDUSD", "NZDUSD",
    "EURJPY", "GBPJPY", "EURGBP", "AUDJPY", "CADJPY", "CHFJPY",
    "EURAUD", "GBPAUD", "AUDCAD", "NZDJPY",
    "XAUUSD", "BTCUSD"
]
pair = st.selectbox("Choose a Pair:", pairs)

st.write("---")

# -------------------
# Calculation
# -------------------
def calculate_profit(opening_price, closing_price, lot_size, pair, trade_type):
    # adjust sign/direction
    if trade_type == "Buy":
        diff = closing_price - opening_price
    else:
        diff = opening_price - closing_price

    # helper defaults
    pips = 0.0
    pip_size = None
    units = None
    profit = None
    profit_currency = None
    note = ""

    # Metals / Crypto (profit in USD)
    if pair == "XAUUSD":
        pip_size = 0.10            # $0.10 per pip (common convention here)
        units = lot_size * 100     # 1 standard lot = 100 oz (adjust if your broker differs)
        pips = diff / pip_size
        pip_value = pip_size * units    # already in USD
        profit = pips * pip_value
        profit_currency = "USD"

    elif pair == "BTCUSD":
        pip_size = 0.01
        units = lot_size * 1
        pips = diff / pip_size
        pip_value = pip_size * units
        profit = pips * pip_value
        profit_currency = "USD"

    # FX pairs where USD is the quote (e.g., EURUSD, GBPUSD) -> pip value in USD
    elif pair.endswith("USD"):
        pip_size = 0.0001 if "JPY" not in pair else 0.01
        units = lot_size * 100000
        pips = diff / pip_size
        pip_value = pip_size * units     # pip value directly in USD
        profit = pips * pip_value
        profit_currency = "USD"

    # FX pairs where USD is the base (e.g., USDJPY, USDCHF, USDCAD)
    # pip_value is in the quote currency (JPY/CHF/CAD) -> convert to USD by dividing by mid price
    elif pair.startswith("USD"):
        pip_size = 0.01 if "JPY" in pair else 0.0001
        units = lot_size * 100000
        pips = diff / pip_size
        pip_value_in_quote = pip_size * units   # in quote currency (e.g., JPY)
        # use mid price to convert quote -> USD (guard zero)
        mid_price = None
        if opening_price > 0 and closing_price > 0:
            mid_price = (opening_price + closing_price) / 2.0
        elif closing_price > 0:
            mid_price = closing_price
        elif opening_price > 0:
            mid_price = opening_price

        if not mid_price or mid_price == 0:
            profit = None
            note = "Can't convert quote currency to USD because price is zero or missing."
            profit_currency = pair[3:]
        else:
            pip_value = pip_value_in_quote / mid_price   # converted to USD
            profit = pips * pip_value
            profit_currency = "USD"
            note = f"Converted pip value from {pair[3:]} → USD using mid price {mid_price:.6f}."

    # JPY quote-crosses not involving USD (e.g., EURJPY, GBPJPY) -> pip value in JPY
    elif "JPY" in pair:
        pip_size = 0.01
        units = lot_size * 100000
        pips = diff / pip_size
        pip_value = pip_size * units         # in JPY
        profit = pips * pip_value
        profit_currency = "JPY"
        note = "Profit is shown in JPY. Add a JPY→USD conversion if you want USD."

    # Other crosses (quote not USD/JPY) -> profit in quote currency
    else:
        pip_size = 0.0001
        units = lot_size * 100000
        pips = diff / pip_size
        pip_value = pip_size * units
        profit = pips * pip_value
        profit_currency = pair[3:]
        note = f"Profit is shown in {profit_currency}. Add conversion to USD if required."

    return {
        "pips": pips,
        "profit": profit,
        "pip_size": pip_size,
        "units": units,
        "profit_currency": profit_currency,
        "note": note
    }

# -------------------
# UI: compute & show
# -------------------
if st.button("📊 Calculate"):
    if opening_price <= 0 or closing_price <= 0 or lot_size <= 0:
        st.warning("⚠️ Please enter positive Opening, Closing prices and Lot size.")
    else:
        out = calculate_profit(opening_price, closing_price, lot_size, pair, trade_type)
        pips = out["pips"]
        profit = out["profit"]
        pip_size = out["pip_size"]
        units = out["units"]
        currency = out["profit_currency"]
        note = out["note"]

        if profit is None:
            st.error("Could not compute profit: " + (note or "insufficient data."))
        else:
            st.success(f"✅ Results for {trade_type} {pair}")
            st.metric("📏 Pips", f"{pips:.2f}")
            if currency == "USD":
                st.metric("💰 Profit", f"${profit:,.2f}")
            else:
                st.metric("💰 Profit", f"{profit:,.2f} {currency}")
            st.write("---")
            st.info(
                f"**Details**\n\n"
                f"- Pip Size: `{pip_size}`\n"
                f"- Units (base currency): `{units:,.0f}`\n"
                f"- Profit currency: `{currency}`\n\n"
                f"{note}"
            )

            # Example debug numbers for USD-base pairs (useful to verify)
            if pair.startswith("USD"):
                mid = (opening_price + closing_price) / 2.0
                pip_value_in_quote = pip_size * units
                st.write(f"Debug: pip_value in {pair[3:]} = {pip_value_in_quote:.6f} {pair[3:]}, mid price = {mid:.6f}, pip_value in USD = {pip_value_in_quote / mid:.6f} USD")

