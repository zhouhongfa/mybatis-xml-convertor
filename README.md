
# Readme

Convert Mybatis xml to jinja2 template, so that we can use jinja2 template to generate sql.

Just use for study and test.

# mybatis xml features support

* support for `<sql>` tag
* support for `<include>` tag
* support for `<foreach>` tag
* support for `<trim>` tag
* support for `<if>` tag
* support for `<where>` tag

## not support

* `<set>` tag
* `<bind>` tag

# install

```
python3 -m venv .env
source .env/bin/activate
pip install -e .
```

# Test

run test class `tests/mybatis_util_test.py`


# demo output

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Mapper namespace='xxx.testMapper'>

    <select id="testForeach">
        SELECT
        name,
        category,
        price
        FROM fruits
        where category = 'apple'
        <if test="category != null and category !=''">
            and category = #{category}
        </if>
        AND name in
        <foreach collection="apples" item="name" open="(" close=")" separator=",">
            #{name}
        </foreach>
        <trim prefix="AND (" suffix=")" suffixOverrides=",">
            <foreach collection="itemss" item="item" open="" close="" separator="OR">
                <choose>
                    <when test="item.name != null and item.name !=''">
                        name = #{item.name},
                    </when>
                    <otherwise>
                        name = 'other_name',
                    </otherwise>
                </choose>
            </foreach>
        </trim>
    </select>
</Mapper>
```

```python
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


# xml directory
jinja2_test_path = 'jinja2_test'
xml_paths = [jinja2_test_path]
# print(xml_paths)
mybatis_manager = TestMybatisUtil(xml_paths)

def test_foreach(self):
    arg = {"apples": ['apple1', 'apple2', 'apple3'], 'itemss': [{'name': None}]}
    print(mybatis_manager.render('xxx.testMapper', "testForeach", arg))
    arg = {"apples": ['apple1', 'apple2', 'apple3'], 'itemss': [{'name': 'itemss_1234'}]}
    print(mybatis_manager.render('xxx.testMapper', "testForeach", arg))
    arg = {"apples": ['apple1', 'apple2', 'apple3'], 'category':  'category_1234'}
    print(mybatis_manager.render('xxx.testMapper', "testForeach", arg))
```

output as follow:

```
("SELECT name, category, price FROM fruits WHERE category = 'apple' AND name IN (:param_0 , :param_1 , :param_2) AND (name = 'other_name')", {'param_0': 'apple1', 'param_1': 'apple2', 'param_2': 'apple3'})
("SELECT name, category, price FROM fruits WHERE category = 'apple' AND name IN (:param_0 , :param_1 , :param_2) AND (name = :param_3)", {'param_0': 'apple1', 'param_1': 'apple2', 'param_2': 'apple3', 'param_3': 'itemss_1234'})
("SELECT name, category, price FROM fruits WHERE category = 'apple' AND category = :param_0 AND name IN (:param_1 , :param_2 , :param_3)", {'param_0': 'category_1234', 'param_1': 'apple1', 'param_2': 'apple2', 'param_3': 'apple3'})
```