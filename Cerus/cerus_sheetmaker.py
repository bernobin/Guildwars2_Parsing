from gw2_parser import Parser, get_date_time
from sheets_updater import csv_to_googlesheet, Google_sheet
import numpy as np


def get_row(evtc):
    a, s, e = cerus_parser.get_ase(evtc)

    ei_data = cerus_parser.get_json(evtc)
    try:
        link = ei_data['permalink']
    except TypeError:
        link = "no upload"

    d, t = get_date_time(evtc)

    cerus_id = a[a['prof'] == 25989].addr.min()
    total_barrier_frac = get_barrier_frac(e, cerus_id)

    total_barrier = get_barrier(ei_data['targets'][0]['totalDamageTaken'][0])

    row = {
        'link': link,
        'date': d,
        'time': t,
        'total barrier (frac)': total_barrier_frac,
        'total barrier': total_barrier
    }

    print(row)

    return row


def get_barrier_frac(e, cerus_id):
    barrier_updates = e[(e['state_change'] == 38) & (e['src_agent'] == cerus_id)].dst_agent.to_numpy()
    barrier_deltas = np.diff(barrier_updates)

    total_barrier = 0
    for delta in barrier_deltas:
        if delta < 1000000:
            total_barrier += delta

    return total_barrier


def get_barrier(dmg_taken):
    sum = 0
    for src in dmg_taken:
        sum += src['shieldDamage']
    return sum

cerus_parser = Parser(generate_reports=True)
# a,s,e = cerus_parser.get_ase('20240306-225226')

cerus_parser.get_csv('cerussheet', get_row)

# e[(e['state_change'] == 38) & (e['src_agent'] == 20976)]
# list times of barrier
