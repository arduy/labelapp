import core
import os
import argparse
import configparser
import win32print

# Lightspeed PO settings
lightspeed_settings = {
    'field_mappings': {
        'Item': 'Description',
        'Retail Price': 'Price',
        'System ID': 'Barcode'
    },
    'quantity_field': 'Order Qty.',
    'description': 'Lightspeed PO',
}

# default
# intended for a user made spreadsheet
default_settings = {
    'quantity_field': 'Qty',
    'description': 'Basic',
}

formats = {
    'lightspeed': lightspeed_settings,
    'default': default_settings,
}


def ask_yes_no(text):
    choice = input(text)
    if choice == 'y':
        return True
    else:
        return False


if __name__ == '__main__':

    mypath = os.path.dirname(os.path.realpath(__file__))

    parser = argparse.ArgumentParser()

    parser.add_argument('data')
    parser.add_argument('--format')
    parser.add_argument('--template')
    parser.add_argument('-np', '--noprint', action='store_true')

    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read(os.path.join(mypath,'config.ini'))

    if args.format in formats:
        itemreader = core.ItemReader(formats[args.format])
    else:
        itemreader = core.ItemReader(formats['default'])

    with open(args.data) as data:
        items = itemreader.read(data)
    if ask_yes_no('Would you like to print {0} labels? [y/n] '.format(len(items))):
        template = core.Template(args.template)
        output = template.fill(items)
        if args.noprint:
            with open(os.path.join(mypath, 'output.txt'), 'w') as file:
                file.write(output)
        else:
            data = bytes(output, 'utf-8')
            myPrinter = win32print.OpenPrinter(config['Settings']['printer'])
            try:
                myJob = win32print.StartDocPrinter(myPrinter, 1, ("Labels", None, "RAW"))
                try:
                    win32print.StartPagePrinter(myPrinter)
                    win32print.WritePrinter(myPrinter, data)
                    win32print.EndPagePrinter(myPrinter)
                finally:
                    win32print.EndDocPrinter(myPrinter)
            finally:
                win32print.ClosePrinter(myPrinter)
