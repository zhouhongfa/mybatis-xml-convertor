from mybatis_xml_convertor.mybatis_util import MybatisXmlUtil
from jinja2 import Environment, select_autoescape, FileSystemLoader
from pathlib import Path
import unittest


class TestMybatisUtil(MybatisXmlUtil):
    def __init__(self, test_path):
        mybatis_ext_path = Path(__file__).parent.parent / \
            'mybatis_xml_convertor' / 'mybatis_ext'
        print(mybatis_ext_path)
        # load inner template
        mybatis_inner_env = Environment(
            loader=FileSystemLoader(mybatis_ext_path.absolute()),
            autoescape=select_autoescape()
        )
        inner_template = mybatis_inner_env.get_template('inner_template.jinja')
        self.mybatis_section = inner_template.module.macro_fun
        self.if_fun_section = inner_template.module.if_fun
        self.import_fun = inner_template.module.import_fun
        self.for_fun = inner_template.module.for_fun
        self.for_sub = inner_template.module.for_sub
        self.for_if_fun = inner_template.module.for_if_fun
        self.trim_section_fun = inner_template.module.trim_section_fun
        self.if_elif_else_fun = inner_template.module.if_elif_else_fun

        self._cache_mapper(test_path)


# xml paths
jinja2_test_path = Path(__file__).parent / 'jinja2_test'
xml_paths = [jinja2_test_path]
# print(xml_paths)
mybatis_manager = TestMybatisUtil(xml_paths)


class Test(unittest.TestCase):
    def test_simple(self):
        print(mybatis_manager.render('xxx.testMapper',
              "selectAll", {"tb_name": 'table1', 'test': 't1'}))
        print(mybatis_manager.render('xxx.testMapper',
              "selectAll", {"tb_name": 'table1', 'test': 't1', 'price': 123}))
        print(mybatis_manager.render('xxx.testMapper',
                                     "selectAll", {"tb_name": 'table1', 'test': 't1', 'price': "123' or (1=1) or 1='1"}))
        print(mybatis_manager.render('xxx.testMapper',
              "testParameters", {"category": 'c12'}))
        print(mybatis_manager.render('xxx.testMapper',
              "testParameters", {"category": '2', "price": 123}))
    def test_include(self):
        print(mybatis_manager.render('xxx.testMapper',
                                     "testInclude", {"category": '12'}))
    def test_sql_simple(self):
        arg = {'label_name': '123132', 'parent_id': 1, 'id': 1}
        print(mybatis_manager.render('xxx.testMapper', "testInsert", arg))
        print(mybatis_manager.render('xxx.testMapper', "testUpdate", arg))
        print(mybatis_manager.render(
            'xxx.testMapper', "deleteById", {'id': 1}))
        print(mybatis_manager.render(
            'xxx.testMapper', "deleteByIds", {'ids': [1, 2]}))
        print(mybatis_manager.render('xxx.testMapper', "count", {}))
    def test_foreach(self):
        arg = {"apples": ['apple1', 'apple2', 'apple3'], 'itemss': [{'name': None}]}
        print(mybatis_manager.render('xxx.testMapper', "testForeach", arg))
        arg = {"apples": ['apple1', 'apple2', 'apple3'], 'itemss': [{'name': 'itemss_1234'}]}
        print(mybatis_manager.render('xxx.testMapper', "testForeach", arg))
        arg = {"apples": ['apple1', 'apple2', 'apple3'], 'category':  'category_1234'}
        print(mybatis_manager.render('xxx.testMapper', "testForeach", arg))
    # def test_foreach2(self):
    #     print(mybatis_manager.render('xxx.testMapper2',
    #         "testForeach", {"name": 2, "name1": 43532}))
    #     print(mybatis_manager.render('xxx.testMapper2',
    #         "testForeach", {"name": 2, "name1": None, "name2": 1}))
    #     print(mybatis_manager.render('xxx.testMapper2',
    #         "testForeach", {"apples": ['a1 and select 1', 'a2'], 'itemss': [{'name': 1, 'name1': 2, }]}))
    #     print(mybatis_manager.render('xxx.testMapper2',
    #         "testForeach", {"apples": ['a1 and select 1', 'a2'], 'itemss': [{'name': 2, 'name2': 3}]}))
    #     print(mybatis_manager.render('xxx.testMapper2',
    #         "testForeach", {"apples": ['a1 and select 1', 'a2'], 'itemss': [{'name': 3, 'name0': 4}]}))
if __name__ == "__main__":
    unittest.main()