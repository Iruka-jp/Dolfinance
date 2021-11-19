def get_yf_options(ticker,expiry_date):
    import requests
    from datetime import datetime
    def get_timestamp_from_str(x):
        if type(x)==str:
            return int(pd.Timestamp(x).to_pydatetime().timestamp())
        elif type(x)==type(pd.Timestamp.now()):
            return int(x.to_pydatetime().timestamp())
    
    if type(expiry_date) not in [type(pd.Timestamp.now()),str]:
        raise Exception('expiry date must be strings or pandas Timestamp.')
    elif type(ticker)!=str:
        raise Exception('Ticker must be a string.')
    else:
        if type(expiry_date)==type(pd.Timestamp.now()):
            if expiry_date.hour==0:
                expiry_date = expiry_date + pd.Timedelta('9h')                
        else:
            if ':' not in expiry_date:
                expiry_date +=' 09:00'
        expiry_date = get_timestamp_from_str(expiry_date)
#         print((ticker,expiry_date))
        url = ('https://query1.finance.yahoo.com/v7/finance/options/{0}?date={1}').format(ticker,expiry_date)
#         print(url)
        headers = {'User-Agent': ''}
        resp_json = requests.get(url, headers=headers).json()
#         print(resp_json)
        data_json = resp_json['optionChain']['result'][0]
#         print(data_json)
        if len(data_json['options'][0]['puts'])>0:
            df = pd.DataFrame(data_json['options'][0]['puts'])
            df['type'] = 'put'
            df2 = pd.DataFrame(data_json['options'][0]['calls'])
            df2['type'] = 'call'
            df = pd.concat([df,df2],axis=0)
            df['expirationDate'] = data_json['options'][0]['expirationDate']
            df['expirationDate'] = df.expirationDate.apply(lambda x:pd.Timestamp(datetime.fromtimestamp(int(str(x)[:10]))) )
            return df
        else:
            return pd.DataFrame()