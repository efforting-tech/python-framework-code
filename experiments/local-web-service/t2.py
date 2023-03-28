from data_example import ar1

for sku_entry in ar1.contents[0].contents:
	print(f'{ar1.contents[0].contents.indices[sku_entry]}:\t{sku_entry.format()}')


# OUTPUT

# capacitor 10 pcs
# slime 5.00 µl
# junk 2.30 kt
# elephant 2 doz

