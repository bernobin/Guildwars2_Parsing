from PARSING.Main_Parser import Log
from UTILS.dash_template import generate_dash
import numpy as np


class CerusLog(Log):
    def get_row(self):
        d, t = self.get_date_time()

        cerus_id = self.agents[self.agents['prof'] == 25989].addr.min()
        barrier_applications = get_barrier_from_ase(self.events, cerus_id)
        total_stacks = len(self.events[(self.events['skillid'] == 69550) & (self.events['dst_agent'] == cerus_id)])

        total_barrier = get_barrier(self.json['targets'][0]['totalDamageTaken'][0])

        row = {
            'link': self.json['permalink'],
            'date': d,
            'time': t,
            'stacks P1': stacks(self.json['mechanics'], get_timespan(self.json['phases'], 'Phase 1')),
            'stacks P2': stacks(self.json['mechanics'], get_timespan(self.json['phases'], 'Phase 2')),
            'final percent': round(100 - self.json['targets'][0]['healthPercentBurned'], 2),
            'final stacks': total_stacks,
            'barrier applications': barrier_applications,
            'total barrier': total_barrier,
            'downstates': get_downstates(self.json['mechanics'])
        }
        return row

    @staticmethod
    def generate_dash(df):
        generate_dash(df)
        pass


def get_barrier_from_ase(e, cerus_id):
    barrier_updates = e[(e['state_change'] == 38) & (e['src_agent'] == cerus_id)].dst_agent.to_numpy()
    barrier_deltas = np.diff(barrier_updates)

    total_barrier = sum(barrier_deltas[barrier_deltas < 1024])
    barrier_applications = len(barrier_deltas[barrier_deltas < 1024])

    return barrier_applications


def get_barrier(dmg_taken):
    summ = 0
    for src in dmg_taken:
        summ += src['shieldDamage']
    return summ


def get_downstates(mechanics):
    for mechanic in mechanics:
        if mechanic['name'] == 'Downed':
            return len(mechanic['mechanicsData'])
    return 0


def stacks(mechanics, timespan):
    if timespan is not None:
        for mech in mechanics:
            if mech['name'] == 'Emp.A':
                counter = 0
                for event in mech['mechanicsData']:
                    if timespan[0] < event['time'] < timespan[1]:
                        counter += 1
                return counter
    return None


def get_timespan(phases, phase_name):
    fight_end = phases[0]['end']
    for phase in phases:
        if phase['name'] == phase_name and phase['end'] < fight_end:
            return [phase['start'], phase['end']]
    return None
