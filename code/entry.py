import psycopg2
import easygui
import json

dbname = 'postgres'
user = 'postgres'
host = 'localhost'

connectStatus = False

while(not connectStatus):
    dbnameInput = input("dbname <"+dbname+">: ")
    userInput = input("user <"+user+">: ")
    hostInput = input("host <"+host+">: ")
    password = input("password: ")

    if (dbnameInput!=''):
        dbname = dbnameInput
    if (userInput!=''):
        user = userInput
    if (hostInput!=''):
        host = hostInput

    try:
        conn = psycopg2.connect("dbname="+dbname+" user="+user+" host="+host+" password="+password)
        print("Successfully connect to database!")
        connectStatus = True
        conn.autocommit = True
    except:
        print("Fail to connect to the database, please try again!")

if (connectStatus):
    cur = conn.cursor()
    while(True):
        print("Select your sql file (sql contains no comment!): ")
        query_path = easygui.fileopenbox()
        file_name = query_path.split("\\")[-1].split(".")[0]
        query = open(query_path, "r", encoding="utf8").read()
        print("\nShow me the databases:\n")

        # command = query.split(' ')[0]
        # if (command in {'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'VALUES', 'EXECUTE', 'DECLARE'}):
        #     query_qep = 'EXPLAIN (FORMAT JSON) ' + query
        # elif (command == 'CREATE' and query.split(' ')[1] == 'TABLE'):
        #     query_qep = 'EXPLAIN (FORMAT JSON) ' + query
        # print(query_qep)

        query_array = query.split(';')
        qep_index = 0
        for query in query_array:
            if query and (not query.isspace()):
                # print(query)
                query = query.strip()
                query_qep = ''
                command = query.split(' ')[0]
                if command in {'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'VALUES', 'EXECUTE', 'DECLARE'}:
                    query_qep = 'EXPLAIN (FORMAT JSON) ' + query
                elif command == 'CREATE' and query.split(' ')[1] == 'TABLE':
                    query_qep = 'EXPLAIN (FORMAT JSON) ' + query
                if len(query_qep) > 0:
                    cur.execute(query_qep)
                    rows = cur.fetchall()
                    for row in rows:
                        qep_index += 1
                        with open('../data/json/' + file_name + '_' + str(qep_index) + '.json', 'wt') as out:
                            res = json.dump(row[0], out, sort_keys=True, indent=4, separators=(',', ': '))

                print('Main query exec...')
                cur.execute(query)
                print ('Row count: ' + str(cur.rowcount))
                if cur.rowcount <= 0:
                    print("")
                    continue
                rows = cur.fetchall()
                for row in rows:
                    for i in range(len(row)):
                        print ("   ", row[i], end='')
                    print("")
                print("")