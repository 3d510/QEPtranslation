import psycopg2
import easygui
import json
import os
import re

from colorama import Fore, Back, Style

from translate_qep import translate_qeptree_to_text
from voice import playAudio

dbname = 'postgres'
user = 'postgres'
host = 'localhost'

for folder in ['json', 'mp3', 'sql', 'txt']:
    folder_path = os.path.join('..', 'data', folder)
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)

connectStatus = False

while not connectStatus:
    print(Fore.CYAN + "*** Enter database credentials to access: " + Style.RESET_ALL)
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
        print(Fore.RED + "Fail to connect to the database, please try again!")

if connectStatus:
    cur = conn.cursor()
    while True:
        print(Fore.CYAN + "\n*** Select your sql file (sql contains no comment!): " + Style.RESET_ALL)
        query_path = easygui.fileopenbox(default=os.path.join('..', 'data', 'sql', "*"))
        file_name = query_path.split(os.path.sep)[-1].split(".")[0]
        print(Fore.YELLOW + "Your sql file path: " + Style.RESET_ALL + query_path)
        query = open(query_path, "r", encoding="utf8").read()

        query_array = query.split(';')
        qep_index = 0
        for query in query_array:
            if not query or query.isspace():
                continue
            print(Fore.YELLOW + "Query: " + Style.RESET_ALL + query)
            query = query.strip().lower()
            command = query.split(' ')[0]

            query_qep = None
            valid_command = re.compile(r"(select|insert|update|delete|values|execute|declare|create table \b.*\b as).*")
            if bool(re.match(valid_command, query)):
                query_qep = 'explain (format json) ' + query

            if query_qep is not None:
                print(Fore.YELLOW + "Playing voice (this might take a while) at ", end='' + Style.RESET_ALL)
                rows = []
                try:
                    cur.execute(query_qep)
                    rows = cur.fetchall()
                except Exception as ex:
                    print(Fore.RED + "Invalid query, cannot explain"  + Style.RESET_ALL)
                    print("Exception:", ex)

                for row in rows:
                    qep_index += 1
                    qep_json_path = os.path.join('..', 'data', 'json', file_name + '_' + str(qep_index) + ".json")
                    qep_text_path = os.path.join('..', 'data', 'txt', file_name + '_' + str(qep_index) + ".txt")
                    with open(qep_json_path, 'wt') as out:
                        res = json.dump(row[0], out, sort_keys=True, indent=2, separators=(',', ': '))
                    translate_qeptree_to_text(qep_json_path, qep_text_path)
                    playAudio(qep_text_path)

            print(Fore.YELLOW + 'Executing query (this might take a while)...' + Style.RESET_ALL)
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
                print(Fore.RED + "Invalid query, cannot execute" + Style.RESET_ALL)
                print("Exception:", ex)

        choice = input(Fore.CYAN + "Continue? (Y to select another sql file, N to quit session):\n" + Style.RESET_ALL)
        if choice == 'N':
            break
            
conn.close()

