def produce_res_rec(counter,result_pack,send_list = None):
    """
    A beautiful recursive tree like hash producer
    """
    global_result = {}
    global_result ['id'] = counter


    #print "The pack is counter:",counter
    #print "The pack is result_pack:",result_pack
    #print "The pack is global_result:",global_result
    #the final step of the execution
    if type(result_pack) != list and type(result_pack) != dict:
        return {'id':counter,'text':str(result_pack)}
    
    elif type(result_pack) == list :
        for result_list in result_pack:
            counter = 2*counter
            if type(result_list) == list:
                tmp_list_result = produce_res_rec(counter,result_list,[])
                global_result['text'] = 'res%s%s'%(counter,counter)
                if not global_result.has_key('item'):
                      global_result['item'] = []

                if type(tmp_list_result) == list:
                    global_result['item'].extend(tmp_list_result)
                else:
                    global_result['item'].append(tmp_list_result)

            else:
                tmp_list_result = produce_res_rec(counter,result_list)
                if type(tmp_list_result) == list:
                    send_list.extend(tmp_list_result)
                else:
                    send_list.append(tmp_list_result)

    elif type(result_pack) == dict :
        for key_result,value_result in result_pack.iteritems():
            #a new key added
            global_result['text'] = str(key_result)
            if not global_result.has_key('item'):
                global_result['item'] = []
           
            if type(value_result) == list:
                tmp_dict_res = produce_res_rec((2*counter+1),value_result,[])
                
            else:
                tmp_dict_res = produce_res_rec((2*counter+1),value_result)
            if type(tmp_dict_res) == list :
                global_result['item'].extend(tmp_dict_res)
            else:
                global_result['item'].append(tmp_dict_res)
    
    else: #shouldnt come here !
        return {}

    if not send_list:
        return global_result
    else:
        return send_list

if __name__ == "__main__":
    """
      
    main_pack = {
            'minion':{'result':True}
            }
    
    main_pack = {
            'minion':[["one","two"],["three","four"]]
            }
    
    
    main_pack = {
            'minion':{'result':True}
            }
    
    
    """
    main_pack = {
            'minion':[
                {
                    'res1':'hey'
                    },
                {
                    'res2':'wey'
                    }
                ]
            }
    global_result = {'id':0,'item':[]}
    final = produce_res_rec(1,main_pack)
    print "The final pack is like that : "
    global_result['item'].append(final)
    print global_result


