import json
import os
from sutime import SUTime

if __name__ == '__main__':
    test_case = u'I need a desk for tomorrow from 2pm to 3pm'

    jar_files = os.path.join(os.path.dirname(__file__), 'java/target')
    sutime = SUTime(jars=jar_files, mark_time_ranges=True)

    print(json.dumps(sutime.parse(test_case), sort_keys=True, indent=4))
