from pathlib import Path
import sys

file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))

# Working route
from lib.defi_tools import DeFiTools #

dfts = DeFiTools()
dfts.iloss_simulate(
    base_token='LFW',
    quote_token='BNB',
    base_token_price=0.014, 
    quote_token_price=330, 
    value=1000, 
    base_pct_chg=100, 
    quote_pct_chg=10)