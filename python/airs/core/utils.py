import datetime

from zoneinfo import ZoneInfo
from dateutil.relativedelta import relativedelta

seasons = {'Summer': (datetime.datetime(2014, 6, 21, tzinfo=ZoneInfo("UTC")), datetime.datetime(2014, 9, 22, tzinfo=ZoneInfo("UTC"))),
           'Autumn': (datetime.datetime(2014, 9, 23, tzinfo=ZoneInfo("UTC")), datetime.datetime(2014, 12, 20, tzinfo=ZoneInfo("UTC"))),
           'Spring': (datetime.datetime(2014, 3, 21, tzinfo=ZoneInfo("UTC")), datetime.datetime(2014, 6, 20, tzinfo=ZoneInfo("UTC")))}


class Utils:
    @staticmethod
    def get_season(date):
        date = datetime.datetime(date.year, date.month, date.day, tzinfo=ZoneInfo("UTC"))
        date = date - relativedelta(years=date.year - 2014)
        for season, (season_start, season_end) in seasons.items():
            if date >= season_start and date <= season_end:
                return season
        else:
            return 'Winter'
