import core
import os
import argparse

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

formats = {
    'lightspeed': lightspeed_settings
}


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('data')
    parser.add_argument('--format')
    parser.add_argument('--template')

    args = parser.parse_args()
    if args.format in formats:
        itemreader = core.ItemReader(formats[args.format])
    else:
        print('Select a file format')

    with open(args.data) as data:
        items = itemreader.read(data)
    template = core.Template(args.template)
    output = template.fill(items)
    with open('output.txt','w') as file:
        file.write(output)
    # os.system(r'RawPrint "\\OFFICEWWS5-PC\TEC B-SX4T" output.txt')
