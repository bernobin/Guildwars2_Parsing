from PARSING.Parser_Factory import parser_factory
from pathlib import Path


def main():
    p = Path('Logs')
    dirs = [d.name for d in p.iterdir() if d.is_dir()]

    print("BOSSES:")
    for index, boss in enumerate(dirs):
        print(f'{index} {boss : <20} {len(list((p / boss / "zevtc").glob("*.zevtc"))) : >4} files')

    selection = int(input("Type a number from above to generate the associated sheet:"))

    if selection in range(len(dirs)):
        parser = parser_factory(dirs[selection])
        parser.get_googlesheet(sheet_id='1X_o-88KodsNycnV2FfX0egNkdqjUkQsdjvoXpfIRZO0')
    else:
        raise ValueError(f'Expected an Integer in the {range(len(dirs))}')


if __name__ == '__main__':
    main()
