import datetime

import pytz

utc=pytz.UTC
seasons = {'Summer': (utc.localize(datetime.datetime(2014, 6, 21)), utc.localize(datetime.datetime(2014, 9, 22))),
        'Autumn': (utc.localize(datetime.datetime(2014, 9, 23)), utc.localize(datetime.datetime(2014, 12, 20))),
        'Spring': (utc.localize(datetime.datetime(2014, 3, 21)), utc.localize(datetime.datetime(2014, 6, 20)))}

class Utils:
    def get_season(date):
        date=pytz.UTC.localize(datetime.datetime(2014,date.month,date.day))
        for season,(season_start, season_end) in seasons.items():
            if date>=season_start and date<= season_end:
                return season
        else:
            return 'Winter'
