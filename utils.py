import dateparser
import yaml
import subprocess
import tempfile
import os
import pandas as pd
import requests
import os.path as osp
import sys
import hashlib


def read_config(fn):
    with open(fn, "r") as f:
        config = yaml.safe_load(f)

    return config


def get_dates(config):
    def formatter(s):
        ps = dateparser.parse(s)
        return dict(year=ps.year, month=ps.month)

    return [formatter(d) for d in config["dates"]]


def get_sites(config,):
    id = config["sheet_details"]["id"]
    gid = config["sheet_details"]["gid"]
    sheet_base = (
        f"https://docs.google.com/spreadsheets/d/{id}/export?format=csv&gid={gid}"
    )
    tmp = tempfile.NamedTemporaryFile(delete=False)
    _ = subprocess.run(["curl", "-L", sheet_base, "--output", tmp.name])
    df = pd.read_csv(tmp.name, header=0, index_col=0)
    sites = df["ID"].values.tolist()
    os.unlink(tmp.name)
    return sites


def send_message(config, html_message):
    settings = config["email"]
    reqs = requests.post(
        f"https://api.mailgun.net/v3/{settings['domain']}/messages",
        auth=("api", settings["api"]),
        data={
            "from": "<{}>".format(settings["from"]),
            "to": settings["to"],
            "subject": "Campsite Availability",
            # "text": message,
            "html": f"<html>{html_message}</html>",
        },
    )
    return reqs


def availability_dict_to_html(availability_dict,site_urls = None):
    html = ""
    for ground_name, ground_sites in availability_dict.items():
        html += "<h2>Campground: {}</h2>".format(ground_name)
        html += "<ul>"
        for site_name, site_dates in ground_sites.items():
            if site_urls is not None:
                html += "<li><b>Campsite</b>: <a href='{}' target='_blank'>{}</a></li>".format(site_urls[site_name],site_name)
            else:
                html += "<li>Campsite: {}</li>".format(site_urls[site_name],site_name)
            html += "<ul>"
            for date in site_dates:
                html += "<li>{}</li>".format(date)
            html += "</ul>"
        html += "</ul>"
    return html

def check_html(config,new_html):
    html_dir = config['directories']['html']
    old_fn= osp.join(html_dir,'latest.html')

    if not osp.isdir(html_dir):
        print('[ERROR] : {} does not exists'.format(html_dir))
        sys.exit(-1)
    if osp.exists(old_fn):
        with open(old_fn,'r+') as of:
            old_html = of.readlines()[0]
    else:
        with open(old_fn,'w+') as of:
            of.writelines(new_html)
        return True

    new_hash = hashlib.md5(bytes('{}'.format(new_html),'utf-8'))
    old_hash = hashlib.md5(bytes('{}'.format(old_html),'utf-8'))

    if new_hash.digest() == old_hash.digest():
        return False
    else:
        with open(old_fn,'w+') as of:
            of.writelines(new_html)
        return True
