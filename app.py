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

# Callebaut technical sheets (per 100 g). Dark couvertures only for now.
GANACHE_COUVERTURES = {
    "Callebaut 70-30-38": {"cocoa_butter": 38.9, "sugar": 26.0},
    "Callebaut 811": {"cocoa_butter": 36.6, "sugar": 43.1},
}
LIQUIDS = {
    "Cream 35%": {"water": 65.0, "sugar": 0.0, "dairy_fat": 35.0},
    "Fruit puree (approx.)": {"water": 85.0, "sugar": 10.0, "dairy_fat": 0.0},
}

# Added sugars, in the proportions of recipe 189 (weight ratio 1 : 2 : 2.5 : 2).
# Each entry: share of the added weight, and the % of water in that ingredient.
ADDED_SUGARS = {
    "Glucose syrup": {"share": 1 / 7.5, "water": 20.0},
    "Invert sugar": {"share": 2 / 7.5, "water": 20.0},
    "Dextrose": {"share": 2.5 / 7.5, "water": 0.0},
    "Sorbitol powder": {"share": 2 / 7.5, "water": 0.0},
}
SUGAR_PER_GRAM = sum(v["share"] * (100 - v["water"]) / 100 for v in ADDED_SUGARS.values())
WATER_PER_GRAM = sum(v["share"] * v["water"] / 100 for v in ADDED_SUGARS.values())


def new_couverture_weight(weight_a, factor_a, factor_b):
    return weight_a * factor_a / factor_b


def design_ganache(liquid_g, water, sugar, dairy_fat, couv_cb, couv_sugar, target_cb, target_sugar):
    """Ganache with a target % of cocoa butter and of total sugars.
    Returns grams of each ingredient and the resulting percentages, or None."""
    if liquid_g <= 0 or couv_cb <= 0:
        return None
    k = target_cb / couv_cb
    s = target_sugar / 100
    sc = couv_sugar / 100
    sl = sugar / 100
    if k >= 1:
        return None
    denominator = 1 - k - (s - sc * k) / SUGAR_PER_GRAM
    total = liquid_g * (1 - sl / SUGAR_PER_GRAM) / denominator if denominator > 0 else -1
    couverture = k * total
    added = (s * total - sl * liquid_g - sc * couverture) / SUGAR_PER_GRAM
    if total <= 0 or added < 0:
        # Couverture and liquid already give enough sugar: no added sugars.
        added = 0.0
        total = liquid_g / (1 - k)
        couverture = k * total
    result = {"couverture": couverture, "total": liquid_g + couverture + added}
    for name, info in ADDED_SUGARS.items():
        result[name] = added * info["share"]
    total = result["total"]
    result["pct_water"] = (liquid_g * water / 100 + added * WATER_PER_GRAM) / total * 100
    result["pct_sugar"] = (liquid_g * sugar / 100 + added * SUGAR_PER_GRAM + couverture * couv_sugar / 100) / total * 100
    result["pct_cocoa_butter"] = couverture * couv_cb / 100 / total * 100
    result["pct_dairy_fat"] = liquid_g * dairy_fat / 100 / total * 100
    return result


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
    st.caption("For piped bonbon ganaches with dark couverture. Based on recipe 189 (811 ganache) and Ramon Morato's book.")

    liquid_name = st.selectbox("Liquid", list(LIQUIDS))
    liquid_g = st.number_input("Grams of liquid", min_value=0.0, value=190.5, step=10.0)
    couv_name = st.selectbox("Couverture", list(GANACHE_COUVERTURES), index=1, key="design_couverture")
    target_cb = st.number_input("Target cocoa butter (%)", min_value=5.0, max_value=30.0, value=16.3, step=0.5)
    target_sugar = st.number_input("Target total sugars (%)", min_value=20.0, max_value=60.0, value=41.0, step=1.0)

    liquid = LIQUIDS[liquid_name]
    couv = GANACHE_COUVERTURES[couv_name]

    result = design_ganache(
        liquid_g, liquid["water"], liquid["sugar"], liquid["dairy_fat"],
        couv["cocoa_butter"], couv["sugar"], target_cb, target_sugar,
    )

    if result is None:
        st.error("These targets do not work with this couverture. Try a lower cocoa butter target.")
    else:
        col1, col2 = st.columns(2)
        col1.metric("Couverture", f"{round(result['couverture'])} g")
        col2.metric("Total", f"{round(result['total'])} g")
        col1, col2 = st.columns(2)
        col1.metric("Glucose syrup", f"{round(result['Glucose syrup'], 1)} g")
        col2.metric("Invert sugar", f"{round(result['Invert sugar'], 1)} g")
        col1, col2 = st.columns(2)
        col1.metric("Dextrose", f"{round(result['Dextrose'], 1)} g")
        col2.metric("Sorbitol powder", f"{round(result['Sorbitol powder'], 1)} g")

        st.subheader("Result")
        st.write(f"Water: **{result['pct_water']:.1f}%**")
        st.write(f"Sugars: **{result['pct_sugar']:.1f}%**")
        st.write(f"Cocoa butter: **{result['pct_cocoa_butter']:.1f}%**")
        st.write(f"Dairy fat: **{result['pct_dairy_fat']:.1f}%**")
        st.info("Recipe 189 has about 22% water, 41% sugars, 16% cocoa butter and 11% dairy fat. Measure the Aw to confirm it is below 0.85.")
   
   
