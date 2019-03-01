import core
import os

if __name__ == '__main__':
    itemreader = core.ItemReader('Qty')
    with open('testdata.csv') as data:
        items = itemreader.read(data)
    template = core.Template('templates/3wide label template.txt')
    output = template.fill(items)
    with open('output.txt','w') as file:
        file.write(output)
    os.system(r'RawPrint "\\OFFICEWWS5-PC\TEC B-SX4T" output.txt')
