import datetime
import pytz

class MarketHours:
    def __init__(self):
        self.est = pytz.timezone('US/Eastern')
        self.london = pytz.timezone('Europe/London')
        self.tokyo = pytz.timezone('Asia/Tokyo')
        self.sydney = pytz.timezone('Australia/Sydney')

    def get_current_times(self):
        now_utc = datetime.datetime.now(pytz.utc)
        return {
            "UTC": now_utc,
            "EST (NY)": now_utc.astimezone(self.est),
            "London": now_utc.astimezone(self.london),
            "Tokyo": now_utc.astimezone(self.tokyo),
            "Sydney": now_utc.astimezone(self.sydney)
        }

    def check_market_state(self):
        now_utc = datetime.datetime.now(pytz.utc)
        ny_time = now_utc.astimezone(self.est)
        lon_time = now_utc.astimezone(self.london)
        tok_time = now_utc.astimezone(self.tokyo)
        syd_time = now_utc.astimezone(self.sydney)
        
        is_weekend = ny_time.weekday() >= 5 and ny_time.weekday() <= 6
        if is_weekend and (ny_time.weekday() == 5 or (ny_time.weekday() == 6 and ny_time.hour < 17)):
            return "WEEKEND_CLOSED (Crypto Only)"

        states = []
        
        # Sydney: 5pm-2am EST
        if syd_time.hour >= 8 and syd_time.hour < 17:
             states.append("Sydney OPEN")
             
        # Tokyo: 7pm-4am EST
        if tok_time.hour >= 9 and tok_time.hour < 18:
             states.append("Tokyo OPEN")
             
        # London: 3am-12pm EST
        if lon_time.hour >= 8 and lon_time.hour < 17:
             states.append("London OPEN")
             
        # NY: 8am-5pm EST
        if ny_time.hour >= 8 and ny_time.hour < 17:
             states.append("NY OPEN")
             
        return states if states else ["Roll-over / Low Liquidity"]

if __name__ == "__main__":
    mh = MarketHours()
    print("="*40)
    print("RELOGIO INSTITUCIONAL OMEGA")
    print("="*40)
    times = mh.get_current_times()
    for loc, t in times.items():
        print(f"{loc}: {t.strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nSTATUS BOLSAS:")
    print(mh.check_market_state())
    print("="*40)
