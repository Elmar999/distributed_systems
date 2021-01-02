import traceback
import ast
import sys
import time
import json
import random
import argparse
from time import sleep
from threading import Thread


from bottle import Bottle, run, request, template
import requests
# ------------------------------------------------------------------------------------------------------
try:
    app = Bottle()

    #board stores all message on the system 
    board = {0 : "Welcome to Distributed Systems Course"} 

    # ------------------------------------------------------------------------------------------------------
    # BOARD FUNCTIONS
    # You will probably need to modify them
    # ------------------------------------------------------------------------------------------------------
    

    def check_pending_requests(board, queue, entry_sequence, element=None):
        if entry_sequence in queue:
            if queue[entry_sequence] == "delete":
                # ignore query and delete pending request from queue
                del queue[entry_sequence]
                return board

            elif queue[entry_sequence][0] == "modify":
                # add element with modified value 
                modified_element = queue[entry_sequence][1]
                board[entry_sequence] = modified_element
                # delete pending request from query
                del queue[entry_sequence]
                return board
        else:
            # if there is no pending request for given entry sequence
            return False
           


    #This functions will add an new element
    def add_new_element_to_store(entry_sequence, element, is_propagated_call=False):
        global board, node_id, queue
        success = False
        try:

            # means we did not find any pending request so we can continue adding new element
            pending_request = check_pending_requests(board, queue, entry_sequence)
            # if pending request is false means, we do not have any pending request in the queue regarding to that entry sequency
            if pending_request == False:
                #if element id is not in the board, we can add new element to the dictionary, with new ID, entry sequence.
                if entry_sequence not in board:
                # assigning new entry element to new key value of dictionary.
                    board[entry_sequence] = element
                    success = True
            else:
                board = val

        except Exception as e:
            print e
        return success

    def modify_element_in_store(entry_sequence, modified_element, is_propagated_call = False):
        global board, node_id, queue
        success = False
        try:
            '''
            In order to modify element in the dictionary board, we take entry sequence(ID) which will be key
            in the dictionary, and we assign new value to the key(ID) of dictionary. Now new entry will be modified_element
            for corresponding key(ID).
            ''' 
            if entry_sequence in board:
                board[entry_sequence] = modified_element
            else:
                queue[entry_sequence] = ["modify", modified_element]

            success = True
        except Exception as e:
            print e
        return success

    def delete_element_from_store(entry_sequence, is_propagated_call = False):
        global board, node_id, delete_key, queue
        success = False
        try:
            # We are deleting specific ID from dictionary.
            if entry_sequence  in board:
                del board[entry_sequence]
            else:
                queue[entry_sequence] = "delete"
            
            success = True
        except Exception as e:
            print e
        return success

    # ------------------------------------------------------------------------------------------------------
    # DISTRIBUTED COMMUNICATIONS FUNCTIONS
    # ------------------------------------------------------------------------------------------------------
    def contact_vessel(vessel_ip, path, payload=None, req='POST'):
        # Try to contact another server (vessel) through a POST or GET, once
        success = False
        try:
            if 'POST' in req:
                res = requests.post('http://{}{}'.format(vessel_ip, path), data=payload)
                print(res.text)
            elif 'GET' in req:
                res = requests.get('http://{}{}'.format(vessel_ip, path))
                print(res.content)
            else:
                print 'Non implemented feature!'
            # result is in res.text or res.json()
            # print(res.text)
            if res.status_code == 200:
                success = True
        except Exception as e:
            print e
        return success

    def propagate_to_vessels(path, payload = None, req = 'POST'):
        global vessel_list, node_id
        for vessel_id, vessel_ip in vessel_list.items():
            if int(vessel_id) != node_id: # don't propagate to yourself
                success = contact_vessel(vessel_ip, path, payload, req)
                if not success:
                    print "\n\nCould not contact vessel {}\n\n".format(vessel_id)


    # ------------------------------------------------------------------------------------------------------
    # ROUTES
    # ------------------------------------------------------------------------------------------------------
    # a single example (index) for get, and one for post
    # ------------------------------------------------------------------------------------------------------
    @app.route('/')
    def index():
        global board, node_id
        return template('server/index.tpl', board_title='Vessel {}'.format(node_id),
                board_dict=sorted({"0":board,}.iteritems()), members_name_string='Dennis Dubrefjord, Elmar Hajizada')


    @app.get('/board')
    def get_board():
        global board, node_id, delete_key, queue, count
        print(queue)
        # print board

        return template('server/boardcontents_template.tpl',board_title='Vessel {}'.format(node_id), board_dict=sorted(board.iteritems()))
    # ------------------------------------------------------------------------------------------------------
    @app.post('/board')
    def client_add_received():
        '''Adds a new element to the board
        Called directly when a user is doing a POST request on /board'''
        global board, node_id, local_clock
        try:

            print("local clock = {}".format(local_clock))
            new_entry = request.forms.get('entry')
            '''
            add element_id(local_clock) + node_id. For example if vessel one submitting its entry with logical clock 10.
            The entry will be added to the board with id 10.1 which is (logical_clock + node_id/10). In this way if there is 
            a concurrent updates it stays concurrent. For example vessel 1 and vessel 2 both have clock 10 and at the same time they submit an entry, then entries will be added as 10.1 and 10.2. So lower id will become first in the board. 
            '''
            if len(board) == 0:
                element_id = 0
            else:
                element_id = local_clock
            add_new_element_to_store(float(element_id) + float(node_id)/10, new_entry) 
            
            # propogate msg with clock to other boards
            
            thread = Thread(target=propagate_to_vessels,
                            args=('/propagate/ADD/' + str(element_id), {'entry': new_entry, 'clock': local_clock, 'id':node_id}, 'POST'))
            thread.daemon = True
            thread.start()
            local_clock += 1

            # return True
        except Exception as e:
            print e
        # return False

    @app.post('/board/<element_id:float>/')
    def client_action_received(element_id):
        global local_clock
        # take entry, will be needed in case of MODIFY.
        entry = request.forms.get('entry')
        
        local_clock += 1

        ''' 
        take option. After looking at other source codes, we found out that in the file of 
        boardcontents_template.tpl, Modify and X buttons are submit buttons with the name "delete", 
        Modify has the value 0 and delete has the value 1.
        '''

        option = request.forms.get('delete')

        # print("local clock = {}".format(local_clock))
        print("element id is {} and clock id is {}".format(element_id, local_clock))

        # if option is 0, means we want to modify element, then we use modify_element_in_store function
        # with the new entry and element_id. We create a thread for propogation.
        if option == '0':
            modify_element_in_store(float(element_id), entry, False)
            thread = Thread(target=propagate_to_vessels,
                            args=('/propagate/MODIFY/' + str(element_id), {'entry': entry, 'clock':local_clock, 'id': node_id}, 'POST'))
            thread.daemon = True
            thread.start()

        # if option is 1, means we want to delete element from board. Then we use delete_element_from_store to 
        # delete entry from board. Then we create a thread to propogate to all vessels.
        elif option == '1':
            delete_element_from_store(float(element_id), False)
            thread = Thread(target=propagate_to_vessels,
                            args=('/propagate/DELETE/' + str(element_id), {'clock': local_clock, 'id': node_id}, 'POST'))
                            # we set daemon to True and thread.start to spawn the thread.
            thread.daemon = True
            thread.start()
           
    
    @app.post('/propagate/<action>/<element_id>')
    def propagation_received(action, element_id):
        global local_clock, concurrent_nodes
        '''
        This post request is used for the propogation purposes, and we check action if we call this post request.
        Actions can be add, delete or modify in this program. We should also cast element_id to the integer type. Because 
        keys(IDs) of the board is in the type of integer and since we passed the element_id in string format to the post request, we need to cast it to int.
        '''

        # update clock with max(local_clock, received_clock) + 1
        received_clock = request.forms.get('clock')
        received_id = request.forms.get('id')
        # print(request.fullpath)
        
        local_clock = max(local_clock, int(received_clock)) + 1


        # print("local clock = {} and received clock = {}".format(local_clock, received_clock))
        
        entry = request.forms.get('entry')
        # queue.append(request.fullpath + "/.{}".format(received_id) + "/{}".format(entry))
        if action == "ADD":
            add_new_element_to_store(float(element_id) + float(received_id)/10, entry, True)
        elif action == "DELETE":
            delete_element_from_store(float(element_id), True)
        elif action == "MODIFY":
            modify_element_in_store(float(element_id), entry, True)

              

    # ------------------------------------------------------------------------------------------------------
    # EXECUTION
    # ------------------------------------------------------------------------------------------------------
    def main():
        global vessel_list, node_id, app, server_list, nodes_list, local_clock, count, queue, concurrent_nodes
        
        concurrent_nodes = dict()
        port = 80
        count = 0
        parser = argparse.ArgumentParser(description='Your own implementation of the distributed blackboard')
        parser.add_argument('--id', nargs='?', dest='nid', default=1, type=int, help='This server ID')
        parser.add_argument('--vessels', nargs='?', dest='nbv', default=1, type=int, help='The total number of vessels present in the system')
        args = parser.parse_args()
        node_id = args.nid
        vessel_list = dict()
        server_list = list()
        nodes_list = list()
        queue = dict()
        local_clock = node_id
        # We need to write the other vessels IP, based on the knowledge of their number
        for i in range(1, args.nbv):
            vessel_list[str(i)] = '10.1.0.{}'.format(str(i))
        

        try:
            run(app, host=vessel_list[str(node_id)], port=port)
        except Exception as e:
            print e
    # ------------------------------------------------------------------------------------------------------
    if __name__ == '__main__':
        main()
except Exception as e:
        traceback.print_exc()
        while True:
            time.sleep(60.)