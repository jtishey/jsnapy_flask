import re


def formatting(post_log):
    """ Do some output formatting for jsnapy_flask based on verbosity and readability """
    data = ""
    post_log = restrict_raw_diffs(post_log)
    for line in post_log:
        # Remove coloring codes
        line = re.sub('\\x1b\[.{1,2}m', '', line)
        # Format missing xpath lines
        if 'Nodes are not present in given Xpath' in line:
            line = line.replace('Nodes are not present in given Xpath:', 'No info found for the given criteria')
        # Check for reasons to not include the line in output and return True if it should be skipped
        skip_line = line_filter(line)
        if skip_line is False:
            line = line + '<br>\n'
            data = data + line
    data = html_output(data)
    return data

def restrict_raw_diffs(post_log):
    """ Find any failed raw diffs and perform a diff on the pre/post values """
    import difflib
    d = difflib.Differ()
    for i, line in enumerate(post_log):
        # Indicates a failed diff:
        if ' Pre node text' in line:
            output = []
            r = line.split('\'')
            pre = str(r[1])
            post = str(r[3])
            pre = pre.split('\\n')
            post = post.split('\\n')
            result = list(d.compare(pre, post))
            q =  "\n".join(result)
            # Check for diff lines (starting with + or -)
            for row in q.splitlines():
               if row[0] == '+' or row[0] == '-':
                  output.append("FAILED! " + str(row))
            # Remove the raw content from the post_log and replace with diff
            post_log.pop(i)
            for diff_line in output:
                post_log.insert(i, diff_line)
    return post_log


def line_filter(line):
    """ Filter lines with specific words """
    # If any of these strings are int the line, do not output that line
    blacklist = ['** Device', '--Performing ', 'Tests Included', 'No difference',
                 'jnpr.jsnapy', 'ID gone missing', 'ID list', 'Difference in pre ']
    skip_line = False
    if line == '':
        skip_line = True
    else:
        for key in blacklist:
            if key in line:
                skip_line = True
    return skip_line


def html_output(data):
    """ Format the results for HTML output """
    i = 0
    output = {}
    # Split the data into sections based on command
    # output is a dict - key = integer, values = list of output lines
    # key is incremented for each command ran in the snapshot
    for line in data.splitlines():
        if 'Final result of --diff without test operator' in line:
            if 'PASS' in line:
                line = 'PASS | No diff in pre/post check'
            else:
                line = 'FAIL | Diff found in pre/post check'
        if '*** Command:' in line or 'Final Result' in line or 'ERROR!!!' in line:
            i += 1
            output[i] = [line]
        else:
            if 'Connecting to device' not in line:
                output[i].append(line)
    # Determine if the command passed, failed, or skipped
    # Also reorder test result to the top
    for command in output:
        status = ''
        # pass / fail index used for reordering lines
        pass_index = 0
        fail_index = 0
        for i, line in enumerate(output[command]):
            if 'FAIL' in line or 'Test Failed' in line:
                # If FAIL, move to the top of the command section, under previous fail lines
                status = 'FAIL'
                reorder = output[command].pop(i)
                output[command].insert(1, reorder)
                fail_index += 1
            elif 'PASS ' in line:
                # PASS only if something else hasnt failed
                if status != 'FAIL':
                    status = 'PASS'
                # Not sure why the reorder is here ?
                reorder = output[command].pop(i)
                pass_index += 1
                output[command].insert(pass_index, reorder)
                pass_index = i
            elif 'SKIPPING' in line:
                # Only mark as skip if there are no pass/fails
                if status != 'FAIL' and status != 'PASS':
                    status = 'SKIP'
            elif 'Final Result' in line:
                status = 'FINAL'
                break

        # Create HTML div for pass/fail/skip
        output[command].insert(0, '<div class="' + status.lower() + '-main">')
        
        # Create a child div to hide individual passed/skipped tests
        if status == 'FAIL':
            # If something failed, keep them exposed above the child div
            output[command].insert(2 + fail_index, '<div class="' + status.lower() + '-child">')
        else:
            output[command].insert(2, '<div class="' + status.lower() + '-child">')
    
    # Add close div tags at the end of each command section
    for command in output:
        output[command].append('</div></div><br>')
    
    # Put all the output back together as result and pass it back to flask
    result = ""
    for command in output:
        for line in output[command]:
            result = result + line
    
    # Append javascript for the jquery div toggles
    result = result + '<script type="text/javascript" src="/jsnapy_flask/static/js/hide_divs.js"></script>'
    return result
