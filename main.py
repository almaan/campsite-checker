import camps
import utils as ut
import argparse as arp



def main(config):

    camp_ids = ut.get_sites(config)
    dates = ut.get_dates(config)

    available_dates = dict()
    urls = dict()
    for camp_id in camp_ids:
        camp_obj = camps.CampGround(camp_id)
        _available_dates,_url = camp_obj.get_availability(dates)
        available_dates.update(_available_dates)
        urls.update(_url)

    html = ut.availability_dict_to_html(available_dates,urls)
    send_message = ut.check_html(config,html)
    if send_message:
        resp = ut.send_message(config,html)

if __name__ == '__main__':
    prs = arp.ArgumentParser()
    aa = prs.add_argument

    aa('-df','--design_file')

    args = prs.parse_args()

    config = ut.read_config(args.design_file)

    main(config)
