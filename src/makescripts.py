import os
import sys
import json

if __name__ == '__main__':
    mypath = os.path.dirname(sys.argv[0])
    main = os.path.join(mypath, 'main.exe')
    with open(os.path.join(mypath,'scripts.json'), 'r') as read_file:
        data = json.load(read_file)
        for params in data:
            scriptname = '{0}.bat'.format(params['name'])
            with open(scriptname, 'w') as file:
                file.write(
                    '@echo off\n{0} --format={1} --template={2} "%~1"'
                        .format(main, params['format'], params['template']))
