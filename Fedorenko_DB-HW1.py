import sqlite3, re


def main_menu():
    action_type = input('You are in Main Menu.\n'
                        'There are the following options:\n'
                        '1. See a document history\n'
                        '2. See a worker activity\n'
                        '3. Register a worker\n'
                        '4. Make an operation with a document (to create, edit, etc.)\n'
                        '5. Register someone\'s right (to read, edit, etc. a document)\n'
                        'Enter the number of the desired option: ')
    if action_type == '1':
        doc_history(input('Please, enter the document name: '))
    if action_type == '2':
        worker_history(input('Please, enter the person full name: '))
    if action_type == '3':
        create_worker()
    if action_type == '4':
        doc_operation(action_choice())
    if action_type == '5':
        give_right()

def action_choice():
    action_num = input('We have the following options with documents:\n'
          '1. Creation\n'
          '2. Editing\n'
          '3. Submition\n'
          '4. Approving\n'
          '5. Ejection\n'
          'Please, enter the number of the desired action: ')
    if action_num == '1':
        return('creation')
    if action_num == '2':
        return('editing')
    if action_num == '3':
        return('submition')
    if action_num == '4':
        return('approval')
    if action_num == '5':
        return('ejection')


def worker_history(name):
    con = sqlite3.connect("Fedorenko_DB.db")
    cur = con.cursor()
    person_id = detect_person(name)
    history_select = cur.execute("SELECT operations.o_date, operations.o_time, operations.operation, documents.doc_name, operations.comment "
                          "FROM operations, documents "
                          "WHERE operations.person_id = ?", (person_id,))
    history = history_select.fetchall()
    for action in history:
        to_print = [action[0], ' ', action[1], ': ', action[2], ' of the document \"', action[3], '\"']
        if action[4] != '':
            to_print.append('; comment: ')
            to_print.append(action[4])
        print(''.join(to_print))
    con.commit()

def doc_history(name):
    con = sqlite3.connect("Fedorenko_DB.db")
    cur = con.cursor()
    doc_id = detect_person(name)
    history_select = cur.execute("SELECT operations.o_date, operations.o_time, operations.operation, staff.p_name, operations.comment "
                          "FROM operations, staff "
                          "WHERE operations.doc_id = ?", (doc_id,))
    history = history_select.fetchall()
    for action in history:
        to_print = [action[0], ' ', action[1], ': ', action[2], ' by ', action[3]]
        if action[4] != '':
            to_print.append('; comment: ')
            to_print.append(action[4])
        print(''.join(to_print))
    con.commit()

def create_worker():
    print('You are creating a note about a worker. Please, fill the following info.')
    p_name = input('Enter the worker\'s full name: ')
    birthdate = input('Enter the worker\'s birthdate (YYYY.MM.DD): ')
    birthplace = input('Enter the worker\'s birthplace: ')
    p_position = input('Enter the worker\'s position (writer or expert): ')
    con = sqlite3.connect("Fedorenko_DB.db")
    cur = con.cursor()
    write = cur.execute("INSERT INTO staff (p_name, birthdate, birthplace, p_position) VALUES (?, ?, ?, ?)", (p_name, birthdate, birthplace, p_position))
    con.commit()

def doc_operation(action):
    print('Please, fill the following info.')
    doc_name = input('The document name: ')
    author = input('The author\'s name: ')
    comment = input('If you like, write a comment: ')
    con = sqlite3.connect("Fedorenko_DB.db")
    cur = con.cursor()
    write_doc = cur.execute("INSERT INTO documents (doc_name) "
                        "VALUES (?)", (doc_name,))
    id_selection = cur.execute("SELECT doc_id "
                        "FROM documents "
                        "WHERE doc_name = ?", (doc_name,))
    doc_id = id_selection.fetchone()
    write_operation = cur.execute("INSERT INTO operations (doc_id, person_id, comment, o_date, o_time, operation) "
                                  "VALUES (?, ?, ?, CURRENT_DATE, CURRENT_TIME, ?)", (doc_id[0], detect_person(author), comment, action))
    con.commit()

def give_right():
    action_num = input('Which options are being given to the person?:\n'
                       '1. Editing\n'
                       '2. Submition\n'
                       '3. Approving\n'
                       '4. Ejection\n'
                       'Please, enter the option number (separate them by commas): ')
    action_num = re.sub('1', 'editing', action_num)
    action_num = re.sub('2', 'submition', action_num)
    action_num = re.sub('3', 'approval', action_num)
    action_num = re.sub('4', 'ejection', action_num)
    action_num = re.sub(' ', '', action_num)
    actions = action_num.split(',')
    giver_id = detect_person(input('Enter the full name of the right giver: '))
    reciever_id = detect_person(input('Enter the full name of the right reciever: '))
    doc_id = detect_doc(input('Enter the name of the document: '))
    con = sqlite3.connect("Fedorenko_DB.db")
    cur = con.cursor()
    for a_type in actions:
        writing = cur.execute("INSERT INTO rights (giver, reciever, doc_id, a_type) "
                              "VALUES (?, ?, ?, ?)", (giver_id, reciever_id, doc_id, a_type))
    con.commit()

def detect_person(name):
    con = sqlite3.connect("Fedorenko_DB.db")
    cur = con.cursor()
    p_id = cur.execute("SELECT person_id, p_name, birthdate, birthplace, p_position "
                         "FROM staff "
                         "WHERE p_name=?", (name,))
    persons = p_id.fetchall()
    if len(persons) == 0:
        print('There is no worker with such a name.')
    elif len(persons) == 1:
        return persons[0][0]
    else:
        i = 1
        print('Please, find the person in the list below')
        for line in persons:
            print(''.join(['(', str(i) , ') Name: ', line[1], '; Birthdate: ', line[2], '; Birthplace: ', line[3], '; Position: ', line[4]]))
            i += 1
        return persons[int(input("Enter the number of the person you meant: "))-1][0]
    con.commit()

def detect_doc(name):
    con = sqlite3.connect("Fedorenko_DB.db")
    cur = con.cursor()
    p_id = cur.execute("SELECT staff.p_name, operations.o_date, operations.o_time"
                       "FROM operations, documents, staff "
                       "WHERE operations.operation = creation AND operations.person_id = staff.p_name AND operations.doc_id = documents.doc_id AND documents.doc_name = ?", (name,))
    docs = p_id.fetchall()
    if len(docs) == 0:
        print('There is no document with such a name.')
    elif len(docs) == 1:
        return docs[0][0]
    else:
        i = 1
        print('Please, consider the information about creation of documents with the name you entered. Find the document in the list.')
        for line in docs:
            print(''.join(['(', str(i) , ') Author\'s name: ', line[1], '; Creation date: ', line[2], '; Creation time: ', line[3]]))
            i += 1
        return docs[int(input("Enter the number of the document you meant: "))-1][0]
    con.commit()


if __name__ == '__main__':
    main_menu()