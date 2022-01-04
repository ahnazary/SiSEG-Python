import glob
import sqlite3
import pdfplumber
import rdflib

from FeatureVector import queryURIs, queryURIsTuples, prefixes

conn = sqlite3.connect('URIs.sqlite')
cur = conn.cursor()


class SQLDatabase:
    @staticmethod
    def createKeywordsTable():
        cur.executescript('''
                
                   create table if not exists Keywords (
                        id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT unique,
                        keyword TEXT,
                        ontology TEXT,
                        layer TEXT,
                        URI TEXT,
                        CBOW REAL,
                        SkipGram REAL,
                        UNIQUE (keyword, ontology, URI)
                    );
                    ''')
        conn.commit()

    @staticmethod
    def createURIsParentsTable():
        cur.executescript('''
               create table if not exists URIsParents (
                    id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT unique,
                    URI   TEXT unique,
                    isClass TEXT,
                    parents TEXT,
                    UNIQUE (URI, isClass, parents)
                );
                ''')
        conn.commit()

    @staticmethod
    def addToKeywords(keyword, ontology, layer, URI, cbow, skipgram):
        cur.execute('''INSERT OR IGNORE INTO Keywords (keyword, ontology, layer, URI, CBOW, SkipGram)
                    VALUES ( ?, ?, ?, ?, ?, ? )''', (keyword, ontology, layer, URI, cbow, skipgram))

        conn.commit()

    @staticmethod
    def addToURIsParents(URI, isClass, parents):
        cur.execute('''INSERT OR IGNORE INTO URIsParents (URI, isClass, parents) 
                VALUES ( ?, ?, ? )''', (URI, isClass, parents))
        conn.commit()

    @staticmethod
    def removeDuplicateRows():
        try:
            cur.executescript('''
            DELETE FROM Keywords
            WHERE id NOT IN
            (
                SELECT MIN(id)
                FROM Keywords
                GROUP BY keyword, ontology, layer, URI
            )
            ''')
            conn.commit()
            cur.executescript('''
                    DELETE FROM URIsParents
                    WHERE id NOT IN
                    (
                        SELECT MIN(id)
                        FROM URIsParents
                        GROUP BY URI, isClass, parents
                    )
                    ''')
            conn.commit()
        except:
            print("Error in deleting duplicate rows!! ")

    @staticmethod
    def queryKeywordFromSQL(word, ontology, layer):
        flag = True
        sqlstr = 'SELECT keyword, ontology, layer, URI, CBOW, SkipGram FROM Keywords'
        for row in cur.execute(sqlstr):
            if word == row[0] and ontology == row[1] and layer == row[2]:
                if row[3] is not None:
                    queryURIs.append(row[3])
                    queryURIsTuples[row[3]] = (row[4], row[5])
                else:
                    # print("keyword exists in database but has no URIs assigned to it", row[3])
                    return True
                flag = False
        if flag:
            print("Keyword does not exist in the database")
            return False
        if not flag:
            return True

    @staticmethod
    def keywordExists(word, ontlogy, layer):
        sqlstr = 'SELECT keyword, ontology, layer FROM Keywords'
        for row in cur.execute(sqlstr):
            if word == row[0] and row[1] == ontlogy and row[2] == layer:
                return True
        return False

    @staticmethod
    def readPDFSIntoSQLTable():
        cur.executescript('''
                           create table if not exists PDFTexts (
                                id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT unique,   
                                PDF TEXT,
                                PageNumber TEXT,
                                Content TEXT  
                            );
                            ''')
        conn.commit()

        PDFslist = []
        sqlstr = 'SELECT PDF FROM PDFTexts'
        for row in cur.execute(sqlstr):
            PDFslist.append(row[0])

        def addPDFTextToSQLTable(pdfName, pageNum, content):
            cur.execute('''INSERT OR IGNORE INTO PDFTexts (PDF, PageNumber, Content) 
                            VALUES ( ?, ?, ? )''', (pdfName, pageNum, content))
            conn.commit()

        for file in glob.glob("/home/amirhossein/Documents/GitHub/Semantic-Annotation/files/*.pdf"):
            if file in PDFslist:
                continue
            print("Reading ", file)
            pageNum = 0
            with pdfplumber.open(file) as pdf:
                for page in pdf.pages:
                    pageNum = pageNum + 1
                    print("extracting page", pageNum)
                    addPDFTextToSQLTable(file, pageNum, page.extract_text(x_tolerance=0.15, y_tolerance=1).lower())

    @staticmethod
    def readPDFContentsIntoASingleString():
        # PDF contents will be stored in this string
        result = ""
        sqlstr = 'SELECT content FROM PDFTexts'
        for row in cur.execute(sqlstr):
            result += row[0]
        f = open("/home/amirhossein/Documents/GitHub/Semantic-Annotation/files/text.txt", 'r')
        result += f.read()
        return result