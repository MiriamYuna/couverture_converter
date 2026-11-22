import streamlit as st

# Fat % from Callebaut's official product pages (milk/Gold/Ruby = total fat).
COUVERTURES = {
    "Callebaut 70-30-38": {"cocoa_butter": 38.9},
    "Callebaut 811": {"cocoa_butter": 36.6},
    "Callebaut 823 milk (total fat)": {"cocoa_butter": 36.2},
    "Callebaut 665 milk (total fat)": {"cocoa_butter": 35.5},
    "Callebaut Gold (total fat)": {"cocoa_butter": 37.1},
    "Callebaut Ruby RB2 (total fat)": {"cocoa_butter": 36.8},
    "White (example)": {"cocoa_butter": 33},
}

# Callebaut technical sheets (per 100 g). Used by the ganache designer.
GANACHE_COUVERTURES = {
    "Callebaut 70-30-38": {"cocoa_butter": 38.9, "sugar": 26.0, "type": "Dark"},
    "Callebaut 811": {"cocoa_butter": 36.6, "sugar": 43.1, "type": "Dark"},
    "Callebaut 823 milk": {"cocoa_butter": 36.2, "sugar": 49.9, "type": "Milk"},
}
LIQUIDS = {
    "Cream 35%": {"water": 65.0, "sugar": 0.0, "dairy_fat": 35.0},
    "Fruit puree (approx.)": {"water": 85.0, "sugar": 10.0, "dairy_fat": 0.0},
}
COCOA_BUTTER_TARGET = {"Dark": 22.0, "Milk": 28.0}


def new_couverture_weight(weight_a, factor_a, factor_b):
    return weight_a * factor_a / factor_b


def design_ganache(liquid_g, water, sugar, dairy_fat, couv_cb, couv_sugar, target_cb):
    """Smallest total weight where water<=20, sugars>=30, dairy fat<=15, butter<=15
    and cocoa butter = target. Returns dict of grams or None."""
    k = target_cb / couv_cb
    if k >= 1 or liquid_g <= 0:
        return None
    total = liquid_g
    while total < liquid_g * 30:
        couv = k * total
        liquid_sugar = liquid_g * sugar / 100
        need = 0.30 * total - liquid_sugar - couv * couv_sugar / 100
        glucose = max(0.0, need / 0.8)
        butter = total - liquid_g - couv - glucose
        if butter >= -1e-9:
            butter = max(butter, 0.0)
            w = (liquid_g * water / 100 + glucose * 0.20) / total * 100
            d = (liquid_g * dairy_fat / 100 + butter) / total * 100
            if w <= 20 and d <= 15 and butter / total * 100 <= 15:
                return {"couverture": couv, "glucose": glucose, "butter": butter, "total": total}
        total += 0.5
    return None


st.title("Chocolate Calculator")
tab_swap, tab_ganache, tab_design = st.tabs(["Swap couverture", "Ganache analyser", "Ganache designer"])

with tab_swap:
    st.header("Swap couverture")

    name_a = st.selectbox("Couverture A (original)", list(COUVERTURES))
    name_b = st.selectbox("Couverture B (new)", list(COUVERTURES), index=1)
    weight_a = st.number_input("Grams of A", min_value=0.0, value=890.0, step=10.0)

    factor_a = COUVERTURES[name_a]["cocoa_butter"] / 100
    factor_b = COUVERTURES[name_b]["cocoa_butter"] / 100
    weight_b = new_couverture_weight(weight_a, factor_a, factor_b)

    st.metric("Grams of B needed", f"{round(weight_b)} g")

with tab_ganache:
    st.header("Ganache analyser")
    st.caption("Based on the truffle balance in Ramon Morato's book (pp. 205-209).")

    cream = st.number_input("Cream 35% fat (g)", min_value=0.0, value=500.0, step=10.0)
    glucose = st.number_input("Glucose syrup (g)", min_value=0.0, value=50.0, step=10.0)
    couverture = st.number_input("Couverture (g)", min_value=0.0, value=650.0, step=10.0)
    butter = st.number_input("Fresh butter (g)", min_value=0.0, value=100.0, step=10.0)
    couv_sugar = st.number_input("Sugar in the couverture (%)", min_value=0.0, max_value=100.0, value=30.0)
    couv_cb = st.number_input("Cocoa butter in the couverture (%)", min_value=0.0, max_value=100.0, value=42.0)

    total = cream + glucose + couverture + butter

    if total > 0:
        water = (cream * 0.65 + glucose * 0.20 + butter * 0.16) / total * 100
        sugars = (glucose * 0.80 + couverture * couv_sugar / 100) / total * 100
        cocoa_butter = couverture * couv_cb / 100 / total * 100
        dairy_fat = (cream * 0.35 + butter * 0.84) / total * 100

        st.subheader(f"Total: {round(total)} g")

        checks = [
            ("Water", water, "max 20%", water <= 20),
            ("Sugars", sugars, "min 30%", sugars >= 30),
            ("Cocoa butter", cocoa_butter, "min 21%", cocoa_butter >= 21),
            ("Dairy fat", dairy_fat, "max 15%", dairy_fat <= 15),
        ]
        for label, value, limit, ok in checks:
            icon = "✅" if ok else "❌"
            st.write(f"{icon} **{label}:** {value:.1f}%  ({limit})")

        advice = []
        if water > 20:
            advice.append("Too much water: use less cream and swap fresh butter for anhydrous butter.")
        if sugars < 30:
            advice.append("Not enough sugars: add invert sugar, glucose syrup, dextrose or sorbitol (a mix works best).")
        if cocoa_butter < 21:
            advice.append("Not enough cocoa butter: add more couverture or some extra cocoa butter.")
        if dairy_fat > 15:
            advice.append("Too much dairy fat: use less cream and butter.")

        if advice:
            st.subheader("What to change")
            for line in advice:
                st.write("• " + line)
        else:
            st.success("This recipe is within the book's balance. Measure the Aw to confirm it is below 0.85.")

with tab_design:
    st.header("Ganache designer")
    st.caption("Balances a truffle ganache (cut with a guitar) using the limits in Ramon Morato's book.")

    liquid_name = st.selectbox("Liquid", list(LIQUIDS))
    liquid_g = st.number_input("Grams of liquid", min_value=0.0, value=500.0, step=10.0)
    couv_name = st.selectbox("Couverture", list(GANACHE_COUVERTURES), key="design_couverture")

    liquid = LIQUIDS[liquid_name]
    couv = GANACHE_COUVERTURES[couv_name]
    target_cb = COCOA_BUTTER_TARGET[couv["type"]]
    st.write(f"Cocoa butter target for a {couv['type'].lower()} ganache cut with a guitar: **{target_cb:.0f}%**")

    result = design_ganache(
        liquid_g, liquid["water"], liquid["sugar"], liquid["dairy_fat"],
        couv["cocoa_butter"], couv["sugar"], target_cb,
    )

    if result is None:
        st.error("No recipe fits all the book's limits with this liquid and couverture. Try another couverture.")
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("Couverture", f"{round(result['couverture'])} g")
        col2.metric("Glucose syrup", f"{round(result['glucose'])} g")
        col3.metric("Anhydrous butter", f"{round(result['butter'])} g")
        st.subheader(f"Total: {round(result['total'])} g")
        st.info("Water max 20%, sugars min 30%, dairy fat max 15%. Measure the Aw to confirm it is below 0.85.")
