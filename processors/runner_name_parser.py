from nameparser import HumanName

def add_name_component_fields(runners):
    for runner in runners:
        human_name = HumanName(runner['name'])
        runner['first_name'] = human_name.first
        runner['last_name'] = human_name.last
        runner['middle_name'] = human_name.middle
        runner['name_suffix'] = human_name.suffix
