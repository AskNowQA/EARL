import json

relationship_file_01 = "earlbinaries/esdumps/dbontologyindex1.json"
relationship_file_02 = "earlbinaries/esdumps/dbpredicateindex14.json"
entity_file = "earlbinaries/esdumps/dbentityindex9.json"

f = open("relationships.txt","w")
for line in open(relationship_file_01,'r'):
    data = json.loads(line)
    f.write(data["_source"]["mergedLabel"]+"\n")
    f.write(data["_source"]["mergedLabel"].lower()+"\n")
    print(data["_source"]["mergedLabel"])
f.close()


f=open("relationships.txt", "a+")
for line in open(relationship_file_02,'r'):
    data = json.loads(line)
    f.write(data["_source"]["mergedLabel"]+"\n")
    f.write(data["_source"]["mergedLabel"].lower()+"\n")
    print(data["_source"]["mergedLabel"])
f.close()


f = open("entities.txt","w")
for line in open(entity_file,'r'):
    data = json.loads(line)
    if"dbpediaLabel" in data["_source"]:
        f.write(data["_source"]["dbpediaLabel"]+"\n")
        f.write(data["_source"]["dbpediaLabel"].lower()+"\n")
        print(data["_source"]["dbpediaLabel"])
    else:
        f.write(data["_source"]["wikidataLabel"]+"\n")
        f.write(data["_source"]["wikidataLabel"].lower()+"\n")
        print(data["_source"]["wikidataLabel"])
