import datetime

import pytz
from dateutil.relativedelta import relativedelta

utc = pytz.UTC
seasons = {'Summer': (utc.localize(datetime.datetime(2014, 6, 21)), utc.localize(datetime.datetime(2014, 9, 22))),
           'Autumn': (utc.localize(datetime.datetime(2014, 9, 23)), utc.localize(datetime.datetime(2014, 12, 20))),
           'Spring': (utc.localize(datetime.datetime(2014, 3, 21)), utc.localize(datetime.datetime(2014, 6, 20)))}


class Utils:
    def get_season(date):
        date = pytz.UTC.localize(datetime.datetime(date.year, date.month, date.day))
        date = date - relativedelta(years=date.year - 2014)
        for season, (season_start, season_end) in seasons.items():
            if date >= season_start and date <= season_end:
                return season
        else:
            return 'Winter'
