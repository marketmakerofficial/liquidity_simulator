# from pathlib import Path
# import sys

# file = Path(__file__).resolve()
# parent, root = file.parent, file.parents[1]
# sys.path.append(str(root))

# # Working route
# from lib.defi_tools import DeFiTools #

# dfts = DeFiTools()
# pnl, uni, stake, farm = dfts.compare_2D(
#     days=100,
#     start_price=0.01,
#     end_price=0.1,
#     base_price=0.014,
#     rw_pool_A=40,
#     rw_pool_B=7,
#     rw_pool_AB=7,
#     fees_AB=0.005)

# print(pnl)
# print(uni)
# print(stake)
# print(farm)