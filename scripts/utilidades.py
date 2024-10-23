import datetime
import calendar
from re import findall

def search_df(regex: str, df, case=False):
    # Search all the text columns of `df`, return rows with any matches.
    textlikes = df.select_dtypes(include=[object, "string"])
    return df[
        textlikes.apply(
            lambda column: column.str.contains(regex, regex=True, case=case, na=False)
        ).any(axis=1)
    ]

#  Devuelve la fecha final del mes según la fecha indicada en el parámetro
def last_date_of_month(any_date):
    # El dia 28 existe en todos los meses. 4 días después, siempre es el próximo mes
    next_month = any_date.replace(day=28) + datetime.timedelta(days=4)
    # restando el número del día actual nos devuelve un mes
    return next_month - datetime.timedelta(days=next_month.day)
def ultimo_dia_mes(fecha):
    year = fecha.year
    mes = fecha.month
    rng = calendar.monthrange(year, mes)
    return datetime.datetime(year, mes, rng[1])

def date_today():
    hoy = datetime.datetime.now()
    t = datetime.time(hoy.hour, hoy.minute, hoy.second)
    d = datetime.date.today()
    dt = datetime.datetime.combine(d, t)
    return dt