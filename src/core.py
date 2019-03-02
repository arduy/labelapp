import csv
import re

class ItemReader:

    def __init__(self,settings):
        self.quantity_field = settings['quantity_field']
        self.field_mappings = settings.get('field_mappings', dict())

    def read(self, csvfile):
        items = []
        dictreader = csv.DictReader(csvfile)
        for row in dictreader:
            quantity = 0
            try:
                quantity = int(row[self.quantity_field])
            except ValueError:
                pass
            for _ in range(quantity):
                new_item = row.copy()
                for key, value in self.field_mappings.items():
                    if key in row:
                        new_item[value] = row[key]
                items.append(new_item)
        return items

class Template:

    field_pattern = r'\[\[(\w+)\]\]'
    command_pattern = r'^\[%(\w+)%\]$'
    new_item_cmd = 'NEWITEM'

    def __init__(self,filename):
        self.filename = filename

    def fill(self,items):
        output = ''
        items = items[:] # copy to leave original unaltered
        items.reverse() # work backwards for O(1) pops
        with open(self.filename) as file:
            current_item = None
            while items:
                for line in file.readlines():
                    match = re.search(self.command_pattern,line)
                    if match:
                        if match.group(1) == self.new_item_cmd:
                            try:
                                current_item = items.pop()
                            except IndexError:
                                current_item = None
                            line = ''
                    match = re.search(self.field_pattern,line)
                    while match:
                        field_name = match.group(1)
                        if current_item is None:
                            field = ''
                        else:
                            try:
                                field = remove_double_brackets(current_item[field_name])
                            except KeyError:
                                field = ''
                        line = line[:match.start(0)] + field + line[match.end(0):]
                        match = re.search(self.field_pattern,line)
                    if line == '\n' or line == '\r\n':
                        line = ''
                    output += line
                file.seek(0)
        return output

def remove_double_brackets(string):
    string = re.sub(r'\[\[','',string)
    string = re.sub(r'\]\]','',string)
    return string
