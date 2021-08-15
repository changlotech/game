import time
import pyupbit
import datetime

access = "업비트에서 받은 API입력"
secret = "업비트에서 받은 API입력"
    # get_target_price(ticker, k)는 변동성볼파전략을 이용해서 매수 목표가를 설정해주는 함수 ticker는 어떤 코인인지, 그리고 k값을 넣어주게 되면
    # 변동성 돌파전략을 계산을 이용해서 이틀치에 2틀치에 해당하는 데이터를 조회하고 여기서 변동성 돌파 전략을 사용해 줍니다.
def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close']+ (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    # 업비트API에서 제공하는 OHLCV를 조회할때 일봉으로 조회하면 그날의 시작시간이 나온다. 그게 9시로 설정이 되어있다. 그래서 그것을 받아올수 있도록 get_ohlcv를 이용해서 값을 받아오고
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    # 거기에 가장 첫 번째 값이 시간값 인데 그 시간 값을 받아와서 start_time에 저장한다. 즉 그냥 9시를 가져오는 것
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

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

# 자동매매 시작
while True:
    try:
        #현재 시간
        now = datetime.datetime.now()
        #시작 시간 (코인시장은 주식시장과 다르게 시작시간이 별도로 정해져있지 않음.)
        start_time = get_start_time("KRW-BTC") # 9:00
        #끝나는 시간   
        end_time = start_time + datetime.timedelta(days=1) # 9시에서 1일을 더해준 값. 다음날 9시가 마감 시간

        # 시간에 따라서 if,else 구문으로 구분해서 동작을 하게 된다.
        # if문은 시작시간과 끝나는시간에서 끝나는시간이 9시면 무한정으로 돌아갈테니까 여기서 10초를 빼줘서 8시59분50초까지 돌아가도록 만들어준다.
        # 9:00 < 현재 < 8:59:50     <= 현재시간이 이 조건을 만족하면 get_target_price()를 이용해서 매수목표가를 설정해 준다

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            #변동성 돌파전략으로 목표가를 세워주고
            target_price = get_target_price("KRW-BTC", 0.5)
            #현재가격
            current_price = get_current_price("KRW-BTC")
            # 목표가격 < 현재가격 이라면 
            if target_price < current_price:
                # 그때 KRW, 내 원화잔고를 조회하고 
                krw = get_balance("KRW")
                # 이게 최소 거래 금액인 5천원 이상이면 비트코인을 매수하는 코드를 작성해놓은 것임.
                if krw > 5000:
                    # 이때 수수료 0.05%를 고려해서 0.9995를 써놨음.
                    upbit.buy_market_order("KRW-BTC", krw*0.9995)
        # 현재시간이 8:59:50 이상이고 9시 전일때           
        else:
            # 당일종가에 비트코인을 전량 매도하는 코드
            # 현재 가지고있는 BTC의 잔고를 가져와서            
            btc = get_balance("BTC")
            # 현재 잔고가 5천원 이상이면 (최소거래금액 이상) 
            if btc > 0.00008:
                # 9시되시 10초 전부터 계속 전량 매도하는 코드 작성
                # 이때도 수수료를 고려해서 99.99%만 매도하도록 해놓음.
                upbit.sell_market_order("KRW-BTC", btc*0.9995)
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)
# 전략을 변경하고싶으면 traget_price(매수가)를 전략에 맞게 구하면 새로운 자동매매 코드를 만들 수 있다.
