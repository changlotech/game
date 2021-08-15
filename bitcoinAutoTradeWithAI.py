import time
import pyupbit
import datetime
import schedule
from fbprophet import Prophet

access = "your-access"
secret = "your-secret"

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]

#predicted_close_price라는 변수를 만들고 여기에 당일 종가의 예측값을 저장해준다. 
#처음에는 0을 저장해주고 아래의 함수를 통해서
#아래의 구글콜랩에서 작성한 코드를 그대로 가져다 놓음
# predicted_close_price는 전역변수
predicted_close_price = 0
def predict_price(ticker):
    """Prophet으로 당일 종가 가격 예측"""
    global predicted_close_price
    df = pyupbit.get_ohlcv(ticker, interval="minute60")
    df = df.reset_index()
    df['ds'] = df['index']
    df['y'] = df['close']
    data = df[['ds','y']]
    model = Prophet()
    model.fit(data)
    future = model.make_future_dataframe(periods=24, freq='H')
    forecast = model.predict(future)
    closeDf = forecast[forecast['ds'] == forecast.iloc[-1]['ds'].replace(hour=9)]
    if len(closeDf) == 0:
        closeDf = forecast[forecast['ds'] == data.iloc[-1]['ds'].replace(hour=9)]
        # 예측한 값(closeValue)을 predicted_close_price에 담는다
    closeValue = closeDf['yhat'].values[0]
    predicted_close_price = closeValue
# 처음에 한 번은 그냥 이렇게 실행을 한다.
# 이 함수를 계속 실행하게되면 굉장히 많은 연산을 필요로한다
predict_price("KRW-BTC")

# 그래서 이것은 schedule이라는 라이브러리를 활용해서
# every().hour 한시간마다
# 이함수가 실행이 되도록하여
# 당일 종가의 값을 1시간마다 업데이트해주도록한 코드
schedule.every().hour.do(lambda: predict_price("KRW-BTC"))

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)
        # schedule을 동작시키고
        schedule.run_pending()

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price = get_target_price("KRW-BTC", 0.5)
            current_price = get_current_price("KRW-BTC")
                                                # 현재가격 < 예측된종가가 더 가격이 높은경우에 매수가 진행되도록 코드 추가 이 때 predicted_close_price는 전역변수로서 1시간마다 업데이트됨
            if target_price < current_price and current_price < predicted_close_price:
                krw = get_balance("KRW")
                if krw > 5000:
                    upbit.buy_market_order("KRW-BTC", krw*0.9995)
        else:
            btc = get_balance("BTC")
            if btc > 0.00008:
                upbit.sell_market_order("KRW-BTC", btc*0.9995)
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)