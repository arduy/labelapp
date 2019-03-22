import core
import sys
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
    'description': 'Default',
}

formats = {
    'lightspeed': lightspeed_settings,
    'default': default_settings,
}


def ask_yes_no(text):
    choice = input(text)
    if choice.lower() in ['y', 'yes', 'y ']:
        return True
    else:
        print('Print job cancelled')
        return False

def verify_barcodes(items):
    for item in items:
        barcode = item.get('Barcode','')
        if not barcode.isdigit():
            desc = item.get('Description','<no description>')
            choice = input('Warning: Barcode irregularity detected for item "{0}"\nBarcode: "{1}"\nWould you like to continue anyway? [y/n]'.format(desc, barcode))
            if not choice.lower() in ['y', 'yes', 'y ']:
                return False
    return True


if __name__ == '__main__':

    mypath = os.path.dirname(sys.argv[0])

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

    template_file = os.path.join(mypath, config['Settings']['TemplateFolder'], args.template)
    if not os.path.isfile(template_file):
        print('Template {0} not found'.format(args.template))
        sys.exit()

    metadata_file = os.path.join(mypath, config['Settings']['Templatefolder'], 'meta.json')
    if not os.path.isfile(metadata_file):
        print('Warning:  Template metadata not found.  Proceeding without.')
        metadata_file = None

    with open(args.data, encoding='utf-8') as data:
        items = itemreader.read(data)

    if not verify_barcodes(items):
        print('Aborting')
        sys.exit()

    if ask_yes_no('Would you like to print {0} labels? [y/n] '.format(len(items))):
        template = core.Template(template_file, metadata_file)
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
