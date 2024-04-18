from PARSING.Main_Parser import Project

from PARSING.Cerus_Parser_Timeline import CerusLogTimeline
from PARSING.Cerus_Parser import CerusLog
from PARSING.Gorseval_Parser import GorsevalLog
from PARSING.QadimThePeerless_Parser import QadimThePeerlessLog
from PARSING.Qadim_Parser import QadimLog
from PARSING.Samarog_Parser import SamarogLog

###
### Automate token deletion if expired
### MOVE nan replacer into class method for create googlesheet
### Implement KeyNotUnique Error for PUI
###


def main():
    projects = set()

    projects.add(Project(name='[CnD] Cerus', boss='Cerus', LogClass=CerusLog))
    projects.add(Project(name='[CnD] Cerus timeline', boss='Cerus', LogClass=CerusLogTimeline))
    projects.add(Project(name='[cA] Gorseval', boss='Gorseval', LogClass=GorsevalLog))
    projects.add(Project(name='[Aves] Qadim The Peerless', boss='Qadim_The_Peerless', LogClass=QadimThePeerlessLog))
    projects.add(Project(name='[Aves] Qadim', boss='Qadim', LogClass=QadimLog))
    projects.add(Project(name='[cA] Samarog', boss='Samarog', LogClass=SamarogLog))

    projects = sorted(projects)

    for i, project in enumerate(projects):
        print(f'{i}:\t{project.name}')
#        parser = project.create_parser()
#        parser.get_csv(max_rows=5)

    selection = int(input(f'\nSelect the index of a project you are interested in:\n'))
    parser = projects[selection].create_parser()
#    parser.get_csv(max_rows=5)
    parser.get_googlesheet(sheet_id='1X_o-88KodsNycnV2FfX0egNkdqjUkQsdjvoXpfIRZO0')


if __name__ == '__main__':
    main()
