
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

> change `inner template` path to your mybatis xml directory first!