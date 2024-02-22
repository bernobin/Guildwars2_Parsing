import pathlib
import time
import numpy as np
import pandas as pd
import struct
import zipfile
import json
import requests
import csv

GW2EI_UPLOAD = 'https://dps.report/uploadContent?json=1&generator=ei'
GW2EI_GETJSON = 'https://dps.report/getJson?id='

# format of data in evtc files
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

state_change_types = [
    'CBTS_NONE',            # not used - not this kind of event
    'CBTS_ENTERCOMBAT',     # src_agent entered combat, dst_agent is subgroup
    'CBTS_EXITCOMBAT',      # src_agent left combat
    'CBTS_CHANGEUP',        # src_agent is now alive
    'CBTS_CHANGEDEAD',      # src_agent is now dead
    'CBTS_CHANGEDOWN',      # src_agent is now downed
    'CBTS_SPAWN',           # src_agent is now in game tracking range (not in realtime api)
    'CBTS_DESPAWN',         # src_agent is no longer being tracked (not in realtime api)
    'CBTS_HEALTHUPDATE',    # src_agent is at health percent. dst_agent = percent * 10000 (eg. 99.5% will be 9950) (not in realtime api)
    'CBTS_LOGSTART',        # log start. value = server unix timestamp **uint32**. buff_dmg = local unix timestamp
    'CBTS_LOGEND',          # log end. value = server unix timestamp **uint32**. buff_dmg = local unix timestamp
    'CBTS_WEAPSWAP',        # src_agent swapped weapon set. dst_agent = current set id (0/1 water, 4/5 land)
    'CBTS_MAXHEALTHUPDATE', # src_agent has had it's maximum health changed. dst_agent = new max health (not in realtime api)
    'CBTS_POINTOFVIEW',     # src_agent is agent of "recording" player  (not in realtime api)
    'CBTS_LANGUAGE',        # src_agent is text language  (not in realtime api)
    'CBTS_GWBUILD',         # src_agent is game build  (not in realtime api)
    'CBTS_SHARDID',         # src_agent is sever shard id  (not in realtime api)
    'CBTS_REWARD',          # src_agent is self, dst_agent is reward id, value is reward type. these are the wiggly boxes that you get
    'CBTS_BUFFINITIAL',     # combat event that will appear once per buff per agent on logging start (statechange==18, buff==18, normal cbtevent otherwise)
    'CBTS_POSITION',        # src_agent changed, cast float* p = (float*)&dst_agent, access as x/y/z (float[3]) (not in realtime api)
    'CBTS_VELOCITY',        # src_agent changed, cast float* v = (float*)&dst_agent, access as x/y/z (float[3]) (not in realtime api)
    'CBTS_FACING',          # src_agent changed, cast float* f = (float*)&dst_agent, access as x/y (float[2]) (not in realtime api)
    'CBTS_TEAMCHANGE',      # src_agent change, dst_agent new team id
    'CBTS_ATTACKTARGET',    # src_agent is an attacktarget, dst_agent is the parent agent (gadget type), value is the current targetable state (not in realtime api)
    'CBTS_TARGETABLE',      # dst_agent is new target-able state (0 = no, 1 = yes. default yes) (not in realtime api)
    'CBTS_MAPID',           # src_agent is map id  (not in realtime api)
    'CBTS_REPLINFO',        # internal use, won't see anywhere
    'CBTS_STACKACTIVE',     # src_agent is agent with buff, dst_agent is the stackid marked active
    'CBTS_STACKRESET',      # src_agent is agent with buff, value is the duration to reset to (also marks inactive), pad61-pad64 buff instance id
    'CBTS_GUILD',           # src_agent is agent, dst_agent through buff_dmg is 16 byte guid (client form, needs minor rearrange for api form)
    'CBTS_BUFFINFO',        # is_flanking = probably invuln, is_shields = probably invert, is_offcycle = category, pad61 = stacking type, pad62 = probably resistance, src_master_instid = max stacks, overstack_value = duration cap (not in realtime)
    'CBTS_BUFFFORMULA',     # (float*)&time[8]: type attr1 attr2 param1 param2 param3 trait_src trait_self, (float*)&src_instid[2] = buff_src buff_self, is_flanking = !npc, is_shields = !player, is_offcycle = break, overstack = value of type determined by pad61 (none/number/skill) (not in realtime, one per formula)
    'CBTS_SKILLINFO',       # (float*)&time[4]: recharge range0 range1 tooltiptime (not in realtime)
    'CBTS_SKILLTIMING',     # src_agent = action, dst_agent = at millisecond (not in realtime, one per timing)
    'CBTS_BREAKBARSTATE',   # src_agent is agent, value is u16 game enum (active, recover, immune, none) (not in realtime api)
    'CBTS_BREAKBARPERCENT', # src_agent is agent, value is float with percent (not in realtime api)
    'CBTS_ERROR',           # (char*)&time[32]: error string (not in realtime api)
    'CBTS_TAG',             # src_agent is agent, value is the id (volatile, game build dependent) of the tag, buff will be non-zero if commander
    'CBTS_BARRIERUPDATE',   # src_agent is at barrier percent. dst_agent = percent * 10000 (eg. 99.5% will be 9950) (not in realtime api)
    'CBTS_STATRESET',       # with arc ui stats reset (not in log), src_agent = npc id of active log
    'CBTS_EXTENSION',       # cbtevent with statechange byte set to this
    'CBTS_APIDELAYED',      # cbtevent with statechange byte set to this
    'CBTS_INSTANCESTART',   # src_agent is ms time at which the instance likely was started
    'CBTS_TICKRATE',        # every 500ms, src_agent = 25 - tickrate (when tickrate < 21)
    'CBTS_LAST90BEFOREDOWN',# src_agent is enemy agent that went down, dst_agent is time in ms since last 90% (for downs contribution)
    'CBTS_EFFECT',          # src_agent is owner. dst_agent if at agent, else &value = float[3] xyz, &iff = float[2] xy orient, &pad61 = float[1] z orient, skillid = effectid. if is_flanking: duration = trackingid. &is_shields = uint16 duration. if effectid = 0, end &is_shields = trackingid (not in realtime api)
    'CBTS_IDTOGUID',        # &src_agent = 16byte persistent content guid, overstack_value is of contentlocal enum, skillid is content id  (not in realtime api)
    'CBTS_LOGNPCUPDATE',    # log npc update. value = server unix timestamp **uint32**. buff_dmg = local unix timestamp. src_agent = species id. dst_agent = agent, flanking = is gadget
    'CBTS_IDLEEVENT',       # internal use, won't see anywhere
    'CBTS_EXTENSIONCOMBAT', # cbtevent with statechange byte set to this, treats skillid as skill for evtc skill table
    'CBTS_UNKNOWN'
]


class Parser:
    def __init__(self, generate_reports=True):
        self.evtc_directory = pathlib.Path.cwd() / 'evtcFiles'
        self.json_directory = pathlib.Path.cwd() / 'jsonFiles'
        self.zevtc_directory = pathlib.Path.cwd() / 'zevtcFiles'
        self.generate_reports = generate_reports

        if not self.evtc_directory.exists():
            self.evtc_directory.mkdir()
        if not self.json_directory.exists():
            self.json_directory.mkdir()
        if not self.zevtc_directory.exists():
            self.zevtc_directory.mkdir()

        for z_file in self.zevtc_directory.iterdir():
            file = self.evtc_directory / z_file.name
            if not file.exists():
                with zipfile.ZipFile(z_file) as zip_ref:
                    zip_ref.extractall(self.evtc_directory)

    def get_ase(self, evtc_name):
        evtc_file = self.evtc_directory / evtc_name

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

    def get_json(self, evtc_name):
        zevtc = evtc_name + '.zevtc'
        zevtc_path = self.zevtc_directory / zevtc

        json_path = self.json_directory / evtc_name
        if json_path.exists():
            t = open(json_path)
            return json.load(t)

        elif self.generate_reports:
            try:
                with zevtc_path.open(mode='rb') as f:
                    r = requests.post(GW2EI_UPLOAD, files={'file': f}, timeout=60000)
                simple_report = r.json()
                report_id = simple_report['id']
                report_permalink = simple_report['permalink']

                r = requests.post(GW2EI_GETJSON + report_id, timeout=60000)
                detailed_report = r.json()
                detailed_report['permalink'] = report_permalink

                with json_path.open(mode='w') as f:
                    print('successfully created json file for', evtc_name)
                    json.dump(detailed_report, f)

                return detailed_report

            except json.decoder.JSONDecodeError:
                print('got jsonDecodeError, sleeping 1 minute')
                time.sleep(60)
                return self.get_json(evtc_name)
        return "no upload"

    def get_agent_trails(self, evtc_name):
        trails = {}
        a, s, e = self.get_ase(evtc_name)
        a.set_index('addr', inplace=True)
        for addr, data in a.iterrows():
            trails[addr] = {
                'name': data['name'],
                'prof': data['prof'],
                'elite': data['is_elite'],
                'locations': [],
                'times': []
            }

        pos_view = e.loc[e['state_change'] == 19]
        pos_view['dst_agent'] = pos_view['dst_agent'].map(q_to_ff)
        for index, data in pos_view.iterrows():
            addr = data['src_agent']
            x, y = data['dst_agent']
            z = data['value']
            t = data['time']

            try:
                trails[addr]['locations'].append((x, y, z))
                trails[addr]['times'].append(t)
            except KeyError:
                trails[addr] = {
                    'name': 'unknown',
                    'prof': 'unknown',
                    'elite': 'unknown',
                    'locations': [(x, y, z)],
                    'times': [t]
                }
        return trails

    def get_csv(self, name, get_row):
        csv_array = []
        fieldnames = []

        for evtc in self.evtc_directory.iterdir():
            row = get_row(evtc.name)
            csv_array.append(row)
            if len(row) > len(fieldnames):
                fieldnames = row.keys()

        with open(name + '.csv', 'w') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_array)


# basic function that extracts time and date from an evtc, assuming the filename is original
def get_date_time(evtc):
    d, t = evtc.split('-')

    d = d[0:4] + '.' + d[4:6] + '.' + d[6:8]
    t = t[0:2] + ':' + t[2:4] + ':' + t[4:6]

    return d, t


# basic function that converts an unsigned longlong into 2 floats. Used for extracting coordinates in a,s,e
def q_to_ff(q):
    return struct.unpack('ff', struct.pack('Q', q))
