import json
import os
import time
import glob

from FirstLayer import FirstLayer, finalJson
from ExtractKeywords import ExtractKeywords

from FeatureVector import queryURIs, queryURIsTuples, finalURIs, finalContext, FeatureVector
from SQLDatabase import SQLDatabase
from MyWord2Vec import MyWord2Vec
from OutputGenerator import OutputGenerator

start_time = time.time()

SQLDatabase.readPDFSIntoSQLTable()
myThing = MyWord2Vec()
MyWord2Vec.startTokenizingInputText(SQLDatabase.readPDFContentsIntoASingleString())

projectPath = os.path.abspath(os.path.dirname(__file__))
path = projectPath + "/files/*"
print(FeatureVector.removeDigitsFromString("pmu_avacon1 84854"))

for file in glob.glob(path):
    SQLDatabase.removeDuplicateRows()
    print('\n', file)
    filePath = file
    filePathOntology = projectPath + "/AllFiles/sargon.ttl"

    extractKeywords = ExtractKeywords(filePath)
    allKeywords = extractKeywords.getAllKeywords()[0]
    fileJsonObject = extractKeywords.getAllKeywords()[1]

    SQLDatabase.createKeywordsTable()
    SQLDatabase.createURIsParentsTable()

    firstLayer = FirstLayer(allKeywords, filePathOntology, fileJsonObject)

    outputGenerator = OutputGenerator(file, finalURIs)
    outputGenerator.writeTurtleFile('''{
    "pmu_avacon1": {
        "@type": "PMU",
        "@id": "avacon1",
            "has channel" : {
            "@id" : "ch1",
            "@type" : "relationship",
            "UL1m": {
                "@id" : "UL1m",
                "@type" : "http://webprotege.stanford.edu/Maqnititute",
                "@value" : "225.656173706055"}	
        },
        "timestamp" : {
            "@type" : "datetime",
            "@value": "2021-11-17T14:23:19.999921+00:00"
        }''')

    outputGenerator.writeJSONLDFileFromDict(firstLayer.buildFinalJson())
    outputGenerator.writeTurtleFile(str(json.dumps(finalJson, indent=4)))
    outputGenerator.writeOWLFile(str(json.dumps(finalJson, indent=4)))

    SQLDatabase.removeDuplicateRows()
    queryURIs.clear()
    queryURIsTuples.clear()
    finalURIs.clear()
    extractKeywords.keywords.clear()
    finalJson.clear()
    finalContext.clear()

print("Total runtime is : " + " %s seconds " % (time.time() - start_time))
