from jinja2 import Environment, PackageLoader, select_autoescape, DictLoader, FunctionLoader, FileSystemLoader
import os
import xml.etree.ElementTree as ET
import re
import sqlparse

# Deprecated

class JinjaSqlTemplateUtil:
    cache = dict()

    def __init__(self, template_path: list[str] = None, default_format='.template'):
        for path in template_path:
            env = Environment(
                loader=FileSystemLoader(path),
                autoescape=select_autoescape(["html", "xml"])
            )
            for file in os.listdir(path):
                if file.endswith(default_format):
                    template = env.get_template(file)
                    for macro in template.module.__dict__:
                        if macro == "_body_stream":
                            continue
                        self.cache[macro] = template

    def render(self, sql_id: str, args: dict = None):
        """
        use macro to split different sql statements
        """
        if sql_id not in self.cache:
            raise Exception("sql id not found")

        return getattr(self.cache[sql_id].module, "test1")(args)


mybatis_inner_env = Environment(
    loader=FileSystemLoader('/Volumes/SSDExt/data/programming/gitRepos/bb-lott-tool/tests/common/jinja2_test'), 
    autoescape=select_autoescape()
)


class XmlConvertUtil:
    cache = dict()

    def __init__(self, template_path: list[str] = None):
        inner_template = mybatis_inner_env.get_template('inner_template.jinja')
        self.mybatis_section = inner_template.module.macro_fun
        self.if_fun_section = inner_template.module.if_fun
        self.import_fun = inner_template.module.import_fun
        self.for_fun = inner_template.module.for_fun
        self.for_sub = inner_template.module.for_sub
        self.if_else_fun = inner_template.module.if_else_fun
        for path in template_path:
            for file in os.listdir(path):
                if file.endswith(".xml"):
                    converted_dict = dict()
                    all_template_array = []
                    mybatis_info_dict = dict()
                    tree = ET.parse(os.path.join(path, file))
                    root = tree.getroot()
                    # should be unique
                    rid = root.attrib['namespace']
                    for child in root:
                        # print(child.tag, child.attrib)
                        cid = child.attrib["id"]
                        text = child.text
                        # converted_dict['id'] = cid

                        text = self._replace_variable(text)

                        mybatis_info_dict['id'] = cid
                        mybatis_info_dict['sql_main'] = text
                        mybatis_info_dict['where_clause'] = self._convert_sub(
                            child)

                        jinja_template = self.mybatis_section(
                            mybatis_info_dict)
                        jinja_template = re.sub(r'\n{2,}', '\n', jinja_template)
                        # change only one \n
                        print(jinja_template)
                        all_template_array.append(jinja_template)
                    converted_dict[rid] = ''.join(all_template_array)

                    jinja_env = Environment(
                        loader=DictLoader(converted_dict),
                        autoescape=select_autoescape()
                    )
                    for id in converted_dict:
                        template = jinja_env.get_template(id)
                        self.cache[id] = template

    def render(self, xml_id: str, args: dict = None):
        if xml_id not in self.cache:
            raise Exception("xml id not found")
        return getattr(self.cache[xml_id].module, "test1")(args)

    def render_mybatis(self, namespace, xml_id: str, args: dict = None):
        if namespace not in self.cache:
            raise Exception(f"{namespace} not found")
        res_sql = getattr(self.cache[namespace].module, xml_id)(args)
        if res_sql is None:
            raise Exception("sql generate error!")
        
        return sqlparse.format(res_sql, strip_whitespace=True, keyword_case='upper')

    def _convert_sub(self, child: ET.Element) -> str:
        arr = []
        for sub in child:
            if sub.text is None:
                continue
            if sub.tag == 'if':
                text = sub.attrib['test']
                # find variable commonly is the first word
                text = re.sub(r'^(\w+)', r' arg.\1 ', text)
                text = re.sub(r'and\s+(\w+)', r'and  arg.\1 ',
                              text, flags=re.IGNORECASE)
                text = re.sub(r'or\s+(\w+)', r'or  arg.\1 ',
                              text, flags=re.IGNORECASE)
                text = text.replace('null', 'None')
                obj = {'condition': text,
                       'condition_text': self._replace_variable(sub.text)}
                arr.append(self.if_fun_section(obj))
            elif sub.tag == 'include':
                refid = sub.attrib['refid']
                obj = {
                    'import_fun': refid
                }
                arr.append(self.import_fun(obj))
            elif sub.tag == 'where':
                #FIXME append and or not, need to check sub tag
                arr.append('where 1=1 and')
                arr.append(self._convert_sub(sub))
            elif sub.tag == 'foreach':
                obj = {
                    'item': sub.attrib['item'],
                    'collection': sub.attrib['collection'],
                    'open': sub.attrib['open'],
                    'close': sub.attrib['close'],
                    'separator': sub.attrib['separator'],
                }
                sub_clause =  self._convert_for_sub(sub, obj)
                obj['sub_clause'] = sub_clause
                arr.append(self.for_fun(obj))
            if sub.tail is not None:
                arr.append(sub.tail)
        return ''.join(arr)
    def _convert_for_sub(self, child: ET.Element, obj) -> str:
        arr = []
        
        for sub in child:
            if sub.text is None:
                continue
            if sub.tag.lower() == 'if':
                text = sub.attrib['test']

                text = text.replace('null', 'None')
                obj_if = {'condition': text,
                       'condition_text': self._replace_variable(sub.text, append_arg=False)}
                arr.append(self.if_fun_section(obj_if))
                if sub.tail is not None:
                    arr.append(self._replace_variable(sub.tail, append_arg=False))
            if sub.tag.lower() == 'choose':
                condition = sub.find('when').attrib['test']
                condition_text = self._replace_variable(sub.find('when').text, append_arg=False)
                else_text = self._replace_variable(sub.find('otherwise').text, append_arg=False)
                obj_if_else = {
                    'condition': condition.strip(),
                    'condition_text': condition_text.strip(),
                    'else_text': else_text.strip()
                }
                arr.append(self.if_else_fun(obj_if_else))
                
        obj['if_clause'] = ''.join(arr)
        return self.for_sub(obj)
    def _replace_variable(self, text: str, append_arg= True) -> str:
        # text = text.replace('null', 'None')
        # != null change to is not defined
        text = re.sub(r'\!\=\s+null', r'is not None', text, flags=re.IGNORECASE)
        if append_arg:
            text = re.sub(r'\$\{([\w]+)\}', r'{{ arg.\1 }}', text)
            text = re.sub(r'\#\{([\w]+)\}', r"'{{ arg.\1 }}'", text)
        else:
            text = re.sub(r'\$\{([\w]+)\}', r'{{ \1 }}', text)
            text = re.sub(r'\#\{([\w.]+)\}', r"'{{ \1 }}'", text)
        return text


# if __name__ == "__main__":
#     paths = ['tests/common/jinja2_test']
#     tmplate = XmlConvertUtil(paths)
#     # print(tmplate.render_mybatis('xxx.testMapper',
#     #       "selectAll", {"tb_name": 'table1', 'price': 123, 'test': 't1'}))
#     print(tmplate.render_mybatis('xxx.testMapper',
#           "testParameters", {"category": 'c12'}))

    # print(tmplate.render_mybatis('xxx.testMapper',
    #       "testInclude", {"category": 'c12', 'price': 1234}))
    # print(tmplate.render_mybatis('xxx.testMapper',
    #       "testForeach", {"apples": ['a  \n  1', 'a2'], 'itemss': [{'name': 123}]}))
