import unittest
import csv
import re
import core

def basic_reader_settings():
    mappings = {
        'SKU': 'Barcode',
    }
    return {
        'quantity_field': 'Qty',
        'description': 'Test Settings',
        'field_mappings': mappings
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
        regex = re.compile(r'\[\[\w+\]\]')
        regex2 = re.compile(r'\[%\w+%\]')
        matches = []
        matches2 = []
        with open('templates/3acrossCode93.txt') as template:
            for line in template.readlines():
                matches += regex.findall(line)
                matches2 += regex2.findall(line)
            self.assertEqual(len(matches),12)
            self.assertEqual(len(matches2),3)

    def test_item_reader(self):
        item_reader = core.ItemReader(basic_reader_settings())
        with open('testdata.csv') as csvfile:
            items = item_reader.read(csvfile)
            self.assertEqual(len(items),9)
            self.assertEqual(items[8]['Description'],'giant plant')
            self.assertEqual(items[3]['Price'],'12.99')

    def test_field_mappings(self):
        settings = basic_reader_settings()
        settings['field_mappings'] = {
            'Description': 'Mapped Description',
            'Price': 'Mapped Price',
            'SKU': 'Barcode'
        }
        item_reader = core.ItemReader(settings)
        with open('testdata.csv') as csvfile:
            items = item_reader.read(csvfile)
            self.assertEqual(items[8]['Mapped Description'],'giant plant')
            self.assertEqual(items[3]['Mapped Price'],'12.99')
            self.assertEqual(items[0]['Barcode'],'12345678')

if __name__ == '__main__':
    unittest.main()
