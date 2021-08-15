import pyupbit
import numpy as np


def get_ror(k=0.5):
    df = pyupbit.get_ohlcv("KRW-BTC", count=7)
    df['range'] = (df['high'] - df['low']) * k
    df['target'] = df['open'] + df['range'].shift(1)

    fee = 0.0009
    df['ror'] = np.where(df['high'] > df['target'],
                         df['close'] / df['target'] - fee,
                         1)
    # 누적수익률을 계산해준다음에 리턴한다
    ror = df['ror'].cumprod()[-2]
    return ror

# k값이 0.1부터 1.0까지 0.1간격으로 증가를 시켜서 get_ror이란 함수를 통해서
for k in np.arange(0.1, 1.0, 0.1):
    ror = get_ror(k)
    # 출력
    print("%.1f %f" % (k, ror))
