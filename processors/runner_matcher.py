def match_runners(results):
    names = {}
    runners = []
    
    for result in results:
        if not 'runner_name' in result:
            continue
        
        name = result['runner_name']
        if name in names:
            names[name].append(result)
        else:
            names[name] = [result]
            
    runner_id = 0
    for name in names:
        runners.append(make_runner_from_results(name, runner_id, names[name]))
        result['runner_id'] = runner_id
        runner_id += 1
    
    return runners
    
def make_runner_from_results(name, runner_id, results):
    runner = {'name': name, 'id': runner_id}

    ages = []
    sexes = []
    for result in results:
        ages.append(result.get('age'))
        sexes.append(result.get('sex'))
        
    runner['ages'] = str(ages)
    runner['sexes'] = str(sexes)    
    
    return runner
        
        
        