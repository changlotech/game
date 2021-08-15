import pyupbit
import numpy as np

# 원화 시장의 BTC에 대해서 count=7(7일 동안의 ohlcv값을 불러오는 코드)
df = pyupbit.get_ohlcv("KRW-BTC", count=7) #업비트는 KRW-BTC

# 변동성돌파 기준 범위(range) 계산 == (고가 - 저가) * k값
# range라는 컬럼을 만들고 여기에 (고가-저가) x 0.5(k값)해서 range(변동성돌파기준범위)를 구해주고

df['range'] = (df['high'] - df['low']) * 0.5

# 그리고range는 전날이기 때문에 .shift(1)를 이용해서 컬럼을 한칸씩 밑으로내림 그다음에 df['open'(시가)]에 더해줘서 타켓 매수가를 만들어줍니다.
# 엑셀컬럼에서 range컬럼에서 한칸씩 밑으로 내려가는것을 열어보면 알 수 있다.    .shift(1)은 그런 의미임.
# target(매수가) 
df['target'] = df['open'] + df['range'].shift(1)
print(df)
#빗썸기준 수수료  fee = 0.0032 업비트는 0.0009BTC라고 나와있음.
fee = 0.0009
# 수익률을 계산하는 코드
# 이거는 넘파이(np) 라이브러리를 활용해서 NumPy.where라는 구문을 사용 np.where(조건문, 참일때 값, 거짓일때 값)
# 여기서는 고가>타겟값(매수가) 보다 높게되면 매수가 진행이 된 상황
# 이게 참이라면 즉 종가에 전부 매도를 하기 때문에
# 종가 / 매수가(타겟) 하면 수익률이 나오게 됨
# 거짓일 때 매수를 진행하지 않게 되면 그대로 있는 거기 때문에 수익률은 1, 그냥 그대로 1
df['ror'] = np.where(df['high'] > df['target'],
                     df['close'] / df['target'] - fee, # -fee 제거했음
                     1)

# 수익률을 누적해서 곱해서 누적 수익률을 구해주게 됨 
# 누적 곱 게산(comprod) => 누적 수익률
df['hpr'] = df['ror'].cumprod()


# drawdown 즉 하락폭을 계산해 주기 위해서 (누적 최대값과 현재 hpr 차이 / 누적최대값)
df['dd'] = (df['hpr'].cummax() - df['hpr']) / df['hpr'].cummax() * 100

# MaxDrawDown은 drawdown중에 max값을 찾아주게 되면
print("MDD(%): ", df['dd'].max())

# 이렇게 저장된 값들을 엑셀에 저장을 해 주게 되면
# dd.xlsx파일에 저장이됨.
df.to_excel("dd.xlsx") 