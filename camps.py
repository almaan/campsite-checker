import requests
from datetime import datetime
import re
import constants as C
from typing import List, Dict, Tuple


def get_ground_name(campsite_id: str, header: str) -> str:
    camp_url = C.CampRelated.campground_web_url + str(campsite_id)
    html_response = requests.get(camp_url, headers=header).text
    try:
        campsite_name = re.search(C.CampRelated.campsite_name_pattern, html_response)[0]
    except TypeError:
        campsite_name = campsite_id
    return campsite_name


def datetime_format(year: int, month: int) -> str:
    return datetime(year, month, 1).isoformat() + ".000Z"


class CampGround:
    def __init__(self, campsite_id: str) -> None:
        self.campsite_id = campsite_id
        self.url = C.CampRelated.campground_api_url.format(campsite_id)
        self.site_base_url = C.CampRelated.campsite_api_url

        self.header = {"User-Agent": "Defined"}
        self.ground_name = get_ground_name(self.campsite_id, self.header)

    def get_availability(
        self,
        dates: str | List[str],
        return_urls: bool = True,
        exclude_accessible: bool = True,
    ) -> Dict[str, str] | Tuple[Dict[str, str], Dict[str, str]]:

        if not isinstance(dates, list):
            dates = [dates]

        available_dates = {}
        site_urls = {}
        for date in dates:
            params = {"start_date": datetime_format(date["year"], date["month"])}
            req = requests.get(self.url, params=params, headers=self.header)
            if not req.ok:
                available_dates = {self.ground_name: {}}
                if return_urls:
                    return available_dates, {}
                else:
                    return available_dates

            data = req.json()

            campsite_data = data["campsites"]

            for site_name, site_info in campsite_data.items():
                site = site_info["site"]
                if site not in available_dates:
                    available_dates[site] = list()
                    site_urls[site] = self.site_base_url + site_name

                availability = site_info["availabilities"]
                availability = [
                    k.split("T")[0]
                    for k, v in availability.items()
                    if v == C.CampRelated.campsite_availability_value
                ]

                available_dates[site] += availability

        available_dates = {k: v for k, v in available_dates.items() if len(v) > 0}
        site_urls = {k: site_urls[k] for k in available_dates.keys()}
        available_dates = {self.ground_name: available_dates}

        if return_urls:
            return available_dates, site_urls

        return available_dates
