from abc import ABC, abstractmethod
from pathlib import Path
from zipfile import ZipFile
from csv import DictWriter
from UTILS.sheets_uploader import get_creds, update_sheet
import struct
import numpy as np
import pandas as pd
import requests
import json
import time

GW2EI_UPLOAD = 'https://dps.report/uploadContent?json=1&generator=ei'
GW2EI_GETJSON = 'https://dps.report/getJson?id='
OUTPUTS = Path('./Outputs')

ENCODING = "utf-8"

AGENT_20180724_DTYPE = np.dtype([
    ('addr', np.uint64),  # required: https://github.com/pandas-dev/pandas/issues/3506
    ('prof', np.uint32),
    ('is_elite', np.uint32),
    ('toughness', np.uint16),
    ('concentration', np.uint16),
    ('healing', np.uint16),
    ('hitbox_width', np.uint16),
    ('condition', np.uint16),
    ('hitbox_height', np.uint16),
    ('name', '|S64'),   # fixed length string
], True)

SKILL_DTYPE = np.dtype([
    ('id', np.int32),
    ('name', 'S64'),
], True)

EVENT_DTYPE = np.dtype([
    ('time', np.uint64),
    ('src_agent', np.uint64),
    ('dst_agent', np.uint64),
    ('value', np.float32),
    ('buff_dmg', np.int32),
    ('overstack_value', np.uint32),
    ('skillid', np.uint32),
    ('src_instid', np.uint16),
    ('dst_instid', np.uint16),
    ('src_master_instid', np.uint16),
    ('dst_master_instid', np.uint16),
    ('iff', np.uint8),
    ('buff', np.uint8),
    ('result', np.uint8),
    ('is_activation', np.uint8),
    ('is_buffremove', np.uint8),
    ('is_ninety', np.uint8),
    ('is_fifty', np.uint8),
    ('is_moving', np.uint8),
    ('state_change', np.uint8),
    ('is_flanking', np.uint8),
    ('is_shields', np.uint8),
    ('is_offcycle', np.uint8),
    ('padding', np.uint32)
], True)


class Parser(ABC):
    def __init__(self):
        self.boss = 'None'
        self.log_directory = Path('./Logs') / self.boss / 'zevtc'

    @abstractmethod
    def get_row(self, log):
        pass

    def get_csv(self):
        csv_arr = []
        fieldnames = []

        for zevtc_file in self.log_directory.glob("*.zevtc"):
            try:
                log = Log(zevtc_file=zevtc_file)
                row = self.get_row(log)
                print(row)
                csv_arr.append(row)

                keys = [i for i in row.keys()]
                fieldnames = update_fieldnames(fieldnames, keys)

            except Exception as e:
                print(f'{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e} with log {zevtc_file.name}')

        with open(OUTPUTS / (self.boss + '.csv'), 'w') as f:
            writer = DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_arr)

        print('\nCreated the csv: ', OUTPUTS / (self.boss + '.csv'))

        return csv_arr, fieldnames

    def get_googlesheet(self, sheet_id):
        csv_array, fieldnames = self.get_csv()
        sheet_values = [[key for key in fieldnames]] + \
                       [[row[key] if key in row else None for key in fieldnames] for row in csv_array]
        sheet_range = self.boss + '_DataDump'
        try:
            creds = get_creds()
            update_sheet(creds, sheet_id, sheet_range, sheet_values)
            print(f'\nuploaded everything to: https://docs.google.com/spreadsheets/d/{sheet_id}/edit#gid=902530857')
        except FileNotFoundError:
            print(f'\nMissing credentials.json file in Misc directory. Could not update the googlesheet.')
        pass

    def __repr__(self):
        return f"{self.__class__.__name__} ({self.boss})"


class Log:
    def __init__(self, zevtc_file):
        self.zevtc_file = zevtc_file
        self.agents, self.skills, self.events = generate_ase(zevtc_file=zevtc_file)
        self.json = generate_json(zevtc_file=zevtc_file)

    def get_date_time(self):
        d, t = self.zevtc_file.stem.split('-')

        # Formating
        d = d[0:4] + '.' + d[4:6] + '.' + d[6:8]
        t = t[0:2] + ':' + t[2:4] + ':' + t[4:6]

        return d, t

    def __repr__(self):
        return f"{self.__class__.__name__} ({self.zevtc_file})"


def generate_ase(zevtc_file):
    evtc_file = zevtc_file.parents[1] / 'evtc' / zevtc_file.stem
    if not evtc_file.exists():
        with ZipFile(zevtc_file) as zip_ref:
            zip_ref.extract(zevtc_file.stem, evtc_file.parent)

    with evtc_file.open(mode='rb') as f:
        # Header
        header = f.read(16)
        evtc, version, area_id, revision = struct.unpack('<4s9sHB', header)

        version = version.decode(ENCODING).rstrip('\0')

        # Agents
        dtype = AGENT_20180724_DTYPE
        num_agents, = struct.unpack("<i", f.read(4))
        agents_buffer = f.read(dtype.itemsize * num_agents)
        agents_df = pd.DataFrame(np.frombuffer(agents_buffer, dtype=AGENT_20180724_DTYPE))

        agents_df['name'] = agents_df['name'].apply(lambda x: x.decode())

        # Skills
        num_skills, = struct.unpack("<i", f.read(4))
        skills_buffer = f.read(SKILL_DTYPE.itemsize * num_skills)
        skills_df = pd.DataFrame(np.frombuffer(skills_buffer, dtype=SKILL_DTYPE))

        # Events
        events_buffer = f.read()
        events_df = pd.DataFrame(np.frombuffer(events_buffer, dtype=EVENT_DTYPE))

    return agents_df, skills_df, events_df


def generate_json(zevtc_file):
    json_file = zevtc_file.parents[1] / 'json' / (zevtc_file.stem + ".json")
    if json_file.exists():
        t = json_file.open()
        return json.load(t)

    try:
        with zevtc_file.open(mode='rb') as f:
            r = requests.post(GW2EI_UPLOAD, files={'file': f}, timeout=60000)
        simple_report = r.json()
        report_id = simple_report['id']
        report_permalink = simple_report['permalink']

        r = requests.post(GW2EI_GETJSON + report_id, timeout=60000)
        detailed_report = r.json()
        detailed_report['permalink'] = report_permalink

        with json_file.open(mode='w') as f:
            print('successfully created json file for', zevtc_file.name)
            json.dump(detailed_report, f)
        return detailed_report

    except json.decoder.JSONDecodeError:
        print('got jsonDecodeError, sleeping 1 minute')
        time.sleep(60)
        return generate_json(zevtc_file)


def update_fieldnames(fieldnames, new_row):
    updated_fieldnames = []

    i, j = 0, 0
    while i < len(fieldnames) and j < len(new_row):
        if fieldnames[i] == new_row[j]:
            updated_fieldnames.append(new_row[j])
            i += 1
            j += 1
        else:
            if new_row[j] not in fieldnames:
                updated_fieldnames.append(new_row[j])
                j += 1
            else:
                k = fieldnames.index(new_row[j])
                while i < k:
                    updated_fieldnames.append(fieldnames[i])
                    i += 1

    while i < len(fieldnames):
        updated_fieldnames.append(fieldnames[i])
        i += 1
    while j < len(new_row):
        updated_fieldnames.append(new_row[j])
        j += 1

    return updated_fieldnames
