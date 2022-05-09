# tCAST file format for corpus generation version v3:

```
function_tokens_map
<fn_token>:<function_name>


global_tokens_map
<global_token>:<global_var_name>  
# NOTE: global_token will be used throughout all function tokenizations.


# Function tokenizations
[[
function_name: <fn_name>
token_sequence
[<List of tCAST tokens>]


variable_tokens_map
<variable_token>:<original_variable_name>


value_tokens_map
<value_token>:<literal_value>
]]*
```