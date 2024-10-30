
# Readme

Convert Mybatis xml to jinja2 template, so that we can use jinja2 template to generate sql.(Influenced by Java development experience)

Just use for study and test, not for production, just for fun.

Currently sql param values will be escaped, like `'` will be `\'`, and value will be display.

# mybatis xml features support

* support for `<sql>` tag
* support for `<include>` tag
* support for `<foreach>` tag
* support for `<trim>` tag
* support for `<if>` tag
* `<where>` tag

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
('SELECT name, category, price FROM fruits WHERE category = ?', ['c12'])
actual params ['2', 123]
('SELECT name, category, price FROM fruits WHERE category = ? AND price > ?', ['2', 123])
.actual params ['123132', 1]
('INSERT INTO notes_label (label_name, parent_id) VALUES (? , ?)', ['123132', 1])
actual params ['123132', 1, 1]
('UPDATE notes_label SET label_name = ? , parent_id = ? WHERE id = ?', ['123132', 1, 1])
actual params [1]
('UPDATE notes_label SET deleted_flag = 0 WHERE id = ?', [1])
actual params [1, 2]
('UPDATE notes_label SET deleted_flag = 0 WHERE id IN (? , ?)', [1, 2])
actual params []
('SELECT count(*) FROM notes_label WHERE deleted_flag = 0', [])
```