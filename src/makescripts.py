import os
import sys

if __name__ == '__main__':
    mypath = os.path.dirname(sys.executable)
    main = os.path.join(mypath, 'main.exe')
    if os.path.isfile(main):
        with open('Lightspeed PO.bat', 'w') as file:
            file.write('@echo off\n{0} --format=lightspeed --template=standard "%~1"'.format(main))
        with open('Large Text No Barcode.bat', 'w') as file:
            file.write('@echo off\n{0} --format=default --template=nobarcode "%~1"'.format(main))
    else:
        print('main.exe not found')
