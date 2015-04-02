from collections import defaultdict

def match_runners(results):
    runners = []
    
    results_by_name_and_sex = defaultdict( list )
    for result in results:
        name = result.get('runner_name')
        sex = result.get('sex')
        results_by_name_and_sex[(name, sex)].append(result)
    
    runner_id = 0
    for key in results_by_name_and_sex:
        name = key[0]
        sex = key[1]
        runners.append(make_runner_from_results(name, sex, runner_id, results_by_name_and_sex[key]))
        result['runner_id'] = runner_id
        runner_id += 1
    
    return runners
    
def make_runner_from_results(name, sex, runner_id, results):
    runner = {'name': name, 'sex': sex, 'id': runner_id}

    birthdate_lte_list = []
    for result in results:
        birthdate_lte = result.get('birthdate_lte')
        if birthdate_lte:
            birthdate_lte = birthdate_lte.strftime("%Y-%m-%d")
        birthdate_lte_list.append(birthdate_lte)
        
    runner['birthdate_lte_list'] = str(birthdate_lte_list)
    
    return runner
        
        
        