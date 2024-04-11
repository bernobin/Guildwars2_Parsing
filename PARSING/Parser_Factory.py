class ParserUI:
    def __init__(self):
        self.registered_parsers = {}

    def create_parser(self):
        bosses = list(self.registered_parsers.keys())
        for index, boss in enumerate(bosses):
            print(f'{index} {boss : <20} {len(list(self.registered_parsers[boss].log_directory.glob("*.zevtc"))) : >4} files')

        selected_index = input("select the index of one boss:\n")
        if bosses[int(selected_index)] in self.registered_parsers:
            return self.registered_parsers[bosses[int(selected_index)]]
        else:
            raise ValueError("input must be between 0 and", len(bosses)-1)