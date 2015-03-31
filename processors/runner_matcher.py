def match_runners(results):
    names = {}
    
    for result in results:
        if not "Name" in result:
            continue
        
        name = result["Name"]
        if name in names:
            names[name].append(result)
        else:
            names[name] = [result]

    for name in names:
        print("%s = %d" % (name, len(names[name])))
        
    print(list(names.keys()))