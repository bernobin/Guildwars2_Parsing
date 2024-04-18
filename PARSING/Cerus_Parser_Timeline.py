from PARSING.Main_Parser import Log
import numpy as np


class CerusLogTimeline(Log):

    def get_row(self):
        d, t = self.get_date_time()

        cerus_id = self.agents[self.agents['prof'] == 25989].addr.min()

        phase_starts = get_phases(self.events)
        cerus_slams = get_slams(self.events, cerus_id)
        add_spawns = get_adds(self.agents, self.events)

        row = {
            'link': self.json['permalink'],
            'date': d,
            'time': t,
            'phase 1 start': (phase_starts['phase 1'] - phase_starts['phase 1']) / 1000,
            'phase 2 start': (phase_starts['phase 2'] - phase_starts['phase 1']) / 1000,
            'phase 3 start': (phase_starts['phase 3'] - phase_starts['phase 1']) / 1000,
#            'add spawns': [(spawn - phase_starts['phase 1']) / 1000 for spawn in add_spawns],
#            'centered slams': [(cerus_slam - phase_starts['phase 1']) / 1000 for cerus_slam in cerus_slams]
        }

        p1_adds = 1
        p2_adds = 1
        p3_adds = 1
        last_spawn = -1

        for spawn in add_spawns:
            if spawn < last_spawn + 1000:
                continue
            last_spawn = spawn

            if np.isnan(phase_starts['phase 2']) or spawn < phase_starts['phase 2']:
                row['phase 1 - add' + str(p1_adds)] = (spawn - phase_starts['phase 1']) / 1000
                p1_adds += 1
            elif np.isnan(phase_starts['phase 3']) or spawn < phase_starts['phase 3']:
                row['phase 2 - add' + str(p2_adds)] = (spawn - phase_starts['phase 2']) / 1000
                p2_adds += 1
            else:
                row['phase 3 - add' + str(p3_adds)] = (spawn - phase_starts['phase 3']) / 1000
                p3_adds += 1

        p1_slams = 1
        p2_slams = 1
        p3_slams = 1

        for slam in cerus_slams:
            if np.isnan(phase_starts['phase 2']) or slam < phase_starts['phase 2']:
                row['phase 1 - slam' + str(p1_slams)] = (slam - phase_starts['phase 1']) / 1000
                p1_slams += 1
            elif np.isnan(phase_starts['phase 3']) or slam < phase_starts['phase 3']:
                row['phase 2 - slam' + str(p2_slams)] = (slam - phase_starts['phase 2']) / 1000
                p2_slams += 1
            else:
                row['phase 3 - slam' + str(p3_slams)] = (slam - phase_starts['phase 3']) / 1000
                p3_slams += 1

        for key in row:
            try:
                if np.isnan(row[key]):
                    row[key] = None
            except TypeError:
                pass

        return row


def get_phases(e) -> dict:
    empowered_rage_buff = 69576
    empowered_regret_buff = 70821

    phase_starts = {
        'phase 1': e[e['state_change'] == 9].time.min(),
        'phase 2': e[e['skillid'] == empowered_rage_buff].head(1).time.min(),
        'phase 3': e[e['skillid'] == empowered_regret_buff].head(1).time.min()
    }


    return phase_starts


def get_slams(e, cerus_id):
    cry_of_rage_ids = [70261, 71005]    # different ids for regular and empowered

    cast_ends = e[(e['skillid'].isin(cry_of_rage_ids)) & (e['is_activation'] == 5)& (e['src_agent'] == cerus_id)].time.tolist()

    return cast_ends


def get_adds(a, e) -> list:
    malicious_shadow_spec_id = 25645
    malicious_shadow_addresses = a[a['prof'] == malicious_shadow_spec_id].addr

    spawns = [
        e[(e['src_agent'] == addr) & (e['state_change'] == 6)].time.min() for addr in malicious_shadow_addresses
    ]

    return spawns
