import numpy as np
import math
import matplotlib.pyplot as plt
from .helpers.helper import Helpers
import pandas as pd
from scipy import interpolate
import matplotlib.cm as cm

class DeFiTools (Helpers):

    def iloss_simulate(self, base_token, quote_token, base_token_price, quote_token_price, value=100, base_pct_chg=0, quote_pct_chg=0):
        """Calculate simulated impermanent loss from an initial value invested, get real time prices from pancakeswap API
            This method create a 3D interpolated surface for impermanent loss and initial/final value invested
        Args:
            base_token (string): Pair first token, ie CAKE
            quote_token (string): Pais second token, ie BNB
            value (int, optional): Value investen in LP default=100
            base_pct_chg (int, optional): value assuming will change first token of LP pair, ie 10 (for +10% change)
            quote_pct_chg (int, optional): value assuming will change first token of LP pair, ie -30 (for -30% change)
        
        Returns:
            tuple (value_f, iloss): final value of value invested, and decimal impermanent loss
        """
        base_token = 'WBNB' if base_token.upper() == 'BNB' else base_token
        quote_token = 'WBNB' if quote_token.upper() == 'BNB' else quote_token
        
        # get real time prices
        tokens = self.pcsTokens()
        px_base = base_token_price#float(tokens.loc[tokens.symbol.str.upper()==base_token.upper()].price)
        px_quote = quote_token_price#float(tokens.loc[tokens.symbol.str.upper()==quote_token.upper()].price)

        # Prepare grid
        q_base, q_quote = (value/2)/px_base,  (value/2)/px_quote
        px_base, px_quote, q_base, q_quote
        pxs_base = [px_base*i/100 for i in range(1,301)]
        pxs_quote = [px_quote*i/100 for i in range(1,301)]
        rows = []
        for px_b in pxs_base:
            for px_q in pxs_quote:
                ratio = (px_b / px_base) / (px_q / px_quote)
                iloss = 2 * (ratio**0.5 / (1 + ratio)) - 1

                row = {'px_base':px_b, 'px_quote':px_q, 
                    'ratio':(px_b / px_base) / (px_q / px_quote),
                    'impremante_loss':iloss}
                rows.append(row)
        
        df = pd.DataFrame(rows)
        df_ok = df.loc[:,['px_base','px_quote','impremante_loss']]
        df_ok = df_ok.replace('NaN',np.nan).dropna()

        if all(isinstance(i, (int, float)) for i in (value, base_pct_chg, quote_pct_chg)):
            px_base_f = px_base * (1+base_pct_chg/100)
            px_quote_f = px_quote * (1+quote_pct_chg/100)
            ratio = (px_base_f / px_base) / ( px_quote_f / px_quote)
            iloss = 2 * (ratio**0.5 / (1 + ratio)) - 1
            value_f = (px_base_f*q_base + px_quote_f * q_quote) * (iloss+1)
        else:
            px_base_f, px_quote_f = px_base, px_quote
            iloss = 0
            value_f = None
            print('must input numerical amount and pct change for base and quote to calculations of final value')
            

        # Ploting surface
        fig = plt.figure(figsize=(8,8))
        x1 = np.linspace(df_ok['px_base'].min(), df_ok['px_base'].max(), len(df_ok['px_base'].unique()))
        y1 = np.linspace(df_ok['px_quote'].min(), df_ok['px_quote'].max(), len(df_ok['px_quote'].unique()))
        x2, y2 = np.meshgrid(x1, y1)
        Z = interpolate.griddata((df_ok['px_base'], df_ok['px_quote']), df_ok['impremante_loss'], (x2, y2))
        Z[np.isnan(Z)] = df_ok.impremante_loss.mean()
        ax = plt.axes(projection='3d', alpha=0.2)
        ax.plot_surface(x2, y2, Z, color='blue', lw=0.1, edgecolors='black', cmap='plasma', alpha=0.3) # can be changed to plot_surface() for colorbar
            
        # Start values ploting
        xmax = df_ok.px_base.max() 
        ymax = df_ok.px_quote.max()
        ax.plot([px_base, px_base], [0,px_quote], [-1,-1], ls='--', color='black', lw=1)
        ax.plot([px_base, px_base], [px_quote,px_quote], [0,-1], ls='--', color='black', lw=1)
        ax.plot([px_base, 0], [px_quote, px_quote], [-1,-1], ls='--', color='black', lw=1)

        # End values ploting
        ax.plot([px_base_f, px_base_f], [0,px_quote_f], [-1,-1], ls='--', c='gray', lw=1)
        ax.plot([px_base_f, px_base_f], [px_quote_f,px_quote_f], [iloss,-1], ls='--', c='gray', lw=1)
        ax.plot([px_base_f, 0], [px_quote_f, px_quote_f], [-1,-1], ls='--', c='gray', lw=1)
        ax.plot([px_base_f, px_base_f], [px_quote_f,ymax], [iloss,iloss], ls='--', c='gray', lw=1)
        ax.plot([px_base_f, 0], [ymax,ymax], [iloss,iloss], ls='--', c='gray', lw=1)
        
        # Plot settings
        # Colorbar only for plot_surface() method instead plot_wireframe()
        m = cm.ScalarMappable(cmap=cm.plasma) 
        m.set_array(df_ok['impremante_loss'])
        plt.colorbar(m, fraction=0.02, pad=0.1)
        x, y, z = (px_base, px_quote,.05)
        p = ax.scatter(x, y, z, c='k', marker='v', s=300)
        #ax.set_title('Impermanent Loss 3D Surface', y=0.95)
        ax.set_xlabel(f'Price {base_token}')
        ax.set_ylabel(f'Price {quote_token}')
        ax.set_zlabel('Impermanent loss')
        ax.view_init(elev=25, azim=240) # start view angle
        
        print (f"Final Impermanent Loss: {iloss:.2%}")
        plt.show()

        return value_f , iloss

    def iloss_stable(self, start_price, end_price, base_price):
        """Calculate simulated impermanent loss from an initial value invested. This method is suitable with the 
            pair with stable coin, i.e., BUSD
        Args:
            start_price (float): initial price of the token
            end_price (float): value assuming the final price of the token
            base_price (float): price of the token at the moment
        
        Returns:
            tuple (value_f, iloss): final value of value invested, and decimal impermanent loss
        """
        priceRange = np.linspace(start_price, end_price, 100)
        priceBase = base_price
        iLoss = []
        for i in range(priceRange.shape[0]):
            r = priceRange[i]/priceBase
            iLoss_ = (((2*math.sqrt(r))/(1+r)) - 1)*100
            iLoss.append(iLoss_)

        plt.plot(priceRange, iLoss)
        plt.xlabel('Price [USD$]', fontsize=13)
        plt.ylabel('PNL [%]', fontsize=13)
        plt.grid(True)
        plt.show()
        return 0


    def risk_profile_stable(self, start_price, end_price, base_price):
        """Calculate simulated risk profile from an initial value invested. This method is suitable with the 
            pair with stable coin, i.e., BUSD
        Args:
            start_price (float): start price of the token to be started
            end_price (float): value assuming the final price of the token
            base_price (float): price of the token at the moment

        Returns:
            tuple (value_f, iloss): final value of value invested, and decimal impermanent loss
        """
        priceRange = np.linspace(start_price, end_price, 100)
        priceBase = base_price
        pnl = []
        uni = []
        for i in range(priceRange.shape[0]):
            res = 100 + 50*((priceRange[i]/priceBase)-1)
            impLoss = 100*(-(math.sqrt(priceRange[i]/priceBase)-1)**2)/2
            unis = res + impLoss
            pnl.append(res)
            uni.append(unis)
        plt.plot(priceRange, pnl, '--b', label='Buy&Hold')
        plt.plot(priceRange, uni, '-r', label='Pancakeswap v2')
        plt.xlabel('Price [USD$]', fontsize=13)
        plt.ylabel('PNL [%]', fontsize=13)
        plt.legend(fontsize=13)
        plt.grid(True)
        plt.show()            
        return 0

    def risk_profile_3d(self, base_token, quote_token, base_token_price, quote_token_price, value):
        """Calculate simulated risk profile from an initial value invested. This method is suitable with the 
            pair with stable coin, i.e., BUSD
        Args:
            start_price (float): start price of the token to be started
            end_price (float): value assuming the final price of the token
            base_price (float): price of the token at the moment

        Returns:
            tuple (value_f, iloss): final value of value invested, and decimal impermanent loss
        """
        value = value
        base_token = 'WBNB' if base_token.upper() == 'BNB' else base_token
        quote_token = 'WBNB' if quote_token.upper() == 'BNB' else quote_token
        
        # get real time prices
        tokens = self.pcsTokens()
        px_base = base_token_price#float(tokens.loc[tokens.symbol.str.upper()==base_token.upper()].price)
        px_quote = quote_token_price#float(tokens.loc[tokens.symbol.str.upper()==quote_token.upper()].price)

        q_base, q_quote = (value/2)/px_base,  (value/2)/px_quote
        px_base, px_quote, q_base, q_quote
        pxs_base = [px_base*i/100 for i in range(1,301)]
        pxs_quote = [px_quote*i/100 for i in range(1,301)]

        rows = []
        pnl = []
        for px_b in pxs_base:
            for px_q in pxs_quote:
                # 
                var_A = (100*(px_b - px_base))/px_base
                var_B = (100*(px_q - px_quote))/px_quote
                buy_hold = (0.5 * var_A + 0.5 * var_B)
                #
                # ratio = (px_b / px_base) / (px_q / px_quote)
                # iloss = 100*(2 * (ratio**0.5 / (1 + ratio)) - 1) # Still work
                x = (var_A/100 + 1) / (var_B/100 + 1)
                iloss = 100*(2 * (x**0.5 / (1 + x)) - 1)
                #
                fin = buy_hold + iloss
                row = {'px_base':px_b, 'px_quote':px_q, 
                    'ratio':(px_b / px_base) / (px_q / px_quote),
                    'impremante_loss':fin}
                rows.append(row)
        df = pd.DataFrame(rows)
        df_ok = df.loc[:,['px_base','px_quote','impremante_loss']]
        df_ok = df_ok.replace('NaN',np.nan).dropna()    

        fig = plt.figure(figsize=(8,8))
        x1 = np.linspace(df_ok['px_base'].min(), df_ok['px_base'].max(), len(df_ok['px_base'].unique()))
        y1 = np.linspace(df_ok['px_quote'].min(), df_ok['px_quote'].max(), len(df_ok['px_quote'].unique()))
        x2, y2 = np.meshgrid(x1, y1)
        Z = interpolate.griddata((df_ok['px_base'], df_ok['px_quote']), df_ok['impremante_loss'], (x2, y2))
        Z[np.isnan(Z)] = df_ok.impremante_loss.mean()
        ax = plt.axes(projection='3d', alpha=0.2)
        ax.plot_surface(x2, y2, Z, color='blue', lw=0.1, edgecolors='black', cmap='inferno', alpha=0.3) # can be changed to plot_surface() for colorbar
        m = cm.ScalarMappable(cmap=cm.inferno) 
        m.set_array(df_ok['impremante_loss'])
        plt.colorbar(m, fraction=0.02, pad=0.1)
        ax.set_xlabel(f'Price {base_token}')
        ax.set_ylabel(f'Price {quote_token}')
        ax.set_zlabel('Risk Profile [%]')
        ax.view_init(elev=25, azim=240) # start view angle
        plt.show()
        return df      

    def compare(self, days, var_A=0, var_B=0, rw_pool_A=0, rw_pool_B=0, rw_pool_AB=0, fees_AB=0):
        """Compare for 2 assets, buy&hold strategy with separate staking and farming by liquidity pool providing.
            Considering: impermanent loss, fees earned and farming/staking rewards
        
        Args:
            days (int): days for strategy
            var_A (float, optional): Percentual variation for A token. Ex 10 for 10%
            var_B (float, optional): Percentual variation for B token. Ex 10 for 10%
            rw_pool_A (float, optional): Percentual rewards per day for one asset pool (Token A)
            rw_pool_B (float, optional): Percentual rewards per day for one asset pool (Token B)
            rw_pool_AB (float, optional): Percentual rewards per day for two asset farm (LP Token AB)
            fees_AB (float, optional): Percentual provider liquidity fees earned per day
        
        Returns:
            dict: Percentual returns for each strategy:
                buy_hold two assets in your wallet
                stake two assets at individual pools
                farming by liquidity pool 
        """
        buy_hold = (0.5 * var_A + 0.5 * var_B)/100
        x = (var_A/100 + 1) / (var_B/100 + 1)
        perdida_impermanente = 2 * (x**0.5 / (1 + x)) - 1

        stake = buy_hold + 0.5 * days * (rw_pool_A/100 + rw_pool_B/100)
        farm = buy_hold * (1+perdida_impermanente) + days * (rw_pool_AB/100 + fees_AB/100)
        mejor = 'Farm' if farm > stake else 'Stake'
        
        return {'buy_hold':f'{buy_hold:.2%}', 'stake':f'{stake:.2%}', 'farm':f'{farm:.2%}', 'Best': mejor}

    def compare_2D(self, days, start_price, end_price, base_price, rw_pool_A=0, rw_pool_B=0, rw_pool_AB=0, fees_AB=0):

        priceRange = np.linspace(start_price, end_price, days)
        priceBase = base_price
        pnl = []
        uni = []
        stake = []
        farm = []
        for i in range(priceRange.shape[0]):
            res = 100 + 50*((priceRange[i]/priceBase)-1)
            impLoss = (-(math.sqrt(priceRange[i]/priceBase)-1)**2)/2
            # print(impLoss)
            stake_ = res + 0.5*days*(rw_pool_A/100 + rw_pool_B/100)
            farm_ = res * (1-impLoss) + days * (rw_pool_AB/100 + fees_AB/100)
            unis = res + 100*impLoss
            pnl.append(res)
            uni.append(unis)
            stake.append(stake_)
            farm.append(farm_)

        # plt.plot(priceRange, pnl, '--b', label='Buy&Hold')
        # plt.plot(priceRange, uni, '-r', label='Pancakeswap v2')
        # plt.plot(priceRange, stake, '-.g', label='Staking')
        # plt.plot(priceRange, farm, linestyle=':', color='black', label='Farming')
        # plt.xlabel('Price [USD$]', fontsize=13)
        # plt.ylabel('PNL [%]', fontsize=13)
        # plt.legend(fontsize=13)
        # plt.grid(True)
        # plt.show()    
        return pnl, uni, stake, farm


    


