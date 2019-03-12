import unittest
import csv
import re
import core

def reader_settings():
    return  {
        'quantity_field': 'Qty',
        'description': 'Test Settings',
    }

class BasicTests(unittest.TestCase):

    def test_reader(self):
        with open('testdata.csv') as csvfile:
            reader = csv.DictReader(csvfile)
            names = ['small plant','big plant','giant plant']
            prices = ['3.99','12.99','39.99']
            for i, row in enumerate(reader):
                self.assertEqual(names[i],row['Description'])
                self.assertEqual(prices[i],row['Price'])

    def test_read_template(self):
        field_regex = re.compile(r'\[\[\w+\]\]')
        cmd_regex = re.compile(r'\[%\w+%\]')
        field_matches = []
        cmd_matches = []
        with open('templates/testtemplate.txt') as template:
            for line in template.readlines():
                field_matches += field_regex.findall(line)
                cmd_matches += cmd_regex.findall(line)
            self.assertEqual(len(field_matches),4)
            self.assertEqual(len(cmd_matches),2)

    def test_item_reader(self):
        item_reader = core.ItemReader(reader_settings())
        with open('testdata.csv') as csvfile:
            items = item_reader.read(csvfile)
            self.assertEqual(len(items),9)
            self.assertEqual(items[8]['Description'],'giant plant')
            self.assertEqual(items[3]['Price'],'12.99')

    def test_field_mappings(self):
        settings = reader_settings()
        settings['field_mappings'] = {
            'Description': 'Mapped Description',
            'Price': 'Mapped Price',
            'Barcode': 'Mapped Barcode'
        }
        item_reader = core.ItemReader(settings)
        with open('testdata.csv') as csvfile:
            items = item_reader.read(csvfile)
            self.assertEqual(items[8]['Mapped Description'],'giant plant')
            self.assertEqual(items[3]['Mapped Price'],'12.99')
            self.assertEqual(items[0]['Mapped Barcode'],'12345678')

if __name__ == '__main__':
    unittest.main()
