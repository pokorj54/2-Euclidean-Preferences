import implied_regions as ir

for i in range(3,10):
    print(i, 'all:', ir.max_regions(i), 'inner', ir.max_inner_regions(i), 'outer',ir.max_outer_regions(i))
