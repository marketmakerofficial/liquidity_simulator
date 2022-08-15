from pathlib import Path
import sys

file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))

# Working route
from lib.defi_tools import DeFiTools #

dfts = DeFiTools()
dfts.risk_profile_stable(
    start_price=0.01, 
    end_price=0.1, 
    base_price=0.014)