/* GCC plugin APIs.

   Copyright (C) 2009, 2010, 2011 Mingjie Xing, mingjie.xing@gmail.com. 

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 2 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program.  If not, see <http://www.gnu.org/licenses/>. */

#define _GNU_SOURCE

#include <stddef.h>
#include <stdlib.h>
#include <stdarg.h>
#include <stdio.h>
#include <ctype.h>

/* GCC header files.  */


#include "gcc-plugin.h"
#include "plugin.h"
#include "plugin-version.h"


#include "tree.h"
#include "gimple.h"
#include "gimple-iterator.h"
#include "coretypes.h"
#include "diagnostic.h"
// #include "tree-flow.h"
#include "tree-cfg.h"
#include "tree-pass.h"
#include "cfgloop.h"
#include "cgraph.h"
#include "options.h"
#include "context.h"

#include "langhooks.h"

/* plugin license check */

int plugin_is_GPL_compatible;

#define MAX_RECORD_TYPES 10000
#define MAX_LINE_NUMBER 16000


tree record_types[MAX_RECORD_TYPES];
int record_type_count = 0;

FILE *json_f;

int json_indent_level = 0;
int json_needs_comma = 0;

#define JSON_ARRAY  1
#define JSON_OBJECT  2


#ifdef TRACE_GCC_BRIDGE
#define TRACE(...) printf(__VA_ARGS__)
#else
#define TRACE(...) do { if(1) printf(__VA_ARGS__); } while(0)
#endif

typedef struct json_context {
  int needs_comma;
  int type;
  int indent;
} json_context;


json_context json_context_stack[128];
int json_context_head = 0;

void json_context_push(int type) {
  json_context_head ++;
  json_context_stack[json_context_head].needs_comma = false;
  json_context_stack[json_context_head].type = type;
}

void json_context_pop() {
  json_context_head--;
}

/* Json writing functions */

void json_indent() {
  int i;
  for(i=0;i<json_context_head;++i) {
    fprintf(json_f, "  ");
  }
}

void json_pre_value() {
  json_context *context = &json_context_stack[json_context_head];
  if(context->type == JSON_ARRAY) {
    if(context->needs_comma) {
      fprintf(json_f, ",");
    }
    context->needs_comma = 1;
    fprintf(json_f, "\n");
    json_indent(); 
  }
}

void json_start_object() {
  json_pre_value();
  fprintf(json_f, "{");
  json_context_push(JSON_OBJECT);
}

void json_start_array() {
  fprintf(json_f, "[");
  json_context_push(JSON_ARRAY);
}

void json_null() {
  json_pre_value();
  fprintf(json_f, "null");
}

void json_field(const char *name) {
  json_context *context = &json_context_stack[json_context_head];
  if(context->needs_comma) {
    fprintf(json_f, ",");
  }
  context->needs_comma = 1;
  fprintf(json_f, "\n");
  json_indent();
  fprintf(json_f, "\"%s\": ", name);

  json_context_stack[json_context_head].needs_comma = 1;
}


void json_string(const char *value, int length) {
  putc('"', json_f);
  while (--length >= 0) {
    char ch = *value++;
	  if (ch >= ' ' && ch < 127) {
	    if(ch == '\\' || ch == '"') {
	      putc('\\', json_f);
	    }
      putc(ch, json_f);
    } else {
	    fprintf(json_f, "\\u%04x", ch);	      
    }
  }
  putc('"', json_f);
}

void json_string_field(const char *name, const char *value) {
  json_field(name);
  json_string(value, strlen(value));
}

void json_string_field2(const char *name, const char *value, int length) {
  json_field(name);
  json_string(value, length);
}


void json_int(long value) {
  json_pre_value();
  fprintf(json_f, "%ld", value);
}

void json_string_value(const char * value) {
  json_pre_value();
  json_string(value, strlen(value));
}

void json_ptr(void *p) {
  json_pre_value();
  fprintf(json_f, "\"%p\"", p);
}

void json_int_field(const char *name, long value) {
  json_field(name);
  json_int(value);
}



void json_bool_field(const char *name, int value) {
  json_field(name);
  fprintf(json_f, value ? "true" : "false");
}


void json_array_field(const char *name) {
  json_field(name);
  json_start_array();
}

void json_end_array() {
  fprintf(json_f, "\n");
  json_context_pop();
  json_indent();
  fprintf(json_f, "]");
}

void json_end_object() {
  json_context_pop();
  fprintf(json_f, "\n");
  json_indent();
  fprintf(json_f, "}");
}


/* Post pass */

static void dump_type(tree type);

static void dump_op(tree op);


static void dump_function_type(tree type) {

  TRACE("dump_function_type: dumping returnType\n");
  
  json_field("returnType");
  dump_type(TREE_TYPE(type));
      
  // The TYPE_ARG_TYPES are a TREE_LIST of the argument types. 
  // The TREE_VALUE of each node in this list is the type of the 
  // corresponding argument; the TREE_PURPOSE is an expression 
  // for the default argument value, if any. If the last node in 
  // the list is void_list_node (a TREE_LIST node whose TREE_VALUE 
  // is the void_type_node), then functions of this type do not 
  // take variable arguments. 
  // Otherwise, they do take a variable number of arguments.  
  
  int variable_arguments;

  TRACE("dump_function_type: dumping argumentTypes\n");

  tree last_arg = TYPE_ARG_TYPES(type);
  
  if(last_arg != NULL_TREE) {
    
    tree next_arg = TREE_CHAIN(last_arg);


    json_array_field("argumentTypes");
    while(next_arg != NULL_TREE) {
      dump_type(TREE_VALUE(last_arg));
      last_arg = next_arg;
      next_arg = TREE_CHAIN(next_arg);
    }

    TRACE("dump_function_type: dumping lastArg\n");
    
    if(TREE_CODE(TREE_VALUE(last_arg)) == VOID_TYPE) {
      variable_arguments = 0;
    } else {
      variable_arguments = 1;
      dump_type(TREE_VALUE(last_arg));
    }
    json_end_array();
  }
  
  json_bool_field("variableArguments", variable_arguments);
  
}

static const char* get_type_name(tree node) {

  enum tree_code_class tclass = TREE_CODE_CLASS (TREE_CODE(node));

  if(tclass == tcc_declaration) {
    TRACE("get_type_name: tclass == tc/c_declaration\n");
    if (DECL_NAME (node)) {
      return IDENTIFIER_POINTER(DECL_NAME (node));
    }
  } else if(tclass == tcc_type) {
    TRACE("get_type_name: tclass == tcc_type\n");  
    if (TYPE_NAME (node)) {
      if (TREE_CODE (TYPE_NAME (node)) == IDENTIFIER_NODE)
      {
        return IDENTIFIER_POINTER (TYPE_NAME (node));

      } else if (TREE_CODE (TYPE_NAME (node)) == TYPE_DECL
                   && DECL_NAME (TYPE_NAME (node)))
      {
        return IDENTIFIER_POINTER (DECL_NAME (TYPE_NAME (node)));
      }
    }
  }
  return NULL;
}

static void dump_record_type(tree type) {
  
  TRACE("dump_record_type: entering\n");

  // the same type may have multiple AST nodes
  // http://www.codesynthesis.com/~boris/blog/2010/05/17/parsing-cxx-with-gcc-plugin-part-3/
  type = TYPE_MAIN_VARIANT(type);
  
  json_field("id");
  json_ptr(type);
  
  // have we already encountered this record type?
  int i;
  for(i=0;i<record_type_count;++i) {
    if(record_types[i] == type) {
      TRACE("dump_record_type: already seen, exiting\n");
      return;
    }
  }
  
  // nope, add it to the list
  if(record_type_count < MAX_RECORD_TYPES) {
    record_types[record_type_count] = type;
    record_type_count++;
  } else {
    printf("TOO MANY RECORD TYPES!!!!");
  }
  TRACE("dump_record_type: added to the list, exiting\n");
}

static void dump_record_type_decl(tree type) {

  TRACE("dump_record_type_decl: entering\n");
    
  json_start_object();
  json_field("id");
  json_ptr(type);
  
  json_bool_field("union", (TREE_CODE(type) == UNION_TYPE));
    
    
  TRACE("dump_record_type_decl: writing name\n");
  const char *name = get_type_name(type);
  if(name) {
    json_string_field("name", name);
    TRACE("dump_record_type_decl: name = %s\n", name);
  } 
  
  
  if(TYPE_SIZE(type)) {
    json_int_field("size", TREE_INT_CST_LOW(TYPE_SIZE(type)));
  }
    
  TRACE("dump_record_type_decl: writing fields\n");
  tree field =  TYPE_FIELDS(type);
  json_array_field("fields");
  while(field) {
    if(TREE_CODE(field) == FIELD_DECL) {
        // skip fields without an offset. 
        // Not sure what they do 
        if(DECL_FIELD_OFFSET (field)) {
          json_start_object();
          json_int_field("id", DEBUG_TEMP_UID (field));
          if(DECL_NAME(field)) {
            json_string_field("name", IDENTIFIER_POINTER(DECL_NAME(field)));
          }
          json_int_field("offset", int_bit_position(field));              
          if(DECL_SIZE(field)) {
            json_int_field("size", TREE_INT_CST_LOW (DECL_SIZE (field)));
          } else {
            json_int_field("size", 0); 
          }        
          json_field("type");
          dump_type(TREE_TYPE(field));
          json_end_object();
        }
    }
    field = TREE_CHAIN(field);
  }
  json_end_array();
  json_end_object();
  
  TRACE("dump_record_type_decl: exiting\n");
}

static void dump_constructor(tree node) {
  unsigned HOST_WIDE_INT ix;
  tree field, val;
  bool is_struct_init = FALSE;

  json_bool_field("clobber", TREE_CLOBBER_P(node));
  
 json_array_field("elements");

  if (TREE_CODE (TREE_TYPE (node)) == RECORD_TYPE
      || TREE_CODE (TREE_TYPE (node)) == UNION_TYPE)
       is_struct_init = TRUE;

  FOR_EACH_CONSTRUCTOR_ELT (CONSTRUCTOR_ELTS (node), ix, field, val)
  {
    json_start_object();

    if (field)
      {
        json_field("field");
        dump_op(field);
      }
    
    json_field("value");
    dump_op(val);
    
    json_end_object();
  }
  
  json_end_array();
}

static void dump_type(tree type) {
  TRACE("dump_type: entering: %s\n", get_tree_code_name(TREE_CODE(type)));
  json_start_object();
  json_string_field("type", get_tree_code_name(TREE_CODE(type)));

  if(TYPE_SIZE(type)) {
    json_int_field("size", TREE_INT_CST_LOW(TYPE_SIZE(type)));
  }
  
  switch(TREE_CODE(type)) {
  case INTEGER_TYPE:
    json_bool_field("unsigned", TYPE_UNSIGNED(type));
    break;
  case REAL_TYPE:
    break;
  case POINTER_TYPE:
  case REFERENCE_TYPE:
    json_field("baseType");
    dump_type(TREE_TYPE(type));
    break;

  case OFFSET_TYPE:
    json_field("offsetBaseType");
    dump_type(TYPE_OFFSET_BASETYPE(type));
    json_field("baseType");
    dump_type(TREE_TYPE(type));
    break;

  case ARRAY_TYPE:
    json_field("componentType");
    dump_type(TREE_TYPE(type));
    
    if(TYPE_DOMAIN(type)) {
      tree domain = TYPE_DOMAIN(type);
      json_field("lbound");
      json_int(TREE_INT_CST_LOW(TYPE_MIN_VALUE(domain)));

      tree ubound = TYPE_MAX_VALUE(domain);
      if(ubound && TREE_CODE(ubound) == INTEGER_CST) {   
        json_field("ubound");
        json_int(TREE_INT_CST_LOW(TYPE_MAX_VALUE(domain)));
      }
      
    }
    break;
    
  case FUNCTION_TYPE:
  case METHOD_TYPE:
    dump_function_type(type);
    break;
    
  case UNION_TYPE:
  case RECORD_TYPE:
    dump_record_type(type);
    break;
    
  }
  json_end_object();
  TRACE("dump_type: exiting: %s\n", get_tree_code_name(TREE_CODE(type)));
}

void dump_real_cst(tree op) {

  long buf[4];
  memset(buf, 0, sizeof(long)*4);

  REAL_VALUE_TYPE r = TREE_REAL_CST(op);
  real_to_target   (buf, &r, &ieee_double_format);

  json_field("bits");
  fprintf(json_f, "\"%08x%08x\"", (int)buf[1], (int)buf[0]);

  char string[100];
  real_to_decimal (string, &r, sizeof (string), 0, 1);
  json_field("decimal");
  fprintf(json_f, "\"%s\"", string);
}


static void dump_op(tree op) {
 	REAL_VALUE_TYPE d;
 	
  TRACE("dump_op: entering\n");

  if(op) {
  
  
    if(TREE_CODE(op)) {
      TRACE("dump_op: code = %s\n", get_tree_code_name(TREE_CODE(op)));
    } else {
      TRACE("dump_op: TREE_CODE(op) == NULL\n");
    }
    
    json_start_object();
    json_string_field("code", get_tree_code_name(TREE_CODE(op)));
    
    if(TREE_CODE(op) != TREE_LIST) {
        json_field("type");
        dump_type(TREE_TYPE(op));
    }

    TRACE("dump_op: starting switch\n");

    switch(TREE_CODE(op)) {
    case FUNCTION_DECL:
      json_int_field("id", DEBUG_TEMP_UID (op));
      json_string_field("name", IDENTIFIER_POINTER(DECL_ASSEMBLER_NAME(op)));
      break;
      
    case PARM_DECL:
    case VAR_DECL:
      json_int_field("id", DEBUG_TEMP_UID (op));
      if(DECL_NAME(op)) {
        json_string_field("name", IDENTIFIER_POINTER(DECL_NAME(op)));
      }
      if (DECL_ASSEMBLER_NAME_SET_P (op)) {
        json_string_field("mangledName",  IDENTIFIER_POINTER (DECL_ASSEMBLER_NAME (op)));
      }
      break;

    case FIELD_DECL:
      json_int_field("id", DEBUG_TEMP_UID (op));
      if(DECL_NAME(op)) {
        json_string_field("name", IDENTIFIER_POINTER(DECL_NAME(op)));
        TRACE("field_name = %s\n", IDENTIFIER_POINTER(DECL_NAME(op)));
      }
      // json_int_field("offset", int_bit_position(op));
      json_int_field("size", TREE_INT_CST_LOW (DECL_SIZE (op)));
      break;
      
    case CONST_DECL:
      json_field("value");
      dump_op(DECL_INITIAL(op));
      break;
          
    case INTEGER_CST:
      json_int_field("value", TREE_INT_CST_LOW (op));
      json_field("type");
      dump_type(TREE_TYPE(op));
      break;
      
    case REAL_CST:
      dump_real_cst(op);
      json_field("type");
      dump_type(TREE_TYPE(op));
	  break;
	    
    case COMPLEX_CST:
      json_field("real");
      dump_op(TREE_REALPART(op));
      json_field("im");
      dump_op(TREE_IMAGPART(op));
      break;
	    
	  case STRING_CST:
	    json_string_field2("value", TREE_STRING_POINTER(op),
        TREE_STRING_LENGTH (op));
      json_field("type");
      dump_type(TREE_TYPE(op));
      break;
	    
	  case MEM_REF:
	    json_field("pointer");
	    dump_op(TREE_OPERAND(op, 0));
	    json_field("offset");
	    dump_op(TREE_OPERAND(op, 1));
	    break;
	    
	  case NOP_EXPR:
	    json_field("value");
	    dump_op(TREE_OPERAND(op, 0));
	    break;
	    
	  case ARRAY_REF:
	    json_field("array");
 	    dump_op(TREE_OPERAND(op, 0));
 	    
 	    json_field("index");
 	    dump_op(TREE_OPERAND(op, 1));
      break;
      
    case REALPART_EXPR:
    case IMAGPART_EXPR:
      json_field("complexValue");
      dump_op(TREE_OPERAND(op, 0));
      break;
      
    case ADDR_EXPR:
      json_field("value");
      dump_op(TREE_OPERAND(op, 0));
 	    // json_field("offset");
 	    // dump_op(TREE_OPERAND(op, 1));
      break;
      
    case CONSTRUCTOR:
      dump_constructor(op);
      break;
      
    case COMPONENT_REF:
      json_field("value");
      TRACE("dump_op: writing COMPONENT_REF value\n");
      dump_op(TREE_OPERAND(op, 0));

      json_field("member");
      TRACE("dump_op: writing COMPONENT_REF member\n");
      dump_op(TREE_OPERAND(op, 1));
      break;

    case BIT_FIELD_REF:
      json_field("value");
      dump_op(TREE_OPERAND (op, 0));
      json_int_field("size", TREE_INT_CST_LOW(TREE_OPERAND(op, 1)));
      json_int_field("offset", TREE_INT_CST_LOW(TREE_OPERAND(op, 2)));
      break;
	    
    case COMPOUND_LITERAL_EXPR:
      json_field("decl");
      dump_op(COMPOUND_LITERAL_EXPR_DECL(op));
      break;  
    
    case POINTER_PLUS_EXPR:
      json_field("pointer");
      dump_op(TREE_OPERAND(op, 0));
      json_field("offset");
      dump_op(TREE_OPERAND(op, 1));
      break;
    
    case OBJ_TYPE_REF:
      json_field("expr");
      dump_op(OBJ_TYPE_REF_EXPR(op));
      json_field("object");
      dump_op(OBJ_TYPE_REF_OBJECT(op));
      json_field("token");
      dump_op(OBJ_TYPE_REF_TOKEN(op));
      break;
    }
    
    json_end_object();
  } else {
    json_null();
  }
  TRACE("dump_op: exiting\n");
}

static void dump_ops(gimple *stmt) {
  int numops = gimple_num_ops(stmt);
  if(numops > 0) {
    json_array_field("operands");
    int i;
    for(i=0;i<numops;++i) {
      tree op = gimple_op(stmt, i);
      if(op) {
        dump_op(op);
      }
    }
    json_end_array();  
  }
}

static void dump_srcref(gimple *stmt) {
  json_int_field("line", gimple_lineno(stmt));

  if(gimple_filename(stmt)) {
    json_string_field("file", gimple_filename(stmt));
  }
}

static void dump_assignment(gimple *stmt) {
  json_start_object();
  json_string_field("type", "assign");
  dump_srcref(stmt);

  json_string_field("operator", get_tree_code_name(gimple_assign_rhs_code(stmt)));

  json_field("lhs");
  dump_op(gimple_assign_lhs(stmt));

  tree rhs1 = gimple_assign_rhs1(stmt);
  tree rhs2 = gimple_assign_rhs2(stmt);
  tree rhs3 = gimple_assign_rhs3(stmt);
    
  json_array_field("operands");
  if(rhs1) dump_op(rhs1);
  if(rhs2) dump_op(rhs2);
  if(rhs3) dump_op(rhs3);
  json_end_array();
  json_end_object();
}

static void dump_cond(basic_block bb, gimple *stmt) {
  json_start_object();
  json_string_field("type", "conditional");
  dump_srcref(stmt);

  json_string_field("operator", get_tree_code_name(gimple_assign_rhs_code(stmt)));
  
  dump_ops(stmt);
      
  edge true_edge, false_edge;
  extract_true_false_edges_from_block (bb, &true_edge, &false_edge);
  
  json_int_field("trueLabel", true_edge->dest->index);
  json_int_field("falseLabel", false_edge->dest->index);
  json_end_object();
 }

static void dump_nop(gimple *stmt) {
  json_start_object();
  json_string_field("type", "nop");
  dump_srcref(stmt);

  json_end_object();
}

static void dump_predict(gimple *stmt) {
  json_start_object();
  json_string_field("type", "predict");
  dump_srcref(stmt);
  json_int_field("hassub", gimple_has_substatements(stmt));
  // json_string_field("name", predictor_name(gimple_predict_predictor(stmt)));
  json_end_object();
}

static void dump_resx(basic_block bb, gimple *stmt) {
  json_start_object();
  json_string_field("type", "resx");
  dump_srcref(stmt);
  // TODO
  // json_int_field("region", gimple_resx_region(stmt));
    json_int_field("region", 0);
  json_end_object();
}
static void dump_eh_dispatch(gimple *stmt) {
  json_start_object();
  json_string_field("type", "eh_dispatch");
  dump_srcref(stmt);
  // TODO
  // json_int_field("region", gimple_eh_dispatch_region(&stmt));
  json_int_field("region", 0);
  json_end_object();
}

static void dump_label(gimple *stmt) {
  json_start_object();
  json_string_field("type", "label");
  dump_srcref(stmt);
  json_end_object();
}

static void dump_return(gimple *stmt) {
  json_start_object();
  json_string_field("type", "return");
  dump_srcref(stmt);

// TODO
  // greturn * ret = as_a <greturn *> (gsi_stmt (gsi));
  // gimple_build_return
  // tree retval = gimple_return_retval(as_a <greturn *> (stmt));
  // if(retval) {
  //   json_field("value");
  //   dump_op(retval);
  // }
  json_end_object();
}

static void dump_call(gimple *stmt) {
  json_start_object();
  json_string_field("type", "call");
  dump_srcref(stmt);
  
  json_field("lhs");
  dump_op(gimple_call_lhs(stmt));
  
  json_field("function");
  dump_op(gimple_call_fn(stmt));
  
  int numargs = gimple_call_num_args(stmt);
  if(numargs > 0) {
    json_array_field("arguments");
    int i;
    for(i=0;i<numargs;++i) {
      dump_op(gimple_call_arg(stmt,i));
    }
    json_end_array();
  }
  json_end_object();
}

static void dump_switch(gimple *stmt) {

  json_start_object();

  int num_ops = gimple_num_ops(stmt);
  
  json_string_field("type", "switch");
  dump_srcref(stmt);
  
  json_field("value");
  dump_op(gimple_op(stmt, 0));
  
  json_array_field("cases");
  
  int default_case = -1;
  
  int i;
  for(i=1;i<num_ops;++i) {
    tree t = gimple_op(stmt, i);

	  basic_block bb = label_to_block(cfun, CASE_LABEL(t));
    
    if(!CASE_LOW(t)) {
      // this is the default case
      default_case = bb->index;
      
    } else { 
      // proper case
      json_start_object();
      
      json_int_field("low",
        TREE_INT_CST_LOW(CASE_LOW(t)));
    
      if (CASE_HIGH (t)) {
        json_int_field("high",
          TREE_INT_CST_LOW(CASE_HIGH(t)));
	    } else {
        json_int_field("high",
          TREE_INT_CST_LOW(CASE_LOW(t)));	    
	    }
      json_int_field("basicBlockIndex", bb->index);
	    json_end_object();
    } 
  }
  json_end_array();  
  
  json_field("defaultCase");
  json_start_object();
  json_int_field("basicBlockIndex", default_case);
  json_end_object();
  
  json_end_object();

}

static void dump_statement(basic_block bb, gimple *stmt) {
  TRACE("dump_statement: entering\n");
  
  switch(gimple_code(stmt)) {
    case GIMPLE_ASSIGN:
      dump_assignment(stmt);
      break;
    case GIMPLE_CALL:
      dump_call(stmt);
      break;
    case GIMPLE_COND:
      dump_cond(bb, stmt);
      break;
    case GIMPLE_NOP:
     dump_nop(stmt);
      break;
    case GIMPLE_PREDICT: // VAR_DECL
     dump_predict(stmt);
      break;
    case GIMPLE_RESX:
     dump_resx(bb, stmt);
      break;
    case GIMPLE_EH_DISPATCH:
     dump_eh_dispatch(stmt);
      break;
    case GIMPLE_RETURN:
      dump_return(stmt);
      break;
    case GIMPLE_SWITCH: // OFFSET_TYPE
      dump_switch(stmt);
      break;
    case GIMPLE_LABEL: // BLOCK
      // this represents a label expression, usually generated
      // in conjunction with a switch statement. We do the 
      // label to basic block translation there, so we don't need
      // these nodes
    //  dump_label(stmt);
      break;
    default:
      json_start_object();
      json_string_field("type", 
        gimple_code_name[gimple_code(stmt)]);
      dump_ops(stmt);
      json_end_object();
  }
  
  TRACE("dump_statement: exiting\n");
}


static void dump_argument(tree arg) {

  TRACE("dump_argument: entering\n");
  
  json_start_object();
  if(DECL_NAME(arg)) {
    TRACE("dump_argument: dumping name = '%s'\n", IDENTIFIER_POINTER(DECL_NAME(arg)));
    json_string_field("name", IDENTIFIER_POINTER(DECL_NAME(arg)));
  }

  TRACE("dump_argument: dumping id\n");
  json_int_field("id", DEBUG_TEMP_UID (arg));
  
  TRACE("dump_argument: dumping type\n");
  json_field("type");
  dump_type(TREE_TYPE(arg));
  
  json_end_object();
  
  TRACE("dump_argument: exiting\n");

}

static void dump_arguments(tree decl) {
  
  tree arg = DECL_ARGUMENTS(decl);
  
  if(arg) {
    json_array_field("parameters");
    
    while(arg) {
      TRACE("dump_arguments: about to call dump_argument\n");
      dump_argument(arg);
      TRACE("dump_arguments: called dump_argument\n");

      arg = TREE_CHAIN(arg);
    }  
    
    json_end_array();
  }
  
  TRACE("dump_arguments: exiting\n");

}

static void dump_local_decl(tree decl) {

  json_start_object();  
  if(DECL_NAME(decl)) {
    json_string_field("name", IDENTIFIER_POINTER(DECL_NAME(decl)));
  } 

  json_int_field("id", DEBUG_TEMP_UID (decl));
  json_bool_field("static", TREE_STATIC(decl));
  if(TREE_TYPE(decl)) {
    json_field("type");
    dump_type(TREE_TYPE(decl));
  }
  if(DECL_INITIAL(decl)) {
    json_field("value");
    dump_op(DECL_INITIAL(decl));
  }

  json_end_object();
}

static void dump_local_decls(struct function *fun) {
  unsigned ix;
  tree var;

  json_array_field("variableDeclarations");

  FOR_EACH_LOCAL_DECL (fun, ix, var)
    {
      dump_local_decl(var);
    }
	json_end_array();
}

static void dump_basic_block(basic_block bb) {

  json_start_object();
  json_int_field("index", bb->index);
  json_array_field("statements");
      
  gimple_stmt_iterator gsi;
  
  for (gsi = gsi_start_bb (bb); !gsi_end_p (gsi); gsi_next (&gsi))
    {
      dump_statement(bb, gsi_stmt(gsi));
    }
  edge e;
  edge_iterator ei;
  FOR_EACH_EDGE (e, ei, bb->succs)
  {

    if ((e->flags & EDGE_FALLTHRU) && e->dest != bb->next_bb)
    {
      json_start_object();
      json_string_field("type", "goto");
      json_int_field("target", e->dest->index);
      json_end_object();
    }
  }
  json_end_array();

  json_array_field("edges");
  FOR_EACH_EDGE (e, ei, bb->succs)
  {
    json_start_object();
    json_int_field("flags", e->flags);
    json_int_field("source", e->src->index);
    json_int_field("target", e->dest->index);
    json_end_object();
  }
    
  json_end_array();
  json_end_object();
}


static unsigned int dump_function_ast (void)
// static unsigned int dump_function (function *function)
{
  if(errorcount > 0) {
   return 0;
  }

  TRACE("dump_function: pre-entering\n");

  TRACE("dump_function: entering %s\n", IDENTIFIER_POINTER(DECL_NAME(cfun->decl)) );

  
  basic_block bb;
  
  json_start_object();
  json_int_field("id", DEBUG_TEMP_UID (cfun->decl));
  json_string_field("name", IDENTIFIER_POINTER(DECL_NAME(cfun->decl)));
  json_string_field("mangledName", IDENTIFIER_POINTER(DECL_ASSEMBLER_NAME(cfun->decl)));
  json_bool_field("weak", DECL_WEAK(cfun->decl));
  json_bool_field("inline", DECL_DECLARED_INLINE_P(cfun->decl));

  json_bool_field("public", TREE_PUBLIC(cfun->decl));
  
  TRACE("dump_function: dumping arguments...\n");
  dump_arguments(cfun->decl);
  
  TRACE("dump_function: dumping locals...\n");
  dump_local_decls(cfun);
    
  TRACE("dump_function: dumping basic blocks...\n");
  json_array_field("basicBlocks");
  // TODO FOR_EACH_BB_FN
  FOR_ALL_BB_FN (bb, cfun) {
    dump_basic_block(bb);
  }

  json_end_array();
  
  json_field("returnType");
  TRACE("dump_function: dumping return type\n");
  dump_type(TREE_TYPE(DECL_RESULT(cfun->decl)));
  TRACE("dump_function: finished dumping return type\n");
  
  json_end_object();
 
  TRACE("dump_function: exiting %s\n", IDENTIFIER_POINTER(DECL_NAME(cfun->decl)) );
  return 0;
}

static void dump_type_decl (void *event_data, void *data)
{
  TRACE("dump_type: starting...\n");

  tree type = (tree) event_data;

  json_start_object();
  

  if(TYPE_NAME(type)) {

    TRACE("dump_type: name = %s\n",  IDENTIFIER_POINTER (TYPE_NAME (type)));
    json_string_field("name", IDENTIFIER_POINTER (TYPE_NAME (type)));
  }
  
  TRACE("dump_type: type = %s\n",  get_tree_code_name(TREE_CODE (type)));

  
  json_string_field("type", get_tree_code_name(TREE_CODE (type)));
  json_end_object();

  TRACE("dump_type: done\n");

}

static void dump_global_var(tree var) {

  TRACE("dump_global_var: entering\n");

  json_start_object();
  json_int_field("id", DEBUG_TEMP_UID(var));
  if(DECL_NAME(var)) {
    json_string_field("name", IDENTIFIER_POINTER(DECL_NAME(var)));
  }
  if (DECL_ASSEMBLER_NAME_SET_P (var)) {
    json_string_field("mangledName",  IDENTIFIER_POINTER (DECL_ASSEMBLER_NAME (var)));
  }
  json_bool_field("public", TREE_PUBLIC(var));
  json_bool_field("extern", DECL_EXTERNAL(var));

  json_field("type");
  dump_type(TREE_TYPE(var));
  
  json_bool_field("const", DECL_INITIAL(var) && TREE_CONSTANT(DECL_INITIAL(var)));

  if(DECL_INITIAL(var)) {
    json_field("value");
    dump_op(DECL_INITIAL(var));
  }
  json_end_object();
  
  TRACE("dump_global_var: exiting\n");

}

static void dump_global_vars() {

  json_array_field("globalVariables");

// TODO    
  // struct varpool_node *node;
  // for (node = varpool_nodes; node; node = node->next)
  //   {
  //       dump_global_var(node->decl);
  //   }

  json_end_array();
}

static void start_unit_callback (void *gcc_data, void *user_data)
{

  json_start_object();
  json_string_field("mainInputFilename", main_input_filename);
  json_array_field("functions");

}

static void dump_aliases() {

  TRACE("dump_aliases: checking aliases\n");
  json_array_field("aliases");

  struct cgraph_node *n;

  FOR_EACH_DEFINED_FUNCTION(n) {
    if (DECL_ASSEMBLER_NAME_SET_P (n->decl)) {
      if(n->alias && n->thunk.alias) {
          json_start_object();
          json_string_field("alias",  IDENTIFIER_POINTER(DECL_ASSEMBLER_NAME(n->decl)));
          json_string_field("definition",  IDENTIFIER_POINTER(DECL_ASSEMBLER_NAME(n->thunk.alias)));
          json_bool_field("public", TREE_PUBLIC(n->decl));
          json_end_object();
      }
    }
  }

  json_end_array();
}

static void finish_unit_callback (void *gcc_data, void *user_data)
{
  int i;
  json_end_array();

  dump_aliases();
  
  dump_global_vars();

  json_array_field("recordTypes");
  for(i=0;i<record_type_count;++i) {
    dump_record_type_decl(record_types[i]);
  }
  json_end_array();


  json_end_object();
  
  fclose(json_f);
}

namespace {

  const pass_data ast_plugin_data = {
    GIMPLE_PASS,
    "ast_plugin",		 /* name */
    OPTGROUP_NONE,			 /* optinfo_flags */
    TV_NONE,				 /* tv_id */
    PROP_gimple_any,		 /* properties_required */
    0,						 /* properties_provided */
    0,						 /* properties_destroyed */
    0,						 /* todo_flags_start */
    0						 /* todo_flags_finish */
  };

  struct ast_plugin : gimple_opt_pass {
    ast_plugin(gcc::context * ctx) :
      gimple_opt_pass(ast_plugin_data, ctx) {
    }

    virtual unsigned int execute(function * fun) override {
      dump_function_ast();
      return 0;
    }

    virtual ast_plugin *clone() override {
      return this;
    }
  };
}

/* Plugin initialization.  */

int
plugin_init (struct plugin_name_args *plugin_info,
             struct plugin_gcc_version *version)
{
  struct register_pass_info pass_info;

  pass_info.pass = new ast_plugin(g);
  pass_info.reference_pass_name = "cfg";
  pass_info.ref_pass_instance_number = 1;
  pass_info.pos_op = PASS_POS_INSERT_AFTER;
  
  json_f = fopen("/Users/daniel/Documents/dev/research/gcc9.3/plugins/ast.json", "w");


  /* Register this new pass with GCC */
  register_callback (plugin_info->base_name, PLUGIN_PASS_MANAGER_SETUP, NULL, &pass_info);

  //register_callback (plugin_name, PLUGIN_FINISH_TYPE, &dump_type_decl, NULL);
  register_callback ("start_unit", PLUGIN_START_UNIT, &start_unit_callback, NULL);
  register_callback ("finish_unit", PLUGIN_FINISH_UNIT, &finish_unit_callback, NULL);

  
  return 0;
}
