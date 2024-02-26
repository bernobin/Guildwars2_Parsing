from gw2_parser import Parser, get_date_time
from sheets_updater import csv_to_googlesheet, Google_sheet
import numpy as np

# erratic energy id = 56582
# immunity buff id = 56627
def get_row(evtc):
    a, s, e = qadimp_parser.get_ase(evtc)

    ei_data = qadimp_parser.get_json(evtc)
    try:
        link = ei_data['permalink']
    except TypeError:
        link = "no upload"

    d, t = get_date_time(evtc)
    qadim_id = a[a['prof'] == 22000].addr.min()
    start = e[e['state_change'] == 9].time.min()
    end = e[e['state_change'] == 10].time.max()

    bubble_down = get_bubble_down(e)
    magma_lift = get_magma_lifting(e)
    trans_start, trans_end = get_pylon_transformation(e)
    charge_time = get_batteringblitz_start(e, qadim_id)

    charge_end_hp = pylon_burn_start(qadim_id, e)
    knockback_end_hp = pylon_burn_end(qadim_id, e)

    t1, t2 = pylon_burn_start(qadim_id, e)
    t1_knock, t2_knock = pylon_burn_end(qadim_id, e)

    ee_dicts = [
        get_erratic_energy(e, a, bubble_down[0], magma_lift[0], qadim_id),
        get_erratic_energy(e, a, bubble_down[1], magma_lift[2], qadim_id),
        get_erratic_energy(e, a, bubble_down[2], charge_time, qadim_id),
        get_erratic_energy(e, a, t1, t1_knock, qadim_id),
        get_erratic_energy(e, a, t2, t2_knock, qadim_id)
    ]

    row = {
        'link': link,
        'date': d,
        'time': t,
        'log start': start,
        'p1 start': bubble_down[0],
        'lift 1 start': magma_lift[0],
        'erratic energy 1': round(sum(ee_dicts[0][k] for k in ee_dicts[0])/100, 2),
        'pylon flip 1 start': trans_start[0],
        'pylon flip 1 end': trans_end[0],
        'lift 1 end': magma_lift[1],

        'p2 start': bubble_down[1],
        'lift 2 start': magma_lift[2],
        'erratic energy 2': round(sum(ee_dicts[1][k] for k in ee_dicts[1])/100, 2),
        'pylon flip 2 start': trans_start[1],
        'pylon flip 2 end': trans_end[1],
        'lift 2 end': magma_lift[3],

        'p3 start': bubble_down[2],
        '40% time': get_hptime(e, 0.4, qadim_id),
        'charge north': charge_time,
        'erratic energy 3': round(sum(ee_dicts[2][k] for k in ee_dicts[2])/100, 2),
        'cc_before_40%': cc_before_40(e, qadim_id, charge_time, bubble_down[2]),

        'hp after charge 1': get_hp(qadim_id, t1, e),
        'hp after charge 2': get_hp(qadim_id, t2, e),
        'hp after knockback 1': get_hp(qadim_id, t1_knock, e),
        'hp after knockback 2': get_hp(qadim_id, t2_knock, e),
        'erratic energy 4': round(sum(ee_dicts[3][k] for k in ee_dicts[3])/100, 2),
        'erratic energy 5': round(sum(ee_dicts[4][k] for k in ee_dicts[4])/100, 2)
    }

    print(row)

    return row
# 56362 qadim bubble (down)?
# 56223 pylon conversion cast
# 56475 magma buff on player?

# interesting timestamps:
# start of last action before phase change
#
# starts charging
# destroyed pylon (north)
# returns center
# starts charging
# destroyed pylon (west)
# returns center
# death
def get_phase_duration(phases):
    phase_list = []
    if 'subPhases' not in phases[0]:
        return []
    log_end = phases[0]['end']
    for phase in phases[0]['subPhases']:
        name = phases[phase]['name']
        start = phases[phase]['start']
        end = phases[phase]['end']

        if end < log_end:
            phase_list.append([name, start, end])
    return phase_list


def get_pylon_transformation(events):
    transfo_start = events[(events['skillid'] == 56223) & (events['is_activation'] == 1)].time.to_list()
    transfo_end = events[(events['skillid'] == 56223) & (events['is_activation'] == 3)].time.to_list()

    while len(transfo_start) < 2:
        transfo_start.append(np.nan)
    while len(transfo_end) < 2:
        transfo_end.append(np.nan)
    return transfo_start, transfo_end


def get_magma_lifting(events):
    lifts = events[(events['skillid'] == 56475) & (events['iff'] == 1)].time.to_list()
    #lifts2 = events[(events['skillid'] == 56488) & (events['iff'] == 0)]

    filtered_lifts = []
    while len(lifts):
        a = lifts.pop(0)
        if len(filtered_lifts) == 0 or a > filtered_lifts[-1] + 4500:
            filtered_lifts.append(a)

    while len(filtered_lifts) < 4:
        filtered_lifts.append(np.nan)

    return filtered_lifts


def get_bubble_down(events):
    bubble_down = events[(events['skillid'] == 56362) & (events['result'] == 1)].time.to_list()

    while len(bubble_down) < 3:
        bubble_down.append(np.nan)
    return bubble_down


def get_erratic_energy(events, agents, start, end, qadim_id):
    downtime_dict = {}
    erratic_energy_id = 56582

    ee_applications = events[(events['skillid'] == erratic_energy_id) & (events['dst_agent'] == qadim_id)]
    players = ee_applications.src_agent.tolist()
    players = list(set(players))

    for player in players:
        player_ee_applications = ee_applications[
            (ee_applications['src_agent'] == player) &
            (ee_applications['time'] <= end) &
            (ee_applications['time'] >= start)
        ].time
        player_ee_delta = np.diff(player_ee_applications, prepend=start, append=end)
        player_ee_downtime = sum(player_ee_delta[player_ee_delta > 6000] - 6000)/(end-start)*100
        account = agents[agents['addr'] == player].name.min()
        try:
            downtime_dict[account.split(':')[0][:-1]] = round(100 - player_ee_downtime, 2)
        except AttributeError:
            print(account)

    return downtime_dict


def get_hptime(events, hp_percent, qadim_id):
    filt = (events['src_agent'] == qadim_id) & (events['state_change'] == 8) & (events['dst_agent'] <= hp_percent * 10000)
    return events[filt].time.min()


def get_batteringblitz_start(events, qadim_id, time=0):
    batteringram_id = 56616
    filt = (events['skillid'] == batteringram_id) & (events['src_agent'] == qadim_id) & (events['time'] >= time) & (events['is_activation'] == 1)
    return events[filt].time.min()


def cc_before_40(events, qadim_id, charge_time, bubble_down):
    cc_id = 56242
    filt = (events['skillid'] == cc_id) & (events['src_agent'] == qadim_id) & (events['time'] <= charge_time) & (events['time'] >= bubble_down)
    return not events[filt].empty

def get_hp(agent_id, time, events):
    filt = (events['state_change'] == 8) & (events['src_agent'] == agent_id) & (events['time'] <= time)
    return events[filt].dst_agent.min()/100

def pylon_burn_start(qadim_id, events):
    immunity_id = 56627

    filt_1 = (events['is_buffremove'] == 3) & (events['skillid'] == immunity_id)
    t1 = events[filt_1].time.min()

    t_star = get_batteringblitz_start(events, qadim_id, t1 + 5000)

    filt_2 = (events['is_buffremove'] == 3) & (events['skillid'] == immunity_id) & (events['time'] > t_star)
    t2 = events[filt_2].time.min()

    return [t1, t2]

def pylon_burn_end(qadim_id, events):
    force_of_retaliation_id = 56405

    t_star = get_batteringblitz_start(events, qadim_id)
    filt_1 = (events['skillid'] == force_of_retaliation_id) & (events['time'] > t_star) & (events['is_activation'] != 1)
    t1 = events[filt_1].time.min()

    t_star = get_batteringblitz_start(events, qadim_id, t1 + 5000)

    filt_2 = (events['skillid'] == force_of_retaliation_id) & (events['time'] > t_star) & (events['is_activation'] != 1)
    t2 = events[filt_2].time.min()

    return [t1, t2]





generate_reports = input("do you want to upload the logs to dps.report? Y/N (Will take a (up to very long) while if jsons have not been generated before)")
if generate_reports == "Y" or generate_reports == "y":
    qadimp_parser = Parser(generate_reports=True)
else:
    qadimp_parser = Parser(generate_reports=False)


qadimp_parser.get_csv('QadimThePeerless_Timeline', get_row)
try:
    csv_to_googlesheet('QadimThePeerless_Timeline', '1UkGLkimQY_csoNbdBtmfGlcyEdtrpHX286_5YVLdRxI')
except Exception as e:
    print("could not upload the csv to the sheet")
    print(e)

#sheet = Google_sheet('1UkGLkimQY_csoNbdBtmfGlcyEdtrpHX286_5YVLdRxI')
#sheet.from_csv(pathlib.Path.cwd() / "QadimThePeerless_Timeline.csv", "QadimThePeerless_Timeline")


a,s,e = qadimp_parser.get_ase('20240221-191123')
