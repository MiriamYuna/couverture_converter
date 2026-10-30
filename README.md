# Couverture Converter

A small Python tool for pastry chefs. It converts a ganache or truffle base from one couverture to another, keeping the **cocoa butter** constant so the texture stays the same.

## Formula

New weight = Weight A x Cocoa butter A / Cocoa butter B

## Example

A truffle base uses 890 g of couverture A (42% cocoa butter). Swapping to couverture B (38% cocoa butter):

890 x 0.42 / 0.38 = 984 g

## How to run

    python couverture_converter.py

Enter the weight of couverture A, then the % cocoa butter of A and B.

## Notes

- Calculating on cocoa butter protects the texture. Calculating on total cocoa solids affects flavour and sugar instead.
- Sugar and flavour may change when swapping couvertures, so always test the result.

## Source

Based on the work of Ramon Morato, *Chocolate* (book). Adapted and implemented in Python by Miriam.

## Author

Professional pastry chef (25 years), learning Python and AI.
