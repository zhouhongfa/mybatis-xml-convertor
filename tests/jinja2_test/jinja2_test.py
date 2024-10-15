import unittest
from jinja2 import Environment, PackageLoader, select_autoescape, DictLoader, FunctionLoader, FileSystemLoader, ModuleLoader


def fun1(name, *args):
    if name == "fun1":
        return "hello world"
    return "hello"


class Test(unittest.TestCase):
    def _test_dict_loader(self):
        env = Environment(
            loader=DictLoader({'index': '{{the}} source {{go}}'}),
            autoescape=select_autoescape()
        )
        template = env.get_template("index")
        print(template.render(the="variables", go="here"))

    def _test_function_loader(self):
        env = Environment(
            loader=FunctionLoader(fun1),
            autoescape=select_autoescape()
        )
        template = env.get_template("fun1")
        self.assertEqual(template.render(arg1=1), "hello world")

    def test_file_loader(self):
        env = Environment(
            loader=FileSystemLoader(
                "/Volumes/SSDExt/data/programming/gitRepos/bb-lott-tool/tests/common/jinja2_test"),
            autoescape=select_autoescape()
        )
        t = env.get_template("test.template")
        arg = {
            'id': 1
        }
        # print(t.module.__dict__)
        # print(getattr(t.module, "test1")(arg))
        # print(getattr(t.module, "test2")(arg))
        # print(getattr(t.module, "trim_fun")('test1, test2,','(',')', ','))
        print(getattr(t.module, "testForeach")({}))
        # print(t.module.test2(arg))

    def _test_call(self):
        env = Environment(
            loader=DictLoader({'test': '''
{% macro  testForeach1(arg)  %} \n\n        


SELECT\n        name,\n        category,\n        price\n        FROM fruits\n        \nwhere 1=1 and\n


{%  for name in arg.collection  %} \n\n

{% if loop.first %}\n (\n{% endif %}\n\n 


{% if not loop.last %} \nOR\n {% endif %} \n\n 


{% if loop.last %} \n )\n{% endif %} \n 


{% endfor %} \n        \n    \n 


{% endmacro %}



 {% macro  testForeach(arg)  %} 
 select name from test where name in 

    {% for item in arg.collection %}
{% if loop.first %}
(
{% endif %}
        
name =  {{ item.name }}

    {% if item == 1 %}
    123
    {% endif%}
       
{% if not loop.last %}
or
{% endif %}

{% raw %}
{% if loop.last %}
    )
{% endif %}
{% endraw %}

    {% endfor %}

 {% endmacro %} 
                               '''}),
            autoescape=select_autoescape()
        )
        template = env.get_template("test")
        # print(template.module.testInclude({'category': 'test'}))
        # print(template.module.testForeach({'collection': [{'name': 'Mary'}, {'name': 'Mary2'}, {'name': 'Mary3'}]}))
        print(template.module.testForeach1({'collection': [{'name': 'Mary'}, {'name': 'Mary2'}, {'name': 'Mary3'}]}))


if __name__ == "__main__":
    unittest.main()
