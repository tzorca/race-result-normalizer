from nameparser import HumanName


def add_name_component_fields(runners):
    for runner in runners:
        if not runner['name']:
            runner['first_name'] = None
            runner['last_name'] = None
            runner['middle_name'] = None
            runner['suffix'] = None
        else:
            human_name = HumanName(runner['name'])
            runner['first_name'] = human_name.first
            runner['last_name'] = human_name.last
            runner['middle_name'] = human_name.middle
            runner['name_suffix'] = human_name.suffix
