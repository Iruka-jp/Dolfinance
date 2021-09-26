def get_yf_data(ticker,start_date,end_date,freq_type,freq):
    freq_types=['mo','wk','d','h','m']
    import requests
    from datetime import datetime
    def get_timestamp_from_str(x):
        if type(x)==str:
            return int(pd.Timestamp(x).to_pydatetime().timestamp())
        elif type(x)==type(pd.Timestamp.now()):
            return int(x.to_pydatetime().timestamp())
        
    def _frequency_str(frequency_type, frequency):
        return '{1}{0}'.format(frequency_type, frequency)
    
    if freq_type not in freq_types:
        raise Exception("ValueError: frequency type must be one of 'wk','mo','d','h','m'")
    elif type(freq)!=int:
        raise Exception('freq must be a positive integer (type int)')
    elif type(start_date) not in [type(pd.Timestamp.now()),str] or type(end_date) not in [type(pd.Timestamp.now()),str]:
        raise Exception('start date and end date must be strings or pandas Timestamp.')
    elif type(ticker)!=str:
        raise Exception('Ticker must be a string.')
    else:
        tt_start = get_timestamp_from_str(start_date)
        tt_end = get_timestamp_from_str(end_date)
        url = (
            'https://query1.finance.yahoo.com/v8/finance/chart/{0}?symbol={0}'
            '&period1={1}&period2={2}&interval={3}&'
            'includePrePost=true&events=div%7Csplit%7Cearn&lang=en-US&'
            'region=US&crumb=t5QZMhgytYZ&corsDomain=finance.yahoo.com'
        ).format(ticker, tt_start, tt_end, _frequency_str(freq_type, freq))
        headers = {'User-Agent': ''}
        resp_json = requests.get(url, headers=headers).json()
        data_json = resp_json['chart']['result'][0]
        return_data = {
            'timestamp': [x * 1000 for x in data_json['timestamp']],
            'open': data_json['indicators']['quote'][0]['open'],
            'high': data_json['indicators']['quote'][0]['high'],
            'low': data_json['indicators']['quote'][0]['low'],
            'close': data_json['indicators']['quote'][0]['close'],
            'volume': data_json['indicators']['quote'][0]['volume']
        }        
        df = pd.DataFrame(return_data)
        df['timestamp'] = df.timestamp.apply(lambda x:pd.Timestamp(datetime.fromtimestamp(int(str(x)[:10]))) )
        return df