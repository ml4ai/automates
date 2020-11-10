# -*- coding: utf-8 -*-
"""
Created on Sat Nov  7 21:24:26 2020

@author: gauravs
"""

import re

# Removing unnecessary information or attributes having default values 

def Attribute_Definition(MMLcode, ELEMENTS, Attr_tobeRemoved, Attr_tobeChecked):
    
    # Defining array to keep Attribute definition
    Definition_array = []
    
    for ele in ELEMENTS:
        
        # Getting indices of the position of the element in the MML code
        position = [i for i in re.finditer(r'\b%s\b' % re.escape(ele), MML)]
        
        for p in position:

            # Attribute begining and ending indices
            (Attr_begin, Attr_end) = p.span()
            
            # Length of the definition of the attribute
            Length = MMLcode[Attr_end:].find(">")   
        
            if Length >0:
                
                # Grabbing definition
                Definition = MMLcode[Attr_end: Attr_end+Length]
                print("MathML element:  ", ele)
                print("Defnition:  ", Definition)
                
                # Append unique definition
                if Definition not in Definition_array:
                    Definition_array.append(Definition)
    
    
    for Darr in Definition_array:
        
        # Attribute and its value -- of the element 
        AttributeParameter = Darr.replace(" ", "").split("=")[0]
        AttributeValue = Darr.replace(" ", "").split("=")[1]
        
        # If Attribute has a defualt value, we can remove it
        # Checking which attributes can be removed
        if AttributeParameter not in Attr_tobeRemoved:
            
            if AttributeParameter in Attr_tobeChecked.keys():
                
                if AttributeValue.replace('\\','').replace('"', '') == Attr_tobeChecked[AttributeParameter]:
                    
                    MMLcode = MMLcode.replace(Darr, '')         
        else:
            MMLcode = MMLcode.replace(Darr, '')         
    
    
    # Replacing greek symbols with their unicodes
    
    code_dict = {}
    
    symbol_index = [i for i,c in enumerate(MMLcode.split()) if ';<!--' in c and '&#x' in c]
    
    for si in symbol_index:
        
        code = MMLcode.split()[si].split(";")[0].split('x')[1]
        code_dict[code] = MMLcode.split()[si+1]
    
    for key, value in code_dict.items():
        
        str_to_replace = '<!-- ' + value + ' -->'
        replacing_str = '<!-- ' + '\\u{}'.format(key) + ' -->'
        
        MMLcode = MMLcode.replace(str_to_replace, replacing_str)
    
    # Printing final MML code
    print('MathML code:  ',MMLcode)
    
    return MMLcode
    
    
if __name__ == '__main__':

    arr = open(r'C:\Users\gaura\OneDrive\Desktop\AutoMATES_local\REPO\mathml_data_dev.js', "r").readlines()

    for i, MML in enumerate(arr):
        
        # Printing original MML
        print("===============================")
        print('Original: \n')
        print(MML)
        
        # Removing multiple backslashes
        i = MML.find('\\\\')
        MML = MML.encode().decode('unicode_escape')
        while i >0:
            MML = MML.replace('\\\\', '\\')
            i = MML.find('\\\\')
    
            
        # Removing initial information about URL, display, and equation itself
        begin = MML.find('<math')+len('<math')
        end = MML.find('>')
        MML = MML.replace(MML[begin:end], '')
        
        
        # ATTRIBUTES
        
        ## Attributes commonly used in MathML codes to represent equations
        ELEMENTS = ['mrow', 'mi', 'mn', 'mo', 'ms', 'mtext', 'math', 'mtable', 'mspace', 'maction', 'menclose', 
                      'merror', 'mfenced', 'mfrac', 'mglyph', 'mlabeledtr', 'mmultiscripts', 'mover', 'mroot',
                      'mpadded', 'mphantom', 'msqrt', 'mstyle', 'msub', 'msubsup', 'msup', 'mtd', 'mtr', 'munder',
                      'munderover', 'semantics']
        
        ## Attributes that can be removed
        Attr_tobeRemoved = ['class', 'id', 'style', 'href', 'mathbackground', 'mathcolor']
        
        ## Attributes that need to be checked before removing, if mentioned in code with their default value,
        ## will be removed else will keep it. This dictionary contains all the attributes with thier default values.
        Attr_tobeChecked = {
                            'displaystyle':'false', 'mathsize':'normal', 'mathvariant':'normal','fence':'false',
                            'accent':'false', 'movablelimits':'false', 'largeop':'false', 'stretchy':'false',
                            'lquote':'&quot;', 'rquote':'&quot;', 'overflow':'linebreak', 'display':'block',
                            'denomalign':'center', 'numalign':'center', 'align':'axis', 'rowalign':'baseline',
                            'columnalign':'center', 'alignmentscope':'true', 'equalrows':'true', 'equalcolumns':'true',
                            'groupalign':'{left}', 'linebreak':'auto', 'accentunder':'false'
                           }
        
                                       
        MML = Attribute_Definition(MML, ELEMENTS, Attr_tobeRemoved, Attr_tobeChecked)    
         
        print("Modified: \n")
        print(MML)   
