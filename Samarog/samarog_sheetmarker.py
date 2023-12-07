from parser import Parser, get_date_time
from sheets_updater import csv_to_googlesheet
import csv
import os
import numpy as np


def get_csv():
    csv_array = []

    for evtc in os.listdir(sama_parser.evtc_directory):
        row = get_row(evtc)
        csv_array.append(row)

    fieldnames = get_row(evtc).keys()
    with open('Samarog.csv', 'w') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_array)


def get_row(evtc):
    a, s, e = sama_parser.get_ase(evtc)
    ei_data = sama_parser.get_json(evtc)

    d, t = get_date_time(evtc)

    breakbar_length, breakbar_damage, breakbar_source = get_breakbar_lengths(ei_data)
    while len(breakbar_length) < 9:
        breakbar_length.append(np.nan)
        breakbar_damage.append(np.nan)
        breakbar_source.append(np.nan)

    score = 0

    row = {
        'link': ei_data['permalink'],
        'date': d,
        'time': t,
        'score': score
    }
    for i in range(9):
        row['length ' + str(i + 1)] = breakbar_length[i]
        row['damage ' + str(i + 1)] = breakbar_damage[i]
        row['source ' + str(i + 1)] = breakbar_source[i]
        row['score'] += min(breakbar_damage[i], 4500) - breakbar_length[i] * 250

    print(row)

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


sama_parser = Parser()

#get_csv()
#csv_to_googlesheet('Samarog')
#https://docs.google.com/spreadsheets/d/1Eexwq48s_lpd88N0puwF0vUyF_RCmZQbZzU7wWiTP1c/edit#gid=0&range=A1