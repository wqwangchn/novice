# https://www.jianshu.com/p/0436ea8336db
# http://www.cocoachina.com/articles/87951
#
# eg:
# 魔法脚本路径pwd:
# /home/jumproot/.ipython/profile_default/startup/hive_magic.py


#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/11/22 下午3:56
# @Title   : Jupyter notebook自定义hive读取数据到df的magic方法
# @Link    : https://ipython.readthedocs.io/en/stable/config/custommagics.html


from IPython.core import magic_arguments
from IPython.core.magic import line_magic, cell_magic, Magics, magics_class
from pyhive import hive
import pandas as pd
import subprocess


class HiveEngine2(object):
    hive_config = {
        '22':{
            'host': '172.18.33.22',
            'port': 10000,
        },
        '23': {
            'host': '172.18.33.23',
            'port': 10000,
        },
        '115':{
            'host': '172.18.33.115',
            'port': 10000,
        },
        '58': {
            'host': '172.18.33.58',
            'port': 10000,
        },
        '13': {
            'host': '172.18.33.13',
            'port': 10000,
        },
    }

    def __init__(self,hostname):
        servers_list = self.hive_config.keys()
        assert hostname in servers_list, 'Only servers {} are supported'.format(str(servers_list))
        _config=self.hive_config.get(hostname)
        self.cur = hive.connect(**_config).cursor()


    def execute(self, sql, size=None):
        for isql in sql.split(';'):
            self.cur.execute(isql)
        if size:
            rows = self.cur.fetchmany(size=size)
        else:
            rows = self.cur.fetchall()
        columns = [x[0] for x in self.cur.description]
        return columns, rows


    def close(self):
        self.cur.close()


def _exec_cmd(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    if stdout:
        print(stdout)
    if stderr:
        print(stderr)


@magics_class
class HiveMagic22(Magics):

    def get_df(self, cell, size=None):
        hv = HiveEngine()
        columns, records = hv.execute(cell, size=size)
        hv.close()
        df = pd.DataFrame(records, columns=columns)
        return df


    def check_csv(self, df_cols, table):
        df_check = self.get_df("select * from {} limit 0".format(table))
        return df_cols == df_check.columns.to_list()


    @cell_magic
    @magic_arguments.magic_arguments()
    @magic_arguments.argument("variable", help="the df variable name")
    @magic_arguments.argument("-h", "--head", action="store_true", help="show 5 rows")
    @magic_arguments.argument("-f", "--file", action="store_true", help="absolute path of the file")
    @magic_arguments.argument("-22", "--host22", action="store_true", help="select the 22 server")
    @magic_arguments.argument("-23", "--host23", action="store_true", help="select the 23 server")
    @magic_arguments.argument("-115", "--host115", action="store_true", help="select the 22 server")
    @magic_arguments.argument("-13", "--host13", action="store_true", help="select the 13 server")
    @magic_arguments.argument("-58", "--host58", action="store_true", help="select the 23 server")
    def hive22(self, line="", cell=None):
        args = magic_arguments.parse_argstring(self.hive22, line)
        size = 5 if args.head else None
        file = args.file
        hostname='23'
        if args.host22:
            hostname='22'
        if args.host23:
            hostname='23'
        if args.host115:
            hostname='115'
        if args.host58:
            hostname='58'
        if args.host13:
            hostname='13'
        if file:
            with open(cell.replace('\n','')) as f:
                cell = f.read().strip()
                if cell.endswith(";"):
                    cell = cell[:-1]
        hv = HiveEngine2(hostname)
        columns, records = hv.execute(cell, size=size)
        hv.close()
        df = pd.DataFrame(records, columns=columns)
        self.shell.user_ns[args.variable] = df


    @cell_magic
    @magic_arguments.magic_arguments()
    @magic_arguments.argument("variable", help="the df variable name")
    @magic_arguments.argument("-o", "--overwrite", action="store_true", help="overwrite or not")
    def hive_write22(self, line, cell):
        args = magic_arguments.parse_argstring(self.hive_write22, line)
        variable = args.variable
        overwrite = args.overwrite
        df = self.shell.user_ns[variable]

        cols = df.columns.to_list()
        if overwrite:
            drop_cmd = """hive -e 'drop table {table}'""".format(table=cell)
            create_cmd = """hive -e 'create table {table} ({fields}) row format delimited fields terminated by ",";'""" \
                .format(table=cell, fields=",".join([x + " string" for x in cols]))
            _exec_cmd(drop_cmd); _exec_cmd(create_cmd)

        # if self.check_csv(cols, cell):
        filename = "/home/jumproot/.jupyter/jupyter_ouput_data/{}.csv".format(cell)
        df.to_csv(filename, header=False, index=False, encoding="utf-8")
        write_cmd = """hive -e 'LOAD DATA LOCAL INPATH "{filename}" INTO TABLE {table}';""" \
            .format(filename=filename, table=cell)
        _exec_cmd(write_cmd)
        # else:
        #     print("Columns do not match.")


ip = get_ipython()
ip.register_magics(HiveMagic22)
