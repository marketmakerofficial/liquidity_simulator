import requests
import pandas as pd
import datetime


class Helpers:
    def toFloatPartial(self, df):
        for i in df.columns:
            try:
                df[[i]] = df[[i]].astype(float)
            except:
                pass
        return df

            
    def pcsSummary(self, as_df = True):

        url = "https://api.pancakeswap.info/api/v2/summary"
        r = requests.get(url).json()
        data = r.get('data', None)
        upd = r.get('updated_at')/1000
        upd_dt = datetime.datetime.fromtimestamp(upd)

        if as_df:
            df = pd.DataFrame.from_dict(data, orient='index')
            df = self.toFloatPartial(df) 
            df['updated'] = upd_dt
            return df
        else:
            return r

    def pcsTokens(self, as_df = True):
        """get all token listed in pancakeswap
        
        Args:
            as_df (bool, optional): if True (default), return is a dataframe, else is a dictionary
        
        Returns:
            DataFrame with next columns: name  symbol  price   price_BNB   updated
        """
        # ultimo precio y volumen de base/quote de todos los pares

        url = "https://api.pancakeswap.info/api/v2/tokens"
        r = requests.get(url).json()
        data = r.get('data', None)
        upd = r.get('updated_at')/1000
        upd_dt = datetime.datetime.fromtimestamp(upd)
        
        if as_df:
            df = pd.DataFrame.from_dict(data, orient='index')
            df = self.toFloatPartial(df) 
            df['updated'] = upd_dt
            return df
        else:
            return r


    def pcsPairs(self, as_df = True):
        """get top 1000 pancakeswap pairs LP order by reserves
        
        Args:
            as_df (bool, optional): if True (default), return is a dataframe, else is a dictionary
        
        Returns:
            DataFrame with next columns: 'pair_address', 'base_name', 'base_symbol', 'base_address',
        'quote_name', 'quote_symbol', 'quote_address', 'price', 'base_volume',
        'quote_volume', 'liquidity', 'liquidity_BNB', 'updated'
        """

        url = "https://api.pancakeswap.info/api/v2/pairs"
        r = requests.get(url).json()
        data = r.get('data', None)
        upd = r.get('updated_at')/1000
        upd_dt = datetime.datetime.fromtimestamp(upd)
        
        if as_df:
            df = pd.DataFrame.from_dict(data, orient='index')
            df = self.toFloatPartial(df) 
            df['updated'] = upd_dt
            return df
        else:
            return r

    def pcsTokenInfo(self, search):
        """get info from a token
        
        Args:
            search (string): Token symbol or contract address
        
        Returns:
            Dict: 
            {
            'name': 'Wrapped BNB',
            'symbol': 'WBNB',
            'price': '524.5429',
            'price_BNB': '1'
            }
        """
        search = 'WBNB' if search.upper() == 'BNB' else search   
        url = "https://api.pancakeswap.info/api/v2/tokens"
        r = requests.get(url).json()
        data = r.get('data', None)
        res = f"Not found: {search}"
        for contract, values in data.items():
            if search.upper() == values['symbol'].upper() or search.upper()==contract.upper():
                res = data[contract]
                break

        return res



    def pcsPairInfo(self, base, quote):
        """get info from a token pair LP
        
        Args:
            base (string): Base LP token, ie "CAKE"
            quote (string): Quote LP token, ie "BNB"
            its the same if you call pcsPAirInfo('cake', 'bnb') or pcsPAirInfo('bnb', 'cake') 
        Returns:
            Dict: {
                    'pair_address': '0xA527a61703D82139F8a06Bc30097cC9CAA2df5A6',
                    'base_name': 'PancakeSwap Token',
                    'base_symbol': 'Cake',
                    'base_address': '0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82',
                    'quote_name': 'Wrapped BNB',
                    'quote_symbol': 'WBNB',
                    'quote_address': '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c',
                    'price': '0.04311198194009326668',
                    'base_volume': '22248744.85',
                    'quote_volume': '934856.36',
                    'liquidity': '982769040.63',
                    'liquidity_BNB': '1878155.84'
                    }
                    * price is actually a ratio between base/quote tokens
        """
        url = "https://api.pancakeswap.info/api/v2/pairs"
        r = requests.get(url).json()
        data = r.get('data', None)
        res = f"Not found: {base}-{quote}"
        base = 'WBNB' if base.upper() == 'BNB' else base
        quote = 'WBNB' if quote.upper() == 'BNB' else quote
        
        for contract, values in data.items():
            base_ = base.upper() == values['base_symbol'].upper()
            quote_ = quote.upper() == values['quote_symbol'].upper()
            base_cross = base.upper() == values['quote_symbol'].upper()
            quote_cross = quote.upper() == values['base_symbol'].upper()

            if  (base_ and quote_) or  (base_cross and quote_cross):
                res = data[contract]
                break
                
        return res
