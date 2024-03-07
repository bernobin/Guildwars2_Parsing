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
    barrier_applications = get_barrier_from_ase(e, cerus_id)

    total_barrier = get_barrier(ei_data['targets'][0]['totalDamageTaken'][0])

    row = {
        'link': link,
        'date': d,
        'time': t,
        'final percent': 100 - ei_data['targets'][0]['healthPercentBurned'],
        'barrier applications': barrier_applications,
        'total barrier': total_barrier,
        'downstates': get_downstates(ei_data['mechanics'])
    }

    print(row)

    return row


def get_barrier_from_ase(e, cerus_id):
    barrier_updates = e[(e['state_change'] == 38) & (e['src_agent'] == cerus_id)].dst_agent.to_numpy()
    barrier_deltas = np.diff(barrier_updates)

    total_barrier = sum(barrier_deltas[barrier_deltas < 1024])
    barrier_applications = len(barrier_deltas[barrier_deltas < 1024])

    return barrier_applications


def get_barrier(dmg_taken):
    sum = 0
    for src in dmg_taken:
        sum += src['shieldDamage']
    return sum


def get_downstates(mechanics):
    for mechanic in mechanics:
        if mechanic['name'] == 'Downed':
            return len(mechanic['mechanicsData'])
    return 0






cerus_parser = Parser(generate_reports=True)
# a,s,e = cerus_parser.get_ase('20240306-225226')

cerus_parser.get_csv('cerussheet', get_row)

try:
    csv_to_googlesheet('cerussheet', '11IqM36gLdmpktxcPZLLp7HIqlLVpbNsx8WfNLERR6M8')
except Exception as e:
    print("could not upload the csv to the sheet")
    print(e)