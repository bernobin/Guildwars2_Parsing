# Guildwars 2 Parsing

Welcome to my gw2 parsing passion project in python.

## Directories

Some useful information about the purpose of the different directories

### Logs

The logs for parsing have to be put into this directory.
The boss directories inside this directory are what determines the structure of the input promp in `main.py`.
There is no generic boss parser (yet), so generating a new directory and selecting it will break the switchstatement in `Parser_Factory.py`.

### Misc

This folder needs to be created and hold a `credentials.json` file if your generated csv's should be automatically uploaded to some google sheet.
A `token.json` gets generated when `sheet_updater.py` is executed, which shortcuts the verification process in the future.

### Outputs

The parsed data gets dumped here in a csv file that is named after the chosen boss.

## Packages

Two different types of code are distinguished here

### PARSING

The `Main_Parser.py` contains an interface for all the boss parsers to follow. 
It implements most of the basic functionalities.
The named Parsers (i.e. `Cerus_Parser.py`) implement the get row method and set the correct directory.
`Parser_Factory.py` is a method that returns the desired parser after the input prompt resolves.

### UTILS

Code that enables some key functionalities but isnt directly used for parsing is put here.
`sheets_uploader.py` for example implements the googlesheets api for automatic uploads.

## main.py

The main method. Run this and see the magic happen.