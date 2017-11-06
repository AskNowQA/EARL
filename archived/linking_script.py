import re
import difflib
import json

import pandas as pd


def make_mini_dict(uri, entity, start, end):
    d = {}
    d['uri'] = uri
    d['label'] = entity
    d['seq'] = str(start) + ',' + str(end)
    return d


df = pd.read_json('../data_v7.json')
rows, cols = df.shape
final_list = []

for i in range(rows):
    id_no = df.loc[i][0]
    ques = df.loc[i][1]
    sparql_query = df.loc[i][2]
    sparql_id = df.loc[i][3]
    predicate_mapping = []
    entity_mapping = []
    checked = 'false'
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
            d = make_mini_dict(uri, build, start, end)
            entity_mapping.append(d)
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
            d = make_mini_dict(uri, build, start, end)
            predicate_mapping.append(d)

    final_dict = {}
    final_dict["id"] = id_no
    final_dict["question"] = ques
    final_dict["sparql_query"] = sparql_query
    final_dict["sparql_id"] = str(sparql_id)
    final_dict["checked"] = checked
    final_dict["predicate mapping"] = predicate_mapping
    final_dict["entity mapping"] = entity_mapping
    try:
        final_list.append(json.dumps(final_dict))
    except TypeError:
        print(type(final_dict['sparql_id']))
        break


file = open('linked.json', 'w')
for item in final_list:
    file.write('%s,\n' % item)
