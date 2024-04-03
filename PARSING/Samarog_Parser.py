from PARSING.Main_Parser import Parser, Log
from pathlib import Path


class SamarogParser(Parser):
    def __init__(self):
        super().__init__('Samarog')

    def get_row(self, log: Log):
        d, t = log.get_date_time()

        breakbar_length, breakbar_damage, breakbar_source = get_breakbar_lengths(log.json)
        while len(breakbar_length) < 9:
            breakbar_length.append(None)
            breakbar_damage.append(None)
            breakbar_source.append(None)

        score = 0

        row = {
            'link': log.json.get('permalink'),
            'date': d,
            'time': t,
            'score': score
        }
        for i in range(9):
            if breakbar_length[i] is None:
                break

            row['length ' + str(i + 1)] = breakbar_length[i]
            row['damage ' + str(i + 1)] = breakbar_damage[i]
            row['source ' + str(i + 1)] = breakbar_source[i]
            row['score'] += min(breakbar_damage[i], 4500) - breakbar_length[i] * 250

        return row


def get_breakbar_lengths(data):
    breakbar_lengths = []
    breakbar_damage = []
    breakbar_source = []
    for i in range(len(data['phases'])):
        phase = data['phases'][i]
        if phase['breakbarPhase']:
            breakbar_lengths.append((phase['end']-phase['start']-2000)/1000)

            highest_cc = -1
            source_cc = ""
            for player in data['players']:
                account = player['account']
                damage = player['dpsTargets'][0][i]['breakbarDamage']
                if damage > highest_cc:
                    highest_cc = damage
                    source_cc = account
            breakbar_damage.append(highest_cc)
            breakbar_source.append(source_cc)

    return breakbar_lengths, breakbar_damage, breakbar_source

