# coding=utf-8
# ------------------------------------------------------------------------------------------------------
# TDA596 - Lab 1
# server/server.py
# Input: Node_ID total_number_of_ID
# Student: Elmar Hajizada, Dennis Dubrefjord
# ------------------------------------------------------------------------------------------------------
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
    # ------------------------------------------------------------------------------------------------------
    
    #This functions will add an new element
    def add_new_element_to_store(entry_sequence, element, is_propagated_call=False):
        global board, node_id
        success = False
        try:
           #if element id is not in the board, we can add new element to the dictionary, with new ID, entry sequence.
           if entry_sequence not in board:
               # assigning new entry element to new key value of dictionary.
                board[entry_sequence] = element
                success = True
        except Exception as e:
            print e
        return success

    def modify_element_in_store(entry_sequence, modified_element, is_propagated_call = False):
        global board, node_id
        success = False
        try:
            '''
            In order to modify element in the dictionary board, we take entry sequence(ID) which will be key
            in the dictionary, and we assign new value to the key(ID) of dictionary. Now new entry will be modified_element
            for corresponding key(ID).
            ''' 
            board[int(entry_sequence)] = modified_element

            success = True
        except Exception as e:
            print e
        return success

    def delete_element_from_store(entry_sequence, is_propagated_call = False):
        global board, node_id, delete_key
        success = False
        try:
            
            # We are deleting specific ID from dictionary.
            del board[int(entry_sequence)]

            old_board = board  
            board = dict()
            for i, keys in enumerate(old_board):
                board[i] = old_board[keys]
            
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
        res = None
        try:
            if 'POST' in req:
                res = requests.post('http://{}{}'.format(vessel_ip, path), data=payload)
                # print(res.text)
            elif 'GET' in req:
                res = requests.get('http://{}{}'.format(vessel_ip, path))
                # print(res.content)
            else:
                print 'Non implemented feature!'
            # result is in res.text or res.json()
            # print(res.text)
            if res.status_code == 200:
                success = True
        except Exception as e:
            print e
        return success, res

    def propagate_to_vessels(path, payload = None, req = 'POST'):
        global vessel_list, node_id
        for vessel_id, vessel_ip in vessel_list.items():
            if int(vessel_id) != node_id: # don't propagate to yourself
                success, _ = contact_vessel(vessel_ip, path, payload, req)
                if not success:
                    print "\n\nCould not contact vessel {}\n\n".format(vessel_id)




    #define election protocol
    class Node:
        def __init__(self, node_id, election=False, coordinator=False):
            self.node_id = node_id
            self.election = election
            self.coordinator = coordinator
            self.received_counter = 0
            self.coordinator_id = None


    def get_higher_nodes(starting_node):
        # get details of higher nodes
        global node_list
        higher_nodes = list()
        # check if higher node in the network is alive, then append it to list.
        for vessel_id, vessel_ip in vessel_list.items():
            if int(vessel_id) != starting_node and int(vessel_id) > starting_node:
                success, response = contact_vessel('10.1.0.{}'.format((vessel_id)), '/check_alive', None, 'GET')
                if success: 
                    higher_nodes.append(int(vessel_id))
                else:
                    print("node is not alive: {}".format(int(vessel_id)))
        return higher_nodes


    def election_msg(higher_nodes, node_id):
        # send a msg to higher nodes, if there is any active higher node, then current node will not be coordinator
        # move onto next higher node id

        for node in higher_nodes:
            success, response = contact_vessel('10.1.0.{}'.format(str(node)), '/send_election_msg', {"node_id":node_id}, 'POST')


    def check_coordinator():
        global node_list
        # check if there is already a coordinator in the network
        for vessel_id, vessel_ip in vessel_list.items():
            if node_list[int(vessel_id)].coordinator == True:
                return False
        return True


    def send_coordinator_msg(coordinator_id):
        global vessel_list
        for vessel_id, vessel_ip in vessel_list.items():
            if int(vessel_id) != coordinator_id:
                success, response = contact_vessel('10.1.0.{}'.format((vessel_id)), '/coordinator_msg', {"coordinator_id":coordinator_id}, 'POST')



    def elect_leader(starting_node):
        # decide who will start election process
        global server_list, node_id, node_list

        if node_id in node_list and node_list[node_id].node_id == starting_node:
            higher_nodes = get_higher_nodes(starting_node)
            if len(higher_nodes) == 0:
                print("I am the coordinator {}".format(node_id))
                node_list[node_id].coordinator = True
                node_list[node_id].coordinator_id = node_id
                send_coordinator_msg(node_id)
                print("Election process finished")
                return

            print(higher_nodes)
            # print(node_list[starting_node].received_counter)
            # starting node will start the election
            # if there is a not any coordinator in network 
            if check_coordinator():
                # make node.election flag to True
                node_list[starting_node].election = True
                election_msg(higher_nodes, starting_node)

            
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
        global board, node_id, node_list
        print board
        
        '''
        Deleting ID from board can be challenging, if there are 3 elements in board, and we delete second entry, board
        will transform from keys -> 0, 1, 2 to 0, 2. However, we know that IDs should be sequential so in fact new keys were supposed to be 0, 1 even if we delete second entry. Thats why, we should always update IDs if we delete entry from the board. We then take a variable old_board whose keys are 0, 2 and we enumerate old_board. Then i variable will be 
        0, 1 in this example. So new keys for the board dictionary will be 0, 1 with the respective values.
        '''

        return template('server/boardcontents_template.tpl',board_title='Vessel {}'.format(node_id), board_dict=sorted(board.iteritems()))
    # ------------------------------------------------------------------------------------------------------
    @app.post('/board')
    def client_add_received():
        '''Adds a new element to the board
        Called directly when a user is doing a POST request on /board'''
        global board, node_id, node_list
        try:
            coordinator_id = node_list[node_id].coordinator_id
            
            if node_id == coordinator_id:
                #get a new entry
                # new element ID will be the length of board. If we have IDs 0, 1, 2 in board new ID will be 3 which is 
                # length of board. We create thread in order to propogate other vessels. We use thread,start() to spawn the
                # thread. Post request /propogate/ADD/3 with the new entry. Post request will be describe in propogate_to_vessels 
                # function.

                new_entry = request.forms.get('new_entry')
                element_id = len(board)
                add_new_element_to_store(element_id, new_entry) 
                thread = Thread(target=propagate_to_vessels,
                                args=('/propagate/ADD/' + str(element_id), {'entry': new_entry}, 'POST'))
                thread.daemon = True
                thread.start()
            else:
                # contact to coordinator node, coordinator node will handle the request
                new_entry = request.forms.get('entry')
                success, response = contact_vessel('10.1.0.{}'.format((str(coordinator_id))), '/board', {'new_entry': new_entry}, 'POST')
            
                

            # return True
        except Exception as e:
            print e
        # return False

    @app.post('/board/<element_id>/')
    def client_action_received(element_id):
        global node_id, node_list
        # print(type(element_id))

        ''' 
        take option. After looking at other source codes, we found out that in the file of 
        boardcontents_template.tpl, Modify and X buttons are submit buttons with the name "delete", 
        Modify has the value 0 and delete has the value 1.
        '''
       
        coordinator_id = node_list[node_id].coordinator_id
        if node_id == coordinator_id:
            # if option is 0, means we want to modify element, then we use modify_element_in_store function
            # with the new entry and element_id. We create a thread for propogation.
            entry = request.forms.get('entry')
            option = request.forms.get("delete")

            if option == '0':
                modify_element_in_store(element_id, entry, False)
                thread = Thread(target=propagate_to_vessels,
                                args=('/propagate/MODIFY/' + (element_id), {'entry': entry}, 'POST'))
                thread.daemon = True
                thread.start()

            # if option is 1, means we want to delete element from board. Then we use delete_element_from_store to 
            # delete entry from board. Then we create a thread to propogate to all vessels.
            elif option == '1':
                delete_element_from_store(element_id, False)
                thread = Thread(target=propagate_to_vessels,
                                args=('/propagate/DELETE/' + (element_id), None, 'POST'))
                                # we set daemon to True and thread.start to spawn the thread.
                thread.daemon = True
                thread.start()
        else:
            # take entry, will be needed in case of MODIFY.
            entry = request.forms.get('entry')
            option = request.forms.get('delete')
            # contact to coordinator
            success, response = contact_vessel('10.1.0.{}'.format((str(coordinator_id))), '/board/{}/'.format(element_id), {'entry': entry, "delete": option}, 'POST')





        

    @app.post('/propagate/<action>/<element_id>')
    def propagation_received(action, element_id):
        '''
        This post request is used for the propogation purposes, and we check action if we call this post request.
        Actions can be add, delete or modify in this program. We should also cast element_id to the integer type. Because 
        keys(IDs) of the board is in the type of integer and since we passed the element_id in string format to the post request, we need to cast it to int.
        '''
        entry = request.forms.get('entry')
        if action == "ADD":
            add_new_element_to_store(int(element_id), entry, True)
        elif action == "DELETE":
            delete_element_from_store(int(element_id), True)
        elif action == "MODIFY":
            modify_element_in_store(int(element_id), entry, True)


    @app.post('/send_election_msg')
    def send_election_msg():
        global node_id
        # # higher node will receive election msg
        # # it needs to start a new election process 

        node_list[node_id].received_counter += 1
        if node_list[node_id].received_counter == 1:
           thread = Thread(target = elect_leader, args=(node_id,))
           thread.daemon = True
           thread.start()

        return {"response": 200}

    @app.post('/coordinator_msg')
    def coordinator_msg():
        global node_id, node_list
        # send coordinator id to all vessels
        coordinator_id = request.forms.get("coordinator_id")
        node_list[node_id].coordinator_id = coordinator_id
        print("coordinator_id of node {} = {}".format(node_id, node_list[node_id].coordinator_id))  

        return {"response": 200}


    @app.get('/check_alive')
    def check_alive():
        return {"response": 200}
       
   

    # ------------------------------------------------------------------------------------------------------
    # EXECUTION
    # ------------------------------------------------------------------------------------------------------
    def main():
        global vessel_list, node_id, app, server_list, node_list

        port = 80
        parser = argparse.ArgumentParser(description='Your own implementation of the distributed blackboard')
        parser.add_argument('--id', nargs='?', dest='nid', default=1, type=int, help='This server ID')
        parser.add_argument('--vessels', nargs='?', dest='nbv', default=1, type=int, help='The total number of vessels present in the system')
        args = parser.parse_args()
        node_id = args.nid
        vessel_list = dict()
        node_list = dict()
        server_list = list()
        # We need to write the other vessels IP, based on the knowledge of their number
        for i in range(1, args.nbv):
            vessel_list[str(i)] = '10.1.0.{}'.format(str(i))
        

        for i, (vessel_id, vessel_ip) in enumerate(vessel_list.items()):
            server_list.append(int(vessel_id))
            node_list[int(vessel_id)] = Node(int(vessel_id))
        # print(node_list.keys())
        server_list = sorted(server_list)


        starting_node = 3
        elect_leader(starting_node)


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