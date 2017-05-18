def output(data):
    """ Format the results for HTML output """
    i = 0
    section = {}
    # Split the data into sections based on command
    for line in data.splitlines():
        if '*** Command:' in line or 'Final Result' in line or 'ERROR!!!' in line:
            i += 1
            section[i] = [line]
        else:
            if 'Connecting to device' not in line:
                section[i].append(line)
    # Determine if the command passed, failed, or skipped
    # Also reorder test result to the top
    for k in section:
        status = 'PASS'
        p = 0
        f = 0
        for i, line in enumerate(section[k]):
            if 'FAIL' in line or 'Test Failed' in line:
                status = 'FAIL'
                q = section[k].pop(i)
                section[k].insert(1, q)
                f += 1
            elif 'PASS ' in line:
                q = section[k].pop(i)
                p += 1
                section[k].insert(p, q)
                p = i
            elif 'SKIPPING' in line:
                status = 'SKIP'
            elif 'Final Result' in line:
                status = 'FINAL'
        section[k].insert(0, '<div class="' + status.lower() + '-main">')
        if status == 'FAIL':
            section[k].insert(2 + f, '<div class="' + status.lower() + '-child">')
        else:
            section[k].insert(2, '<div class="' + status.lower() + '-child">')
    for k in section:
        section[k].append('</div></div><br>')
    result = ""
    for k in section:
        for line in section[k]:
            #if '***********' in line:
            #    line = line.replace('<br>', '')
            result = result + line

    result = result + '<script type="text/javascript" src="/jsnapy_flask/static/js/jsnapy_flask.js"></script>'
    return result
