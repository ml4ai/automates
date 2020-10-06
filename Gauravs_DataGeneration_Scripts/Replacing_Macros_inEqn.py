'''
# replacing macros with their expanded form
def Macros(macro_eq, macro_dict):

    # first spot the greek letters to avoid confusion in between macros and greek letters
    gl_arr = [gl for gl in greek_letters if gl in macro_eq]
    gl_list = []
    for gl in gl_arr:
        gl_list += list(range(macro_eq.find(gl), macro_eq.find(gl)+len(gl)))

    macro_in_eqn = {}
    macro_posi = {}
    for macro in macro_dict.keys():
        if macro in macro_eq:
            print([macro, macro_eq.find(macro)])
            macro_posi[macro] =  macro_eq.find(macro)  # position dictionary of macros
            macro_in_eqn[macro] = macro_dict[macro] # expanded form dictionary of macros

    #removing any possible macro which is a part of greek_letters
    if len(macro_posi)!=0:
        mp = [mp for mp in macro_posi.values() if mp in gl_list]
        if len(mp)!=0:
            macro_in_eqn.pop((list(macro_posi.keys())[list(macro_posi.values()).index(mp[0])]))

        # initializing an indicator flag --> to check if there will be change in the equation
        indicator = False

        for m in macro_in_eqn.keys():
        # replacing the macros with parameters
            if m in macro_eq and '#' in macro_in_eqn[m]:
                try:
                    ff = macro_in_eqn[m]
                    if ff.find('{') != 0:
                        n_var = int(ff[1]) 
                #check the number of parameter given upfront and grab that parameter 
                    n_var_upfront = (ff.find('{')//3) - 1
                    var_upfront = [ff[1+i*3] for i in range(1, n_var_upfront) if n_var_upfront !=0]
                #check the number of parameter given in the eqn and grab those parameter 
                    n_var_rem = n_var - n_var_upfront
                    n_loop = 0
                    var_eqn = []
                    eq_copy = macro_eq
                    b = eq_copy.find(m)
                    b_end = b+len(m)
                    eq_copy = eq_copy[b_end: ]
                    while n_loop < n_var_rem:
                        eq_part1 = eq_copy.find("{")
                        eq_part11 = eq_copy.find("}")
                        var_eqn.append(eq_copy[eq_part1 +1 : eq_part11])
                        eq_copy = eq_copy[eq_part11+1 : ]
                        n_loop+=1
                    list_var = var_upfront + var_eqn 
            #make a dictionaries having parameters and there values
                    temp_macro_dict = {}
                    for a_ind, a in enumerate(list_var):
                        temp_macro_dict['#{}'.format(a_ind+1)] = a 
            # replace the macro with the expanded form
                    ff = ff[ff.find('{'): ]    
                    for tmd in temp_macro_dict.keys():
                        if tmd in ff:
                            ff = ff.replace(tmd, temp_macro_dict[tmd])
                    macro_eq = macro_eq.replace(m,ff)
                    indicator = True
                except:
                     print("MACRO are in wrong format")

        # replacing the macros with no parameters
            if m in macro_eq and '#' not in macro_in_eqn[m]:
                try:
                    macro_eq = macro_eq.replace(m, macro_in_eqn[m])
                    #print(m)
                    indicator = True
                except:
                    print("MACRO is in the wrong format")

        # there are no actual macros to replace --> i.e. all were a part of greek letters       
            else:
                indicator = False

        return(macro_eq, indicator)

    # if length of macro_posi = 0    
    else:
        indicator = False
        return(macro_eq, indicator)
'''
