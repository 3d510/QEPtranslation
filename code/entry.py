import psycopg2
import easygui
import json
import os
import re
import glob

from code.translate_qep import translate_qeptree_to_text

dbname = 'postgres'
user = 'postgres'
host = 'localhost'

connectStatus = False

while not connectStatus:
    print("*** Enter database credentials to access: ")
    dbnameInput = input("dbname <" + dbname + ">: ")
    userInput = input("user <" + user + ">: ")
    hostInput = input("host <" + host + ">: ")
    password = easygui.passwordbox("PASSWORD:")

    if dbnameInput != '':
        dbname = dbnameInput
    if userInput != '':
        user = userInput
    if hostInput != '':
        host = hostInput

    try:
        conn = psycopg2.connect("dbname=" + dbname + " user=" + user + " host=" + host + " password=" + password)
        print("Successfully connect to database!")
        connectStatus = True
        conn.autocommit = True
    except:
        print("Fail to connect to the database, please try again!")

if connectStatus:
    cur = conn.cursor()
    while True:
        print("\n*** Select your sql file (sql contains no comment!): ")
        query_path = easygui.fileopenbox(default=os.path.join('..', 'data', 'sql', "*"))
        file_name = query_path.split(os.path.sep)[-1].split(".")[0]
        print("Your sql file path: ", query_path)
        query = open(query_path, "r", encoding="utf8").read()

        # print("\nShow me the databases:\n")
        # command = query.split(' ')[0]
        # if command in ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'VALUES', 'EXECUTE', 'DECLARE']:
        #     query_qep = 'EXPLAIN (FORMAT JSON) ' + query
        # elif command == 'CREATE' and query.split(' ')[1] == 'TABLE':
        #     query_qep = 'EXPLAIN (FORMAT JSON) ' + query
        # print(query_qep)

        query_array = query.split(';')
        qep_index = 0
        for query in query_array:
            if not query or query.isspace():
                continue
            print("Query:", query)
            query = query.strip().lower()
            command = query.split(' ')[0]

            query_qep = None
            valid_command = re.compile(r"(select|insert|update|delete|values|execute|declare|create table \b.*\b as).*")
            if bool(re.match(valid_command, query)):
                query_qep = 'explain (format json) ' + query

            if query_qep is not None:
                rows = []
                try:
                    cur.execute(query_qep)
                    rows = cur.fetchall()
                except Exception as ex:
                    print("Invalid query, cannot explain")
                    print("Exception:", ex)

                for row in rows:
                    qep_index += 1
                    qep_json_path = os.path.join('..', 'data', 'json', file_name + '_' + str(qep_index) + ".json")
                    qep_text_path = os.path.join('..', 'data', 'txt', file_name + '_' + str(qep_index) + ".txt")
                    with open(qep_json_path, 'wt') as out:
                        res = json.dump(row[0], out, sort_keys=True, indent=2, separators=(',', ': '))
                    translate_qeptree_to_text(qep_json_path, qep_text_path)

            print('Executing query...')
            try:
                cur.execute(query)
                print('Row count: ' + str(cur.rowcount), " - Results:")
                if cur.rowcount <= 0:
                    print("")
                    continue
                rows = cur.fetchall()
                for row in rows:
                    for i in range(len(row)):
                        print("   ", row[i], end='')
                    print("\n")
            except Exception as ex:
                print("Invalid query, cannot execute")
                print("Exception:", ex)

        choice = input("Continue? (Y to select another sql file, N to quit session):\n")
        if choice == 'N':
            break

    cur.close()
