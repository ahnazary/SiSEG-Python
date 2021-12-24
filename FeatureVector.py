import rdflib

prefixes = """PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
PREFIX om: <http://www.wurvoc.org/vocabularies/om-1.8/> 
PREFIX owl: <http://www.w3.org/2002/07/owl#> 
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
PREFIX foaf: <http://xmlns.com/foaf/0.1/> 
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> 
PREFIX time: <http://www.w3.org/2006/time#> 
PREFIX saref: <https://w3id.org/saref#>  
PREFIX saref: <https://saref.etsi.org/core/>  
PREFIX schema: <http://schema.org/>  
PREFIX dcterms: <http://purl.org/dc/terms/>  
PREFIX base: <http://def.isotc211.org/iso19150-2/2012/base#> 
PREFIX oboe-core: <http://ecoinformatics.org/oboe/oboe.1.0/oboe-core.owl#> 
PREFIX sosa: <http://www.w3.org/ns/sosa/> 
PREFIX sosa-om: <http://www.w3.org/ns/sosa/om#> 
PREFIX dc: <http://purl.org/dc/elements/1.1/> 
PREFIX dct: <http://purl.org/dc/terms/> 
PREFIX iso19156-gfi: <http://def.isotc211.org/iso19156/2011/GeneralFeatureInstance#> 
PREFIX iso19156-om: <http://def.isotc211.org/iso19156/2011/Observation#> 
PREFIX iso19156-sf: <http://def.isotc211.org/iso19156/2011/SamplingFeature#> 
PREFIX iso19156-sfs: <http://def.isotc211.org/iso19156/2011/SpatialSamplingFeature#> 
PREFIX iso19156-sp: <http://def.isotc211.org/iso19156/2011/Specimen#> 
PREFIX iso19156_gfi: <http://def.isotc211.org/iso19156/2011/GeneralFeatureInstance#> 
PREFIX iso19156_sf: <http://def.isotc211.org/iso19156/2011/SamplingFeature#> 
PREFIX xml: <http://www.w3.org/XML/1998/namespace> 
PREFIX skos: <http://www.w3.org/2004/02/skos/core#> 
PREFIX terms: <http://purl.org/dc/terms/> 
PREFIX vann: <http://purl.org/vocab/vann/> 
PREFIX webprotege: <http://webprotege.stanford.edu/> 
PREFIX : <https://w3id.org/saref#> \n"""
bannedStrings = ["type",
                 "unit",
                 "measure",
                 "relation",
                 "value",
                 "relationship",
                 "property",
                 "the",
                 "has",
                 "and",
                 "add",
                 "one"]
bannedURIs = ["https://w3id.org/saref",
              "http://www.w3.org/ns/sosa/om"]
ontologyStr = ""

# all URIs
queryURIs = []

# URIs with tuples as values to save their features (second feature is popularity and third one shows if its from
# first layer or second layer)
queryURIsTuples = dict()

URIs = dict()


class FeatureVector:

    def __init__(self, keywords, ontology):
        self.keywords = keywords
        self.ontology = ontology
        self.ontology = rdflib.Graph()
        self.ontology.parse(ontology)

    # just for testing
    def test(self):

        queryStrExact = prefixes + """SELECT ?subject
                        WHERE{
                        {?subject rdfs:label ?object}
                        FILTER (regex(?object, \"""" + "fLOor" + "\", \"i\" ))}"
        queryResult = self.ontology.query(queryStrExact)
        for row in queryResult:
            print(f"{row.subject}", "kkkkkkkkkkkkkkkkkk")

    # def generateFeatureVectors(self):

    # generatesd popularity features
    def setPopularityFeatures(self):
        factor = len(queryURIs) / queryURIs.count(self.most_frequent(queryURIs))
        for item in queryURIsTuples:
            tempTuple = (
                factor * queryURIs.count(item) / len(queryURIs), queryURIsTuples[item][0], queryURIsTuples[item][1])
            queryURIsTuples[item] = tempTuple

    # returns a list of parents of a node in the ontology
    def getClassNode(self, nodeName):
        result = list()
        queryString = prefixes + """SELECT ?subject
           WHERE{
           {?subject rdfs:subClassOf <""" + nodeName + ">}FILTER (!isBlank(?subject))}"

        queryStringBlankNode = prefixes + """SELECT ?subject
           WHERE{
           {?subject rdfs:subClassOf [?b <""" + nodeName + ">]}}"

        queryResult = self.ontology.query(queryString)
        queryResultBlankNode = self.ontology.query(queryStringBlankNode)

        for row in queryResult:
            # print(f"{row.subject}")
            result.append(f"{row.subject}")

        for row in queryResultBlankNode:
            # print(f"{row.subject}")
            result.append(f"{row.subject}")
        return result

    # returns true if node is of type owl:class
    def isClassNode(self, nodeName):
        queryString = prefixes + """SELECT ?object
           WHERE{
           {<""" + nodeName + "> rdf:type ?object}}"

        queryResult = self.ontology.query(queryString)
        for row in queryResult:

            # this filter works for ontologies that include owl:class
            if "owl" in f"{row.object}".lower() and "class" in f"{row.object}".lower():
                return True
            else:
                return False

    # this method creates a string from a list so it can be stored in a SQL table
    @staticmethod
    def getStringOfList(inputList):
        result = ""
        temp = 0
        for i in inputList:
            if temp == 0:
                result = result + str(i) + ","
            elif temp == len(inputList) - 1:
                result = result + " " + str(i)
            else:
                result = result + " " + str(i) + ","
            temp = temp + 1
        return result

    @staticmethod
    def most_frequent(List):
        counter = 0
        num = List[0]

        for i in List:
            curr_frequency = List.count(i)
            if curr_frequency > counter:
                counter = curr_frequency
                num = i

        return num

    def isNumber(self, inputString):
        try:
            float(inputString)
            return True
        except:
            return False

    def isBoolean(self, inputString):
        if inputString.lower() == "true" or inputString.lower() == "false":
            return True
        else:
            return False

    @staticmethod
    def getQueryURIs():
        return queryURIs

    @staticmethod
    def getPrefixes():
        return prefixes

    @staticmethod
    def getBannedStrings():
        return bannedStrings

    @staticmethod
    def getURIs():
        return URIs

    @staticmethod
    def getqueryURIsTuples():
        return queryURIsTuples
