from gw2_parser import Parser, get_date_time
from sheets_updater import csv_to_googlesheet


def get_row(evtc):
    a, s, e = qadim_parser.get_ase(evtc)
    ei_data = qadim_parser.get_json(evtc)

    d, t = get_date_time(evtc)

    row = {
        'link': ei_data['permalink'],
        'date': d,
        'time': t
    }

    lamp_duration = get_lamp_duration(e)
    for i in range(3):
        row['lamp ' + str(i+1)] = lamp_duration[i] / 1000

    print(row)
    return row


# Returns array of length 3. Array[i] is the duration (ms) of lamp i+1.
# will skip info of logs where we finish lamp but don't reach burn?
def get_lamp_duration(events):
    lamp_bond_id = 51726
    power_of_the_lamp_id = 52035
    starts = get_phase_starts(events)

    lamp_bond_times = events.loc[(events['skillid'] == lamp_bond_id) & (events['is_buffremove'] == 0)].time
    power_of_the_lamp_times = events.loc[(events['skillid'] == power_of_the_lamp_id) & (events['buff_dmg'] == 0)].time

    entry_events = [lamp_bond_times[lamp_bond_times <= starts[i]].max() for i in range(3)]
    exit_events = [power_of_the_lamp_times[power_of_the_lamp_times <= starts[i]].max() for i in range(3)]

    return [exit_events[i] - entry_events[i] for i in range(3)]


# Returns array of length 3. Array[i] is the time main phase i+1 start.
def get_phase_starts(events):
    flame_armor_id = 52568

    starts = [-1, -1, -1]

    flame_armor_drop = events.loc[(events['skillid'] == flame_armor_id) & (events['result'] == 1)].time
    starts[0] = flame_armor_drop.min()
    starts[1] = flame_armor_drop[flame_armor_drop > starts[0]].min()
    starts[2] = flame_armor_drop[flame_armor_drop > starts[1]].min()

    return starts


qadim_parser = Parser()
qadim_parser.get_csv('Qadim', get_row)
