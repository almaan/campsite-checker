import requests
from datetime import datetime
import re

def get_ground_name(campsite_id, header):
    camp_url = "https://www.recreation.gov/camping/campgrounds/" + str(campsite_id)
    html_response = requests.get(camp_url, headers=header).text
    campsite_name = re.search("(?s)(?<=<h1>)(.+?)(?=</h1>)", html_response)[0]
    return campsite_name


def read_campsites(fname):
    with open(fname, "r") as f:
        lines = f.readlines()
    lines = [l.rstrip("\n") for l in lines]
    return lines


class CampGround:
    def __init__(self, campsite_id):
        self.campsite_id = campsite_id
        self.url = f"https://www.recreation.gov/api/camps/availability/campground/{campsite_id}/month"
        self.site_base_url = 'https://www.recreation.gov/camping/campsites/'

        self.header = {"User-Agent": 'Defined'}
        self.ground_name = get_ground_name(self.campsite_id, self.header)

    def get_availability(self, dates,return_urls = True):


        if not isinstance(dates, list):
            dates = [dates]

        available_dates = {}
        site_urls = {}
        for date in dates:
            params = {
                "start_date": datetime(date["year"], date["month"], 1).isoformat()
                + ".000Z"
            }
            data = requests.get(self.url, params=params, headers=self.header).json()
            campsite_data = data["campsites"]

            for site_name,site_info in campsite_data.items():
                site = site_info["site"]
                if site not in available_dates:
                    available_dates[site] = list()
                    site_urls[site] = self.site_base_url + site_name

            availability = site_info["availabilities"]
            availability = [
                k.split("T")[0] for k, v in availability.items() if v == "Available"
            ]

            available_dates[site] += availability

        available_dates = {k: v for k, v in available_dates.items() if len(v) > 0}
        site_urls = {k:site_urls[k] for k in available_dates.keys()}
        available_dates =  {self.ground_name: available_dates}

        if return_urls:
            return available_dates,site_urls

        return available_dates

