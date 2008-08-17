global_max = 0
def produce_res_rec(result_pack):
    """
    A beautiful recursive tree like hash producer
    """
    send_list = []
    global global_max
    #print "The pack is counter:",counter
    #print "The pack is result_pack:",result_pack
    #print "The pack is global_result:",global_result
    #the final step of the execution
    if type(result_pack) != list and type(result_pack) != dict:
        global_max = global_max + 1
        return {'id':global_max,'text':str(result_pack)}
    
    elif type(result_pack) == list :
        for result_list in result_pack:
            if type(result_list) == list:
                #if there is a new list then the new parent trick
                global_max = global_max +1
                tmp_parent = {}
                tmp_parent['id'] = global_max
                tmp_parent['text'] = 'leaf_result%s'%(global_max)

                tmp_list_result = produce_res_rec(result_list)

                if tmp_list_result and type(tmp_list_result) == list:
                    tmp_parent['item'] = []
                    tmp_parent['item'].extend(tmp_list_result)
                elif tmp_list_result:
                    tmp_parent['item'] = []
                    tmp_parent['item'].append(tmp_list_result)
                #appended to the parent
                send_list.append(tmp_parent)

            else:
                tmp_list_result = produce_res_rec(result_list)
                if type(tmp_list_result) == list:
                    send_list.extend(tmp_list_result)
                else:
                    send_list.append(tmp_list_result)

    elif type(result_pack) == dict :
        for key_result,value_result in result_pack.iteritems():
            #a new key added
            global_max = global_max +1
            tmp_parent = {}
            tmp_parent ['id'] = global_max
            tmp_parent ['text'] = str(key_result)
           
            tmp_dict_res = produce_res_rec(value_result)
                
            if tmp_dict_res and type(tmp_dict_res) == list :
                tmp_parent ['item'] = []
                tmp_parent['item'].extend(tmp_dict_res)
            elif tmp_dict_res:
                tmp_parent ['item'] = []
                tmp_parent['item'].append(tmp_dict_res)

            send_list.append(tmp_parent)
    
    else: #shouldnt come here !
        return {}

    return send_list

if __name__ == "__main__":
    """
      
      
    main_pack = {
            'minion':[["one","two"],["three","four"]]
            }
    
    
    
    
       
    
    
    main_pack = {
            
                'minion':{
                    'result1':True,
                    'result2':False
                    },
                'minion2':{
                    'result3':True,
                    'result4':False
                    },
                'minion3':{
                    'result5':True,
                    'result6':False
                    }

        
            }
    """
    
    main_pack = {
            'minion1':[
                {
                    'res1':[['hey','hhhey'],['mey','mmmey']]
                    },
                {
                    'res2':['wey','dey']
                    }
                ],
            'minion2':[
                {
                    'res3':['nums','mums']
                    },
                {
                    'res4':['wums','dums']
                    }
                ]
 
            }


    final = produce_res_rec(main_pack)
    print "The final pack is like that : "
    print final


