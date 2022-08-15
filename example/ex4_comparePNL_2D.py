from pathlib import Path
import sys

file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))

# Working route
from lib.defi_tools import DeFiTools #

dfts = DeFiTools()
res = dfts.compare(
    days=20, 
    var_A=150, 
    var_B=150, 
    rw_pool_A=0.01, 
    rw_pool_B=0.05, 
    rw_pool_AB=0.2, 
    fees_AB=0.01)
print(res)