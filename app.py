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
    st.header("Ganache")
    st.write("Coming soon.")
