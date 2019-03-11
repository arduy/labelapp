import core
import os
import argparse
import configparser

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


if __name__ == '__main__':

    config = configparser.ConfigParser()
    config.read('config.ini')

    parser = argparse.ArgumentParser()

    parser.add_argument('data')
    parser.add_argument('--format')
    parser.add_argument('--template')
    parser.add_argument('-np', '--noprint', action='store_true')

    args = parser.parse_args()
    if args.format in formats:
        itemreader = core.ItemReader(formats[args.format])
    else:
        itemreader = core.ItemReader(formats['default'])
        print('Using default file format')

    with open(args.data) as data:
        items = itemreader.read(data)
    template = core.Template(args.template)
    output = template.fill(items)
    with open('output.txt','w') as file:
        file.write(output)
    if not args.noprint:
        os.system('RawPrint "{0}" output.txt'.format(config['Settings']['printer']))
