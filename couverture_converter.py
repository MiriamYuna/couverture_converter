# Couverture converter
# Keeps the amount of cocoa butter constant when swapping one couverture for another.

def new_couverture_weight(weight_a, factor_a, factor_b):
    return weight_a * factor_a / factor_b

print("Couverture converter")
weight_a = float(input("Grams of couverture A: ").replace(",", "."))
cocoa_butter_a = float(input("% cocoa butter in A (e.g. 42): ").replace(",", "."))
cocoa_butter_b = float(input("% cocoa butter in B (e.g. 38): ").replace(",", "."))

weight_b = new_couverture_weight(weight_a, cocoa_butter_a / 100, cocoa_butter_b / 100)
print("You need", round(weight_b), "g of couverture B")