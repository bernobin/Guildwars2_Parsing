from PARSING.Main_Parser import Parser, Log
import numpy as np


class GorsevalParser(Parser):
    def __init__(self):
        super().__init__('Gorseval')

    def get_row(self, log: Log):
        d, t = log.get_date_time()

        gorse_id = log.agents[log.agents['prof'] == 15429].addr.min()
        chargedsoul_ids = log.agents[log.agents['prof'] == 15434].addr.tolist()

        phase_starts, phase_ends = get_phase_start_end(log.events, gorse_id)
        split_starts = get_split_starts(log.events, chargedsoul_ids)
        split_deaths = get_split_deaths(log.events, chargedsoul_ids)

        row = {
            'link': log.json['permalink'],
            'date': d,
            'time': t,

            'p1 breakbar start': (get_cc_start_end(log.events, phase_starts[0])[0] - phase_starts[0]) / 1000,
            'p1 breakbar end': (get_cc_start_end(log.events, phase_starts[0])[1] - phase_starts[0]) / 1000,
            'p1 end': (phase_ends[0] - phase_starts[0]) / 1000,
            's1 start': (split_starts[0] - phase_starts[0]) / 1000,
            's1 add1 death': (split_deaths[0] - phase_starts[0]) / 1000,
            's1 add2 death': (split_deaths[1] - phase_starts[0]) / 1000,
            's1 add3 death': (split_deaths[2] - phase_starts[0]) / 1000,
            's1 add4 death': (split_deaths[3] - phase_starts[0]) / 1000,

            'p2 start': (phase_starts[1] - phase_starts[0]) / 1000,
            'p2 breakbar start': (get_cc_start_end(log.events, phase_starts[1])[0] - phase_starts[0]) / 1000,
            'p2 breakbar end': (get_cc_start_end(log.events, phase_starts[1])[1] - phase_starts[0]) / 1000,
            'p2 end': (phase_ends[1] - phase_starts[0]) / 1000,
            's2 start': (split_starts[1] - phase_starts[0]) / 1000,
            's2 add1 death': (split_deaths[4] - phase_starts[0]) / 1000,
            's2 add2 death': (split_deaths[5] - phase_starts[0]) / 1000,
            's2 add3 death': (split_deaths[6] - phase_starts[0]) / 1000,
            's2 add4 death': (split_deaths[7] - phase_starts[0]) / 1000,

            'p3 start': (phase_starts[2] - phase_starts[0]) / 1000,
            'p3 breakbar start': (get_cc_start_end(log.events, phase_starts[2])[0] - phase_starts[0]) / 1000,
            'p3 breakbar end': (get_cc_start_end(log.events, phase_starts[2])[1] - phase_starts[0]) / 1000,
            'p3 end': (phase_ends[2] - phase_starts[0]) / 1000,
        }

        for key in row:
            try:
                if np.isnan(row[key]):
                    row[key] = None
            except TypeError:
                pass

        return row


def get_cc_start_end(e, phase_start):
    breakbar_change_id = 23276
    filt = (e['skillid'] == breakbar_change_id) & (e['time'] >= phase_start + 5000) & (e['time'] <= phase_start + 25000)
    states = e[filt].head(2).time.tolist()

    if len(states) < 1:
        return np.nan, np.nan
    elif len(states) < 2:
        return states[0], np.nan
    return states[0], states[1]


def get_phase_start_end(e, gorse_id):
    protective_shadow = e[e['skillid'] == 31877]
    phase1_start = e[e['state_change'] == 9].time.min()  # finds the logstart

    phase1_end = protective_shadow[(protective_shadow['is_buffremove'] == 0) & (protective_shadow['time'] > 0)].time.min()
    phase2_start = protective_shadow[protective_shadow['is_buffremove'] == 1].time.min()
    phase2_end = protective_shadow[(protective_shadow['is_buffremove'] == 0) & (protective_shadow['time'] > phase1_end)].time.min()
    phase3_start = protective_shadow[(protective_shadow['is_buffremove'] == 1) & (protective_shadow['time'] > phase2_start)].time.min()

    phase3_end = np.nan
    final_health = e[(e['state_change'] == 8) & (e['src_agent'] == gorse_id)].dst_agent.min()
    if final_health < 100:
        phase3_end = e[(e['state_change'] == 8) & (e['src_agent'] == gorse_id)].time.max()

    return [phase1_start, phase2_start, phase3_start], [phase1_end, phase2_end, phase3_end]


def get_split_starts(e, chargedsoul_ids):
    filt = (e['state_change'] == 6) & (e['src_agent'].isin(chargedsoul_ids))
    spawns = e[filt].time
    split1_start = spawns.min()

    filt = (e['state_change'] == 6) & (e['src_agent'].isin(chargedsoul_ids)) & (e['time'] > split1_start + 5000)
    spawns = e[filt].time
    split2_start = spawns.min()

    return [split1_start, split2_start]


def get_split_deaths(e, chargedsoul_ids):
    filt = (e['state_change'] == 4) & (e['src_agent'].isin(chargedsoul_ids))
    deaths = e[filt].copy()
    deaths.set_index('src_agent', drop=True, inplace=True)
    deaths.sort_index(inplace=True)

    deaths_array = deaths.time.tolist()
    while len(deaths_array) < 8:
        deaths_array.append(np.nan)

    return deaths_array
