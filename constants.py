from enum import Enum


class CampRelated(str,Enum):
    campground_api_url = 'https://www.recreation.gov/api/camps/availability/campground/{}/month'
    campground_web_url = 'https://www.recreation.gov/camping/campgrounds/'
    campsite_api_url = 'https://www.recreation.gov/camping/campsites/'
    campsite_name_pattern = "(?s)(?<=<h1>)(.+?)(?=</h1>)"

    campsite_availability_value = 'Available'


class SheetRelated(str,Enum):
    sheet_url = 'https://docs.google.com/spreadsheets/d/{}/export?format=csv&gid={}'
