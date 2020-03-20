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
        with open('test/testdata.csv') as csvfile:
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
        with open('test/testtemplate') as template:
            for line in template.readlines():
                field_matches += field_regex.findall(line)
                cmd_matches += cmd_regex.findall(line)
            self.assertEqual(len(field_matches),1)
            self.assertEqual(len(cmd_matches),1)

    def test_item_reader(self):
        item_reader = core.ItemReader(reader_settings())
        with open('test/testdata.csv') as csvfile:
            items = item_reader.read(csvfile)
            self.assertEqual(len(items),9)
            self.assertEqual(items[8]['Description'],'giant plant')
            self.assertEqual(items[3]['Price'],'12.99')

    def test_quantity_error(self):
        item_reader = core.ItemReader(reader_settings())
        with open('test/noquantity.csv') as csvfile:
            with self.assertRaises(core.QuantityError) as cm:
                item_reader.read(csvfile)
            self.assertEqual(cm.exception.quantity_field, item_reader.quantity_field)

    def test_field_mappings(self):
        settings = reader_settings()
        settings['field_mappings'] = {
            'Description': 'Mapped Description',
            'Price': 'Mapped Price',
            'Barcode': 'Mapped Barcode'
        }
        item_reader = core.ItemReader(settings)
        with open('test/testdata.csv') as csvfile:
            items = item_reader.read(csvfile)
            self.assertEqual(items[8]['Mapped Description'],'giant plant')
            self.assertEqual(items[3]['Mapped Price'],'12.99')
            self.assertEqual(items[0]['Mapped Barcode'],'12345678')

    def test_meta_limits(self):
        settings = reader_settings()
        item_reader = core.ItemReader(settings)
        with open('test/testdata.csv') as csvfile:
            items = item_reader.read(csvfile)
            template = core.Template('test/testtemplate','test/testmeta.json')
            output = template.fill(items)
            for line in output.splitlines():
                self.assertEqual(len(line), 4) # field length limit in testmeta.json
            self.assertEqual(len(output.splitlines()), 9)

    def test_no_meta(self):
        settings = reader_settings()
        item_reader = core.ItemReader(settings)
        with open('test/testdata.csv') as csvfile:
            items = item_reader.read(csvfile)
            template = core.Template('test/testtemplate2','test/testmeta.json')
            output = template.fill(items)
            for line in output.splitlines():
                self.assertTrue(line in ['small plant', 'giant plant', 'big plant'])
            self.assertEqual(len(output.splitlines()), 9)

    def test_meta_error(self):
        settings = reader_settings()
        item_reader = core.ItemReader(settings)
        with open('test/testdata.csv') as csvfile:
            items = item_reader.read(csvfile)
            template = core.Template('test/testtemplate2','test/badmeta.json')
            with self.assertRaises(core.MetadataError):
                output = template.fill(items)


if __name__ == '__main__':
    unittest.main()
