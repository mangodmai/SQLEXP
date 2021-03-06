#! /usr/bin/env python
# -*- coding:utf-8 -*-
# author:flystart
# home:www.flystart.org


from lib.core.data import paths,conf,logger
from lib.core.common import put_file_contents
from thirdparty.prettytable.prettytable import PrettyTable
import imp
import inspect
import sys
import urlparse

DUMP_FILE = ""


class Actions():
    def __init__(self,conf):
        self.conf = conf
        try:
            module_name = "{0}_{1}".format(conf.dbms,conf.tech)
            fp, pathname, description = imp.find_module(module_name, [paths.DBS])
            module_obj = imp.load_module("_", fp, pathname, description)
            data_name = getattr(module_obj, conf.dbms.capitalize())
            a= conf.tech
            self.dbms = data_name(a)
            # self.dbms = data_name(conf.tech)
        except Exception,e:
            logger.error(e.message)
            sys.exit(0)

    def do(self,method,*args):
        method = getattr(self.dbms,method)
        ret = method(*args)
        return ret

    def get_current_user(self):
        fun = inspect.stack()[0][3]
        user = self.do(fun)
        info = "CurrentUser is:"+user
        logger.success(info)
        put_file_contents(DUMP_FILE, info)
        return

    def get_current_db(self):
        fun =  inspect.stack()[0][3]
        db = self.do(fun)
        info = "CurrentDb is:"+db
        logger.success(info)
        put_file_contents(DUMP_FILE, info)
        return


    def get_dbs(self):
        fun = inspect.stack()[0][3]
        dbs = self.do(fun)
        out = PrettyTable()
        out.add_column("DATABASE:",dbs)
        logger.info(out)
        put_file_contents(DUMP_FILE,str(out))
        return

    def get_tables(self):
        fun = inspect.stack()[0][3]
        dbs = conf.dbs
        tables = []
        for db in dbs:
            tables = self.do(fun,db)
            logger.success(db)
            out = PrettyTable()
            out.add_column("TABLES:", tables)
            logger.info(out)
            put_file_contents(DUMP_FILE, "db:{0}".format(db))
            put_file_contents(DUMP_FILE, str(out))
        return

    def get_columns(self):
        fun = inspect.stack()[0][3]
        db  = conf.dbs[0]
        tables = conf.table
        for table in tables:
            cols = self.do(fun,db,table)
            out = PrettyTable()
            out.add_column(table, cols)
            logger.info(out)
            put_file_contents(DUMP_FILE, "table:{0}.{1}".format(db,table))
            put_file_contents(DUMP_FILE, str(out))
        return

    def dump(self):
        fun = inspect.stack()[0][3]
        dbs = conf.dbs
        tables = conf.table
        cols = conf.columns
        '''
        if (len(dbs) > 1 and len(tables)>0) or (len(tables)>1 and len(cols>0)):
            logger.info("Please -D db -T table -C col --dump")
        '''
        for db in dbs:
            if not tables:
                tables = self.do("get_tables",db)
            logger.info(tables)
            for table in tables:
                if (not conf.table and not conf.columns) or (conf.table and not conf.columns):
                    cols = self.do("get_columns",db,table)
                logger.info(cols)
                out = PrettyTable()
                info = "{0}.{1}\n".format(db, table)
                logger.info(info)
                put_file_contents(DUMP_FILE, info)
                for col in cols:
                    values = self.do(fun,db,table,col)
                    out.add_column(col,values)
                    logger.info(out)
                put_file_contents(DUMP_FILE, str(out))
        return


def action():
    global DUMP_FILE
    target = urlparse.urlparse(conf.url).netloc
    DUMP_FILE = r"{0}/{1}".format(paths.DUMP_PATH, target+".txt")
    act = Actions(conf)
    if conf.getCurrentUser:
        logger.info("get current_user")
        act.get_current_user()

    if conf.getCurrentDb:
        logger.info("get current_db")
        act.get_current_db()
    if conf.getDbs:
        logger.info("list all databases")
        act.get_dbs()
    if conf.getTables:
        logger.info("list tables")
        act.get_tables()
    if conf.getColumns:
        logger.info("list columns")
        act.get_columns()
    if conf.dumpTable:
        act.dump()