from pathlib import Path
import sys

file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))

# Working route
from lib.defi_tools import DeFiTools #

dfts = DeFiTools()
dfts.risk_profile_3d(
    base_token='LFW',
    quote_token='BNB',
    base_token_price=0.014, 
    quote_token_price=330, 
    value=1000)