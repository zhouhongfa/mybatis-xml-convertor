from jinja2 import Environment, select_autoescape, FileSystemLoader
import os
# from flask import Flask
import logging

from mybatis_xml_convertor.mybatis_util import MybatisXmlUtil

logger = logging.getLogger(__name__)

class MybatisManager(MybatisXmlUtil):
    def __init__(self):
        ...
    # Flask usage example 
    # def init_app(self, app: Flask):
    #     basedir = os.path.abspath(os.path.dirname(__file__))
    #     mybatis_inner_env = Environment(
    #         loader=FileSystemLoader(basedir),
    #         autoescape=select_autoescape()
    #     )
    #     inner_template = mybatis_inner_env.get_template('inner_template.jinja')
    #     self.mybatis_section = inner_template.module.macro_fun
    #     self.if_fun_section = inner_template.module.if_fun
    #     self.import_fun = inner_template.module.import_fun
    #     self.for_fun = inner_template.module.for_fun
    #     self.for_sub = inner_template.module.for_sub
    #     self.for_if_fun = inner_template.module.for_if_fun
    #     self.trim_section_fun = inner_template.module.trim_section_fun

    #     self._cache_mapper(app.config['MYBATIS_TEMPLATE_PATH'])
    #     logger.debug('mybatis xml init finished!')