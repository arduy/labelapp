import csv
import re
import json
import os

class ItemReader:

    def __init__(self,settings):
        self.settings = settings
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
            except KeyError:
                print("Error: Input data does not have a correctly named quantity column")
                print('Input format: "{0}"'.format(self.settings['description']))
                print('Quantity column name: "{0}"'.format(self.settings['quantity_field']))
                return []
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

    def __init__(self,filename,meta_filename=None):
        self.filename = filename
        self.meta_filename = meta_filename

    def autosplit(self,items):
        try:
            with open(self.meta_filename) as meta_file:
                meta_data = json.load(meta_file)
                name = os.path.basename(self.filename)
                data = None
                for val in meta_data:
                    if val['name'].lower() == name.lower():
                        data = val
                        break
                if data is not None:
                    split_params = data.get('autosplit')
                else:
                    split_params = None
        except Exception as e:
            print('Error reading template metadata: {0}'.format(str(e)))
            return items
        if split_params is not None:
            new_items = []
            if split_params.get('mode') == 'simple':
                src_name = split_params['field']
                target_name = split_params['target']
                src_limit = split_params['limits'][src_name]
                target_limit = split_params['limits'][target_name]
                for item in items:
                    new_item = item.copy()
                    if len(new_item[src_name]) > src_limit:
                        source = new_item[src_name].split(' ')
                        new_target = ''
                        new_source = ''
                        length = 0
                        # make target as long as possible
                        # put rest in source
                        source.reverse()
                        for i, word in enumerate(source):
                            if i > 0:
                                word = word+' '
                            length += len(word)
                            if length <= target_limit:
                                new_target = word + new_target
                            else:
                                new_source = word + new_source
                        new_item[src_name] = new_source
                        new_item[target_name] = new_target
                    new_items.append(new_item)
                return new_items
            else:
                return items
        else:
            return items

    def fill(self,items):
        self.verify()
        field_limits = {}
        if self.meta_filename is not None:
            try:
                with open(self.meta_filename) as meta_file:
                    meta_data = json.load(meta_file)
                    name = os.path.basename(self.filename)
                    data = None
                    for val in meta_data:
                        if val['name'].lower() == name.lower():
                            data = val
                            break
                    if data is not None:
                        field_limits = data.get('field_limits', {})
            except Exception as e:
                print('Error reading template metadata: {0}'.format(str(e)))
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
                                if field_name in field_limits:
                                    field = truncate(field, field_limits[field_name])
                            except KeyError:
                                field = ''
                        line = line[:match.start(0)] + field + line[match.end(0):]
                        match = re.search(self.field_pattern,line)
                    if line == '\n' or line == '\r\n':
                        line = ''
                    output += line
                file.seek(0)
        return output

    # For now, check that template has at least one [%NEWITEM%] tag
    # Prevents infinite looping
    def verify(self):
        with open(self.filename) as file:
            for line in file.readlines():
                match = re.search(self.command_pattern, line)
                if match:
                    if match.group(1) == self.new_item_cmd:
                        return True
        raise TemplateError('Template is missing a [%NEWITEM%] command')

class TemplateError(Exception):
    pass

def remove_double_brackets(string):
    string = re.sub(r'\[\[','',string)
    string = re.sub(r'\]\]','',string)
    return string

def truncate(string, length):
    if isinstance(length, int):
        return string[:length]
