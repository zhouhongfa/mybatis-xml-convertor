
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

```
("SELECT name, category, price FROM fruits WHERE category = 'apple' AND name IN (:param_0 , :param_1 , :param_2) AND (name = 'other_name')", {'param_0': 'apple1', 'param_1': 'apple2', 'param_2': 'apple3'})
("SELECT name, category, price FROM fruits WHERE category = 'apple' AND category = :param_0 AND name IN (:param_1 , :param_2 , :param_3) AND ()", {'param_0': 'category_1234', 'param_1': 'apple1', 'param_2': 'apple2', 'param_3': 'apple3'})
("SELECT name, category, price FROM fruits WHERE category = 'apple' AND when113 = :param_0", {'param_0': 2})
("SELECT name, category, price FROM fruits WHERE category = 'apple' AND when112 = :param_0", {'param_0': 1})
("SELECT name, category, price FROM fruits WHERE category = 'apple' AND when113 = :param_0", {'param_0': Undefined})
.('SELECT name, category, price FROM WHERE category = :param_0', {'param_0': '12'})
.('SELECT * FROM table1 WHERE 1=1 AND deleted_flag = 0 AND other_col = 0 ORDER BY id DESC', {})
('SELECT * FROM table1 WHERE 1=1 AND deleted_flag = 0 AND price = :param_0 AND other_col = 0 ORDER BY id DESC', {'param_0': 123})
('SELECT * FROM table1 WHERE 1=1 AND deleted_flag = 0 AND price = :param_0 AND other_col = 0 ORDER BY id DESC', {'param_0': "123' or (1=1) or 1='1"})
('SELECT name, category, price FROM fruits WHERE category = :param_0', {'param_0': 'c12'})
('SELECT name, category, price FROM fruits WHERE category = :param_0 AND price > :param_1', {'param_0': '2', 'param_1': 123})
.('INSERT INTO notes_label (label_name, parent_id) VALUES (:param_0 , :param_1)', {'param_0': '123132', 'param_1': 1})
('UPDATE notes_label SET label_name = :param_0 , parent_id = :param_1 WHERE id = :param_2', {'param_0': '123132', 'param_1': 1, 'param_2': 1})
('UPDATE notes_label SET deleted_flag = 0 WHERE id = :param_0', {'param_0': 1})
('UPDATE notes_label SET deleted_flag = 0 WHERE id IN (:param_0 , :param_1)', {'param_0': 1, 'param_1': 2})
('SELECT count(*) FROM notes_label WHERE deleted_flag = 0', {})
```