# removes \r, \n and redundant spaces
def normalize(string):
    return str(string).replace('\r', '').replace('\n', ' ').replace('\t', ' ').replace('  ', ' ').strip()