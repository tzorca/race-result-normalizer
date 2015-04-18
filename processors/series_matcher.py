from collections import defaultdict

def match_series(races):
    # Group races by month
    races_by_month = defaultdict( list )
    for race in races:
        races_by_month[race['date'].month].append(race)
    
    # Group month-grouped races by name
    races_by_month_and_name = defaultdict( list )
    for month in races_by_month:
        name_groups = defaultdict( list )
        
        for race in races_by_month[month]:
            name_groups[race['name']].append(race)

        races_by_month_and_name[month] = name_groups

    # Create and assign series
    series_id = 1
    series_list = []
    for month in races_by_month_and_name:
        month_specific_races_by_name = races_by_month_and_name[month]
        for name in month_specific_races_by_name:
            series_list.append({"id": series_id, "name": name, "month": month})
            series_races = month_specific_races_by_name[name]
            print(month_specific_races_by_name)
            for race in series_races:
                race['series_id'] = series_id
                
            series_id += 1
    
    return series_list