from neo4j import GraphDatabase
import pyautogui


class Neo4jConnection:

    def __init__(self, uri, user, pwd):
        self.__uri = uri
        self.__user = user
        self.__pwd = pwd
        self.__driver = None
        try:
            self.__driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__pwd))
        except Exception as e:
            print("Failed to create the driver:", e)

    def close(self):
        if self.__driver is not None:
            self.__driver.close()

    def query(self, query, db=None):
        assert self.__driver is not None, "Driver not initialized!"
        session = None
        response = None
        try:
            session = self.__driver.session(database=db) if db is not None else self.__driver.session()
            response = list(session.run(query))
        except Exception as e:
            print("Query failed:", e)
        finally:
            if session is not None:
                session.close()
        return response
    def queryNoList(self, query, db=None):
        assert self.__driver is not None, "Driver not initialized!"
        session = None
        response = None
        try:
            session = self.__driver.session(database=db) if db is not None else self.__driver.session()
            response = session.run(query)
        except Exception as e:
            print("Query failed:", e)
        finally:
            if session is not None:
                session.close()
        return response


conn = Neo4jConnection(uri="bolt://localhost:7687", user="test", pwd="123")
conn.query("CREATE OR REPLACE DATABASE maglev")

query_string = '''
    CREATE(IsaacA:Person{name:'Isaac Asimov',born:1920})
    CREATE(HGWells:Person{name:'Herbert George Wells',born:1866})
    CREATE(JWCampbell:Person{name:'John Wood Campbell Jr.',born:1910})
    CREATE(ArturasV:Person{name:'Arturas Vellemaa',born:2000})
    CREATE(FrankH:Person{name:'Franklin Patrick Herbert Jr.',born:1920})

    CREATE(IRobot:Novel{title:'I, Robot',published:1950})
    CREATE(TimeMachine:Novel{title:'The Time Machine',published:1895})
    CREATE(DocMoreau:Novel{title:'The Island of Doctor Moreau',published:1896})
    CREATE(MightiestMachine:Novel{title:'The Mightiest Machine',published:1947})
    CREATE(Dune:Novel{title:'Dune',published:1965})


    CREATE(SciFi:Genre{title:'Science Fiction'})

    CREATE
        (IRobot)-[:GENRE]->(SciFi),
        (IsaacA)-[:AUTHOR]->(IRobot)
    CREATE
        (TimeMachine)-[:GENRE]->(SciFi),
        (DocMoreau)-[:GENRE]->(SciFi),
        (HGWells)-[:AUTHOR]->(DocMoreau),
        (HGWells)-[:AUTHOR]->(TimeMachine),
        (HGWells)-[:INSPIRED]->(IsaacA),
        (HGWells)-[:INSPIRED]->(FrankH)
    CREATE
        (MightiestMachine)-[:GENRE]->(SciFi),
        (JWCampbell)-[:AUTHOR]->(MightiestMachine),
        (JWCampbell)-[:INSPIRED]->(IsaacA)
    CREATE
        (Dune)-[:GENRE]->(SciFi),
        (FrankH)-[:AUTHOR]->(Dune)
    CREATE
        (ArturasV)-[:READ]->(IRobot),
        (ArturasV)-[:READ]->(TimeMachine),
        (ArturasV)-[:READ]->(DocMoreau)
'''
results = conn.query(query_string, db='authors')


def queryAndPrint(query):
    results = conn.query(query, db='authors')
    for i in range(len(results)):
        print(results[i])

query_string_all_nodes = '''
    MATCH(n)
    RETURN n
'''
while True:
    print("1.Show all nodes")
    print("2.Find authors by year of birth")
    print("3. Find all works of a specific author")
    print("4. Return the authors who inspired a specific novel")
    print("5. Find connection between any two people in the database")
    print("6. Find degrees of separation between any two people in the database")
    value = input("Choose: ")
    if value == "1":
        queryAndPrint(query_string_all_nodes)
    elif value == "2":
        valueS = input("Input year of birth: ")
        query_string = '''
            MATCH (n:Person)
            WHERE n.born={year}
            RETURN n.name
        '''.format(year=valueS)
        queryAndPrint(query_string)
    elif value == "3":
        valueS = input("Input author name: ")
        query_string = '''
            MATCH (:Person{{ name: {0} }})-->(novel)
            RETURN novel.title
        '''.format(repr(valueS))
        queryAndPrint(query_string)
    elif value == "4":
        valueS = input("Input the name of the novel: ")
        query_string = '''
            MATCH(:Novel{{ title:{0} }})<-[:AUTHOR]-(author)<-[:INSPIRED]-(inspiration)
            RETURN inspiration.name
        '''.format(repr(valueS))
        queryAndPrint(query_string)
    elif value == "5":
        print("All people in the database:")
        query_string = '''MATCH (person:Person) RETURN person.name'''
        results = conn.query(query_string, db='authors')
        for i in range(len(results)):
            print(results[i])
        valueS = input("Choose the first person: ")
        valueT = input("Choose the second person: ")
        query_string = '''
        MATCH p=shortestPath((:Person {{name:{0}}})-[*]-(:Person{{name:{1}}})) RETURN nodes(p)
        '''.format(repr(valueS), repr(valueT))
        result=conn.query(query_string,db='authors')
        print(result[0])
    elif value == "6":
        print("All people in the database:")
        query_string = '''MATCH (person:Person) RETURN person.name'''
        results = conn.query(query_string, db='authors')
        for i in range(len(results)):
            print(results[i])
        valueS = input("Choose the first person: ")
        valueT = input("Choose the second person: ")
        query_string = '''
                MATCH p=shortestPath((:Person {{name:{0}}})-[*]-(:Person{{name:{1}}})) RETURN length(p)
                '''.format(repr(valueS), repr(valueT))
        result = conn.query(query_string, db='authors')
        print(result[0])
        # queryAndPrint(query_string)
# for i in range(len(results)):
#    print(results[i])
