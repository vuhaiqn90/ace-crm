# -*- coding: utf-8 -*-

from odoo.fields import datetime
from datetime import timedelta


def ks_get_date(ks_date_filter_selection):
    series = ks_date_filter_selection
    return eval("ks_date_series_"+series.split("_")[0])(series.split("_")[1])


# Last Specific Days Ranges : 7, 30, 90, 365
def ks_date_series_l(ks_date_selection):
    ks_date_data = {}
    date_filter_options = {
        'day': 0,
        'week': 7,
        'month': 30,
        'quarter': 90,
        'year': 365,
    }
    ks_date_data["selected_end_date"] = datetime.now().strftime("%Y-%m-%d 23:59:59")
    ks_date_data["selected_start_date"] = (datetime.now() - timedelta(
        days=date_filter_options[ks_date_selection])).strftime("%Y-%m-%d 00:00:00")
    return ks_date_data


# Current Date Ranges : Week, Month, Quarter, year
def ks_date_series_t(ks_date_selection):
    return eval("ks_get_date_range_from_"+ks_date_selection)("current")


# Previous Date Ranges : Week, Month, Quarter, year
def ks_date_series_ls(ks_date_selection):
    return eval("ks_get_date_range_from_"+ks_date_selection)("previous")


def ks_get_date_range_from_day(date_state):
    ks_date_data = {}

    date = datetime.now()

    if date_state=="previous":
        date = date-timedelta(days=1)

    ks_date_data["selected_start_date"] = datetime(date.year,date.month,date.day)
    ks_date_data["selected_end_date"] = datetime(date.year,date.month,date.day+1) - timedelta(seconds=1)
    return ks_date_data


def ks_get_date_range_from_week(date_state):
    ks_date_data = {}

    date = datetime.now()

    if date_state=="previous":
        date = date-timedelta(days=7)

    date_iso = date.isocalendar()
    year = date_iso[0]
    week_no = date_iso[1]

    ks_date_data["selected_start_date"] = datetime.strptime('%s-W%s-1'%(year,week_no-1), "%Y-W%W-%w")
    ks_date_data["selected_end_date"] = ks_date_data["selected_start_date"] + timedelta(days=6,hours=23,minutes=59,seconds=59,milliseconds=59)
    return ks_date_data

def ks_get_date_range_from_month(date_state):
    ks_date_data = {}

    date = datetime.now()
    year = date.year
    month = date.month

    if date_state=="previous":
        month -= 1
        if month==0:
            month = 12
            year -= 1

    ks_date_data["selected_start_date"] = datetime(year,month,1)
    ks_date_data["selected_end_date"] = datetime(year,month+1,1)-timedelta(seconds=1)
    return ks_date_data


def ks_get_date_range_from_quarter(date_state):
    ks_date_data = {}

    date = datetime.now()
    year = date.year
    quarter = int((date.month - 1) / 3) + 1

    if date_state == "previous":
        quarter -= 1
        if quarter == 0:
            quarter = 4
            year -= 1

    ks_date_data["selected_start_date"] = datetime(year, 3 * quarter - 2, 1)

    month = 3 * quarter
    remaining = int(month / 12)
    ks_date_data["selected_end_date"] = datetime(year + remaining, month % 12 + 1, 1)-timedelta(seconds=1)

    return ks_date_data


def ks_get_date_range_from_year(date_state):
    ks_date_data = {}

    date = datetime.now()
    year = date.year

    if date_state=="previous":
        year -= 1

    ks_date_data["selected_start_date"] = datetime(year, 1, 1)
    ks_date_data["selected_end_date"] = datetime(year+1, 1, 1)-timedelta(seconds=1)

    return ks_date_data

