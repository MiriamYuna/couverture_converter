import streamlit as st

# Product database. These are EXAMPLE values: replace with your own technical sheets.
COUVERTURES = {
    "Callebaut 70-30-38": {"cocoa_butter": 38.9},
    "Callebaut 811": {"cocoa_butter": 36.6},
    "Callebaut 823 milk (total fat)": {"cocoa_butter": 36.2},
    "Callebaut 665 milk (total fat)": {"cocoa_butter": 35.5},
    "Callebaut Gold (total fat)": {"cocoa_butter": 37.1},
    "Callebaut Ruby RB2 (total fat)": {"cocoa_butter": 36.8},
    "White (example)": {"cocoa_butter": 33},
}
def new_couverture_weight(weight_a, factor_a, factor_b):
    return weight_a * factor_a / factor_b

st.title("Chocolate Calculator")
tab_swap, tab_ganache = st.tabs(["Swap couverture", "Ganache"])

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
