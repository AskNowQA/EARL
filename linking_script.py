import re
import difflib

import pandas as pd


df = pd.read_json('../data_v7.json')
rows, cols = df.shape

final_list = []
for i in range(rows):
    id_no = df.loc[i][0]
    uris = re.findall(r'http://dbpedia.org/[^>]*', df.loc[i][2])

    l = re.findall(r'\S+[^?]', df.loc[i][1])
    l = [x.strip().lower() for x in l]

    for uri in uris:
        s = uri.split('/')
        label, entity = s[-2], s[-1]
        if label == 'resource':
            entity = re.sub('_', ' ', entity).lower()
            start = 1000
            build = ''
            for match in difflib.get_close_matches(entity, l, 5, 0):
                if match in entity:
                    if match in build:
                        continue
                    build += ' ' + match
                    temp = df.loc[i][1].lower().find(match)
                    if temp < start:
                        start = temp
                else:
                    break
            build = build.strip()
            length = len(build)
            end = start + length - 1
            final_list.append([id_no, uri, start, end])
        else:
            entity = entity.lower()
            matches = difflib.get_close_matches(entity, l, 5, 0)
            build = matches[0]
            start = df.loc[i][1].lower().find(build)
            if build in entity:
                for match in matches[1:]:
                    if match in entity and match not in build:
                        build += ' ' + match
                        temp = df.loc[i][1].lower().find(match)
                        if temp < start: start = temp
                    else:
                        break
            length = len(build)
            end = start + length - 1
            final_list.append([id_no, uri, start, end])

df_final = pd.DataFrame(data=final_list, columns=['id', 'uri', 'start', 'end'])
df_final.to_csv('linked.csv', index=False)
