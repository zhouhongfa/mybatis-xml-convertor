from jinja2 import Environment, select_autoescape, DictLoader
import os
from xml.etree.ElementTree import parse as xml_parse
from xml.etree.ElementTree import Element
import regex
import sqlparse
from .enum import StrEnum

class XmlConstants(StrEnum):
    XML_EXT = ".xml"
    NAMESPACE = "namespace"
    MAPPER = "mapper"
    ID = "id"
    SQL_MAIN = "sql_main"
    WHERE_CLAUSE = "where_clause"
    TEST = "test"
    IF = "if"
    ELSE_IF = "elif"
    ELSE = "else"
    FOR = "for"
    WHERE = "where"
    CHOOSE = "choose"
    WHEN = "when"
    OTHERWISE = "otherwise"
    FOREACH = "foreach"
    INCLUDE = "include"
    TRIM = "trim"


class RegexConstants(StrEnum):
    ARG_VAR = r'{{ arg.\1 }}'
    ARG_IF_VAR = r"{% if arg.\1 is number %}{{arg.\1}}{% else %}{{quote_str(arg.\1)}}{% endif %}"
    ARG_VAR2 = r'{{ \1 }}'
    ARG_VAR3 = r"{% if \1 is number %}{{\1}}{% else %}{{quote_str(\1)}}{% endif %}"
    ARG_CONDITION = r'arg.\1'


variable_re = regex.compile(r'^([\w.]+)')
var_replace_re1 = regex.compile(r'\$\{([\w]+)\}')
var_replace_re2 = regex.compile(r'\#\{(\w+)\}')
var_replace_re3 = regex.compile(r'\$\{([\w]+)\}')
var_replace_re4 = regex.compile(r'\#\{([\w.]+)\}')
null_re = regex.compile(r'null', flags=regex.IGNORECASE)


class MybatisXmlUtil:
    mybatis_section = None
    if_fun_section = None
    import_fun = None
    for_fun = None
    for_sub = None
    for_if_fun = None
    trim_section_fun = None
    if_elif_else_fun = None
    nested_macro = '''
    {% macro quote_str(arg) %}'{{arg|replace("'", "''")}}'{% endmacro %}

    {% macro trim_fun(arg, prefix, suffix, trim_text) %}
    {{prefix}}
    {{arg|trim(trim_text)}}
    {{suffix}}
    {% endmacro %}
    
    {% macro raw_temp(arg) %}
    {{arg}}
    {% endmacro %}
    '''

    def render(self, namespace, xml_id: str, args: dict = None):
        res_sql = getattr(self.jinja_env.get_template(namespace).module, xml_id)(args)
        return sqlparse.format(res_sql, strip_whitespace=True, keyword_case='upper')

    def check_mapper(self, namespace, id):
        # FIXME should check ?
        return True
        # return id in self.jinja_env.get_template(namespace).module.__dict__
    
    # def _prepare_template(self):
    #     """
    #     prepare template, load all template once if necessary
    #     """
    #     for id in self.converted_dict.keys():
    #         self.jinja_env.get_template(id)

    def _cache_mapper(self, template_path):
        mapper_xmls = []
        for path in template_path:
            for root, dirs, files in os.walk(path):
                for basename in files:
                    file_path = os.path.join(root, basename)
                    if basename.endswith(XmlConstants.XML_EXT.value):
                        mapper_xmls.append(file_path)

        converted_dict = dict(self.mapper_convert(mapper_xmls))
        self.jinja_env = Environment(
            loader=DictLoader(converted_dict),
            autoescape=select_autoescape()
        )
    def mapper_convert(self, file_paths:list[str]):
        """
        convert xml to jinja2 template string
        """
        for file_path in file_paths:
            all_template_array = []
            # append nested fun
            all_template_array.append(self.nested_macro)
            mybatis_info_dict = dict()
            tree = xml_parse(file_path)
            root = tree.getroot()
            if root.tag is not None and root.tag.lower() != XmlConstants.MAPPER.value:
                return
            # should be unique
            rid = root.attrib[XmlConstants.NAMESPACE.value]
            if rid is None:
                raise Exception("namespace is required")
            for child in root:
                # print(child.tag, child.attrib)
                cid = child.attrib[XmlConstants.ID.value]
                text = child.text
                # converted_dict['id'] = cid

                text = self._replace_variable(text)

                mybatis_info_dict[XmlConstants.ID.value] = cid
                mybatis_info_dict[XmlConstants.SQL_MAIN.value] = text
                mybatis_info_dict[XmlConstants.WHERE_CLAUSE.value] = self._convert_sub(
                    child)

                jinja_template = self.mybatis_section(
                    mybatis_info_dict)

                all_template_array.append(jinja_template)
            yield rid, ''.join(all_template_array)

    def _convert_sub(self, child: Element) -> str:
        arr = []
        for sub in child:
            if sub.tag.lower() == XmlConstants.IF.value:
                text = sub.attrib[XmlConstants.TEST.value]
                variable = variable_re.findall(text.strip())[0]
                text = self._condition_replace(
                    sub.attrib[XmlConstants.TEST.value], variable)
                # find variable commonly is the first word
                text = self._replace_variable(text)
                obj = {'condition': text,
                       'condition_variable': variable,
                       'condition_text': self._replace_variable(sub.text)}
                arr.append(self.if_fun_section(obj))
            elif sub.tag.lower() == XmlConstants.INCLUDE.value:
                refid = sub.attrib['refid']
                obj = {
                    'import_fun': refid
                }
                arr.append(self.import_fun(obj))
            elif sub.tag.lower() == XmlConstants.WHERE.value:
                # FIXME append and or not, need to check sub tag
                arr.append('where 1=1')
                if sub.text is not None and len(sub.text.strip()) > 0:
                    arr.append(self._replace_variable(sub.text))
                arr.append(self._convert_sub(sub))
            elif sub.tag.lower() == XmlConstants.FOREACH.value:
                obj = {
                    'item': sub.attrib['item'],
                    'collection': sub.attrib['collection'],
                    'open': self._attrib_get(sub, 'open'),
                    'close': self._attrib_get(sub, 'close'),
                    'separator': self._attrib_get(sub, 'separator'),
                }
                sub_clause = self._convert_for_sub(sub, obj)
                obj['sub_clause'] = sub_clause
                arr.append(self.for_fun(obj))
            elif sub.tag.lower() == XmlConstants.TRIM.value:
                obj = {
                    'type': XmlConstants.TRIM.value,
                    'prefix': self._attrib_get(sub, 'prefix'),
                    'suffix': self._attrib_get(sub, 'suffix'),
                    'trim_text': self._attrib_get(sub, 'suffixOverrides'),
                }
                obj['trim_body'] = self._convert_sub(sub)
                if sub.text is not None:
                    obj['trim_body'] = sub.text + obj['trim_body']
                arr.append(self.trim_section_fun(obj))
            elif sub.tag.lower() == XmlConstants.CHOOSE.value:
                arr.append(self._convert_choose_to_if_else(sub))
            if sub.tail is not None and len(sub.tail.strip()) > 0:
                arr.append(self._replace_variable(sub.tail))
        return ''.join(arr)

    def _convert_for_sub(self, child: Element, obj) -> str:
        """
        foreach sub convert
        """
        arr = []
        if child.text is not None and len(child.text.strip()) != 0:
            text = child.text.strip()
            arr.append(self._replace_variable(text, append_arg=False))
        for sub in child:
            if sub.tag.lower() == XmlConstants.IF.value:
                text = sub.attrib[XmlConstants.TEST.value]
                variable = variable_re.findall(text.strip())[0]
                text = self._condition_replace(text, variable)
                obj_if = {'condition': text,
                          'condition_variable': variable,
                          'condition_text': self._replace_variable(sub.text, append_arg=False)}
                arr.append(self.for_if_fun(obj_if))
                if sub.tail is not None:
                    arr.append(self._replace_variable(
                        sub.tail, append_arg=False))
            elif sub.tag.lower() == XmlConstants.CHOOSE.value:
                arr.append(self._convert_choose_to_if_else(
                    sub, in_foreach=True))
        obj['if_clause'] = ''.join(arr)
        return self.for_sub(obj)

    def _convert_choose_to_if_else(self, sub: Element, in_foreach=False) -> str:
        if sub.tag.lower() == XmlConstants.CHOOSE.value:
            when_eles = sub.findall(XmlConstants.WHEN.value)
            t_choose_arr = []
            for when_ele in when_eles:
                when_test = when_ele.attrib[XmlConstants.TEST.value]

                variable = variable_re.findall(when_test.strip())[0]
                condition = self._condition_replace(
                    when_test, variable, append_arg=not in_foreach, check_defined=True)

                condition_text = self._replace_variable(
                    when_ele.text.strip(), append_arg=not in_foreach)
                t_choose_arr.append({
                    'condition': condition,
                    'condition_text': condition_text
                })

            else_text = self._replace_variable(
                sub.find(XmlConstants.OTHERWISE.value).text, append_arg=not in_foreach)
            obj_if_else = {
                'if_elif_funs': t_choose_arr,
                'else_text': else_text.strip(),
            }
            return self.if_elif_else_fun(obj_if_else)

        return ''

    def _condition_replace(self, text: str, variable, append_arg=True, check_defined=False):
        if append_arg and variable:
            text = regex.sub(r'\b('+variable+')', RegexConstants.ARG_CONDITION.value, text)
            if check_defined:
                text = f'arg.{variable} is defined and ({text})'
        if check_defined and not append_arg:
            text = f'{variable} is defined and ({text})'
        return null_re.sub(r'None', text)

    def _replace_variable(self, text: str, append_arg=True) -> str:
        """
        :param text: text
        :param append_arg: if append arg to template
        :return:
        """
        if append_arg:
            text = var_replace_re1.sub(RegexConstants.ARG_VAR.value, text)
            text = var_replace_re2.sub(RegexConstants.ARG_IF_VAR.value, text)
        else:
            text = var_replace_re3.sub(RegexConstants.ARG_VAR2.value, text)
            text = var_replace_re4.sub(RegexConstants.ARG_VAR3.value, text)
        return text

    def _attrib_get(self, sub: Element, attrib: str):
        if attrib in sub.attrib:
            return sub.attrib[attrib]
        return ''
