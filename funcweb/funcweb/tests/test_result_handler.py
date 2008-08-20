#all the test cases which are 16 and handle 4 level 
#list hash indentation are tested manually because 
#couldnt find a way to automate that process :)
#zeros stands for dict type 1 id for lists

test_0000 = {
        'minion1':{
            'result1':{
                'result11':{
                        'result111':{
                            'result1111':1111
                        }
                    }
                },
                'result12':{
                    'result12':{
                        'result122':{
                            'result1222':1222
                        }
                    }
                }
            },
            'minion2':{
                'result2':{
                    'result22':{
                        'result222':{
                            'result2222':2222
                        }
                    }
                }
            ,
            'result2s':{
                    'result2s':{
                        'result12s':{
                            'result122s':1225
                        }
                    }
                }
            }
        }

test_0001 = {
            'minion1':{
                'result1':{
                    'result11':{
                        'result111':[1111,1111,1111]
                        }
                    },
                
                'result12':{
                    'result12':{
                        'result122':[1222,1222,1222]
                        }
                }
            },
            'minion2':{
                'result2':{
                    'result22':{
                        'result222':[2222,2222,2222]
                    }
                },
            'result2s':{
                    'result2s':{
                        'result12s':[2225,2225,2225]
                    }
                }
            }
        }

test_0010 = {
            'minion1':{
                'result1':{
                    'result11':[{'res111':111},{'res111':111}]
                        },
                'result12':{
                    'result122':[{'res1222':1222},{'res1222':1222}]
                        }
            },
            'minion2':{
                'result2':{
                    'result22':[{'res222':222},{'res222':222}]
                        },
                'result25':{
                    'result225':[{'res2225':2225},{'res2225':2225}]
                        }
                }
        }

test_0011 = {
            'minion1':{
                'result1':{
                    'result11':[[1111,1111],[1111,1111]]
                        },
                'result12':{
                    'result122':[[1222,1222],[1222,1222]]
                        }
            },
            'minion2':{
                'result2':{
                    'result22':[[2222,2222],[2222,2222]]
                        },
                'result25':{
                    'result225':[[2225,2225],[2225,2225]]
                        }
                }
        }

test_0100 = {
            'minion1':{
                'result1':[
                    {'dict11':{'dict111':1111},'dict16':{'dict111':1111}},
                    {'dict12':{'dict122':1222},'dict18':{'dict122':1222}}
                ],
                'result13':[
                    {'dict13':{'dict133':1333},'dict15':{'dict133':1333}},
                    {'dict14':{'dict144':1444},'dict16':{'dict144':1444}}
                ]
                },
            'minion2':{
                'result2':[
                    {'dict22':{'dict222':2222},'dict24':{'dict244':2444}},
                    {'dict23':{'dict233':2333},'dict25':{'dict255':2555}}
                ],
                'result21':[
                    {'dict21':{'dict211':2111},'dict23':{'dict233':2333}},
                    {'dict24':{'dict244':2444},'dict27':{'dict244':2444}}
                ]
                }
                }

test_0101 = {
            'minion1':{
                'result1':[
                    {'dict11':[1111,1111],'dict16':[1666,1666]},
                    {'dict12':[1222,1222],'dict18':[1888,1888]}
                ],
                'result13':[
                    {'dict13':[1333,1333],'dict15':[1555,1555]},
                    {'dict14':[1444,1444],'dict16':[1666,1666]}
                ]
                },
            'minion2':{
                'result2':[
                    {'dict22':[2222,2222],'dict24':[2444,2444]},
                    {'dict23':[2333,2333],'dict25':[2555,2555]}
                ],
                'result21':[
                    {'dict21':[2111,2111],'dict23':[2333,2333]},
                    {'dict24':[2444,2444],'dict27':[2777,2777]}
                ]
                }
                }

test_0110 = {
            'minion1':{
                'result1':[
                    [{'dict11':[1111,1111]},{'dict16':[1666,1666]}],
                    [{'dict12':[1222,1222]},{'dict18':[1888,1888]}]
                ],
                'result13':[
                    [{'dict13':[1333,1333]},{'dict15':[1555,1555]}],
                    [{'dict14':[1444,1444]},{'dict16':[1666,1666]}]
                ]
                },
            'minion2':{
                'result2':[
                    [{'dict22':[2222,2222]},{'dict24':[2444,2444]}],
                    [{'dict23':[2333,2333]},{'dict25':[2555,2555]}]
                ],
                'result21':[
                    [{'dict21':[2111,2111]},{'dict23':[2333,2333]}],
                    [{'dict24':[2444,2444]},{'dict27':[2777,2777]}]
                ]
                }
                }

test_0111 = {
            'minion1':{
                'result1':[
                    [[1111,1111],[1666,1666]],
                    [[1222,1222],[1888,1888]]
                ],
                'result13':[
                    [[1333,1333],[1555,1555]],
                    [[1444,1444],[1666,1666]]
                ]
                },
            'minion2':{
                'result2':[
                    [[2222,2222],[2444,2444]],
                    [[2333,2333],[2555,2555]]
                ],
                'result21':[
                    [[2111,2111],[2333,2333]],
                    [[2444,2444],[2777,2777]]
                ]
                }
                }

test_1000 = {
            'minion1':{
                'res1': [
                {'result11':{'result111':{'result1111':1111}}},
                {'result13':{'result133':{'result1333':1333}}}
                ],
                'res11':[
                {'result15':{'result155':{'result1555':1555}}},
                {'result17':{'result177':{'result1777':1777}}}
                ],

            },
            'minion2':{
                'res2':[
                {'result21':{'result211':{'result2111':2111}}},
                {'result23':{'result233':{'result2333':2333}}}
                ],
                'res22':[
                {'result25':{'result255':{'result2555':2555}}},
                {'result27':{'result277':{'result2777':2777}}}
                ],
            }
        }

test_1001 = {
            'minion1':{
                'res1': [
                {'result11':{'result111':[1111,1111]}},
                {'result13':{'result133':[1333,1333]}}
                ],
                'res11':[
                {'result15':{'result155':[1555,1555]}},
                {'result17':{'result177':[1777,1777]}}
                ],

            },
            'minion2':{
                'res2':[
                {'result21':{'result211':[2111,2111]}},
                {'result23':{'result233':[2333,2333]}}
                ],
                'res22':[
                {'result25':{'result255':[2555,2555]}},
                {'result27':{'result277':[2777,2777]}}
                ],
            }
        }

test_1010 = {
            'minion1':{
                'res1': [
                {'result11':[{'result111':[1111,1111]}]},
                {'result13':[{'result133':[1333,1333]}]}
                ],
                'res11':[
                {'result15':[{'result155':[1555,1555]}]},
                {'result17':[{'result177':[1777,1777]}]}
                ],

            },
            'minion2':{
                'res2':[
                {'result21':[{'result211':[2111,2111]}]},
                {'result23':[{'result233':[2333,2333]}]}
                ],
                'res22':[
                {'result25':[{'result255':[2555,2555]}]},
                {'result27':[{'result277':[2777,2777]}]}
                ],
            }
        }


test_1011 = {
            'minion1':{
                'res1': [
                {'result11':[[1111,1111],[1111,1111]]},
                {'result13':[[1333,1333],[1333,1333]]}
                ],
                'res11':[
                {'result15':[[1555,1555],[1555,1555]]},
                {'result17':[{'result177':[1777,1777]}]}
                ],

            },
            'minion2':{
                'res2':[
                {'result21':[[2111,2111],[2111,2111]]},
                {'result23':[[2333,2333],[2333,2333]]}
                ],
                'res22':[
                {'result25':[[2555,2555],[2555]]},
                {'result27':[[2777,2777],[2555]]}
                ],
            }
        }

test_1100 = {
            'minion1':{
                'res1': [
                [{'result11':{'result111':{'result1111':1111}}}],
                [{'result13':{'result133':{'result1333':1333}}}]
                ],
                'res11':[
                [{'result15':{'result155':{'result1555':1555}}}],
                [{'result17':{'result177':{'result1777':1777}}}]
                ],

            },
            'minion2':{
                'res2':[
                [{'result21':{'result211':{'result2111':2111}}}],
                [{'result23':{'result233':{'result2333':2333}}}]
                ],
                'res22':[
                [{'result25':{'result255':{'result2555':2555}}}],
                [{'result27':{'result277':{'result2777':2777}}}]
                ],
            }
        }

test_1101 = {
            'minion1':{
                'res1': [
                [{'result11':{'result111':[1111,1111,1111]}}],
                [{'result13':{'result133':[1333,1333,1333]}}]
                ],
                'res11':[
                [{'result15':{'result155':[1555,1555,1555]}}],
                [{'result17':{'result177':[1777,1777,1777]}}]
                ],

            },
            'minion2':{
                'res2':[
                [{'result21':{'result211':[2111,2111,2111]}}],
                [{'result23':{'result233':[2333,2333,2333]}}]
                ],
                'res22':[
                [{'result25':{'result255':[2555,2555,2555]}}],
                [{'result27':{'result277':[2777,2777,2777]}}]
                ],
            }
        }

test_1110 = {
            'minion1':{
                'res1': [
                [[{'result111':{'result1111':1111}}]],
                [[{'result133':{'result1333':1333}}]]
                ],
                'res11':[
                [[{'result155':{'result1555':1555}}]],
                [[{'result177':{'result1777':1777}}]]
                ],

            },
            'minion2':{
                'res2':[
                [[{'result211':{'result2111':2111}}]],
                [[{'result233':{'result2333':2333}}]]
                ],
                'res22':[
                [[{'result255':{'result2555':2555}}]],
                [[{'result277':{'result2777':2777}}]]
                ],
            }
        }


test_1111 = {
            'minion1':{
                'res1': [
                [[[1111,1111,1111],[1111,1111,1111]]],
                [[[1222,1222,1222],[1222,1222,1222]]]
                ],
                'res11':[
                [[[1555,1555,1555],[1555,1555,1555]]],
                [[[1777,1777,1777],[1777,1777,1777]]]
                ],

            },
            'minion2':{
                'res2':[
                [[[2111,2111,2111],[2111,2111,2111]]],
                [[[2333,2333,2333],[2333,2333,2333]]]
                ],
                'res22':[
                [[[2555,2555,2555],[2555,2555,2555]]],
                [[[2777,2777,277],[2777,2777,2777]]]
                ],
            }
        }

test_cases = [
        test_0000,
        test_0001,
        test_0010,
        test_0011,
        test_0100,
        test_0101,
        test_0110,
        test_0111,
        test_1000,
        test_1001,
        test_1010,
        test_1011,
        test_1100,
        test_1101,
        test_1101,
        test_1110,
        test_1111
        ]

from funcweb.result_handler import produce_res_rec

def test_result_handler():
    """
    Run handler cases
    """

    for test_case in test_cases:
        result = produce_res_rec(test_case)
        #not a perfect one but it is just a poc
        #if sth is wrong can be seen here
        #if someone wants to add more casess it is 
        #just enough to add them to the list
        #print result
        assert type(result) == list

