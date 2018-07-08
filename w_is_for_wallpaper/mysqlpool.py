"""
(c) Pavel Gurkov aka trueneu, 2016, All Rights Reserved

All direct communications with MySQL are done here
"""

import logging
import datetime
from mysql.connector import pooling, PoolError, DatabaseError, DataError, ProgrammingError
from w_is_for_wallpaper import mysql_helpers
from w_is_for_wallpaper import history

class MysqlPoolException(Exception):
    pass


class MysqlExecuteException(Exception):
    pass


class MysqlPool:
    def __init__(self, pool_name=None, pool_size=1, database='test', user='test', password='test',
                 host='127.0.0.1', port=3306):
        if pool_name:   # a duck typing hack that allows us to create the object before we actually get
                        # any connection up
            try:
                self._pool = pooling.MySQLConnectionPool(pool_name=pool_name,
                                                         pool_size=pool_size,
                                                         pool_reset_session=True,
                                                         database=database,
                                                         user=user,
                                                         password=password,
                                                         host=host,
                                                         port=port)
            except (PoolError, DatabaseError) as e:
                msg = "Couldn't create MySQL pool %s: %s" % (pool_name, str(e))
                logging.critical(msg)
                raise MysqlPoolException(msg)

    def _execute_queries(self, queries, one_row=False, fetch_lastrowid=False):
        """

        :param queries: list of queries to execute
        :param one_row: fetching just one row or multiple rows
        :param fetch_lastrowid: True if we want to fetch last row id inserted
        :return: selected info if query is select. lastrowid if it's insert and fetch_lastrowid == True
        """

        logging.debug('executing queries: "{queries}" in pool {pool}'.format(queries=queries,
                                                                             pool=self._pool.pool_name))
        try:
            cnx = self._pool.get_connection()
            result = []
            for query in queries:
                crs = cnx.cursor(dictionary=True)
                try:
                    crs.execute(query)
                    res = crs.fetchone() if one_row else crs.fetchall()
                    if fetch_lastrowid:
                        res = (res, crs.lastrowid)
                except DatabaseError as e:
                    msg = "Couldn't execute query %s: %s" % (query, str(e))
                    logging.error(msg)
                    raise MysqlExecuteException(msg)
                finally:
                    crs.close()
                result.append(res)
            cnx.commit()

        except PoolError as e:
            msg = "Couldn't execute queries %s: %s" % (queries, str(e))
            logging.error(msg)
            raise MysqlExecuteException(msg)

        finally:
            cnx.close()
        return result

    def set_pool_config(self, **config):
        self._pool.set_config(**config)

    def generic_select(self, table, columns, where=None, order_by=None, multiple_rows=False,
                       start=None, amount=1000):
        """
        A generic select
        :param columns: list of columns to select
        :param table: table to select from
        :param where: a dict to be inserted in 'where' clause, {field: value, ...}, None if there's no where
        :param order_by: a dict in form {'column': 'order'}
        :param multiple_rows: False if only one row wanted, True if many.
        :param start: SQL limit's first arg
        :param amount: SQL limit's second arg
        :return: dict or list of dicts (if multiple_rows): {column: field, ...}
        """
        query = 'select {columns} from {table}'.format(columns=', '.join(columns), table=table)
        query = mysql_helpers.additions(query, where, order_by, start, amount)

        return (self._execute_queries([query], one_row=True)[0] if not multiple_rows
                else self._execute_queries([query])[0])

    def generic_select_left_join(self, tables, columns, joins, where=None, order_by=None, multiple_rows=False,
                                 start=None, amount=1000):
        """
        :param tables: list of tables to take part in resulting query
                       in form [(table0, alias0), (table1, alias1), ...]
        :param columns: list of lists of columns to be selected in form
                       [[column0_table0, column1_table0],
                        [column0_table1, column1_table1],
                        ...
                        ]
        :param joins: list of joins in form
                      [((tableX_id, column), sign_str, (tableY_id, column)),
                       ((tableW_id, column), sign_str, (tableZ_id, column)),
                       ...
                       ]
        :param where: a dict to be inserted in 'where' clause, {field: value, ...}, None if there's no where
        :param order_by: a dict in form {'column': 'order'}
        :param multiple_rows: False if only one row wanted, True if many.
        :param start: SQL limit's first arg
        :param amount: SQL limit's second arg
        :return: dict or list of dicts (if multiple_rows): {column: field, ...}
        """
        query = mysql_helpers.form_query_select_left_join(tables, columns, joins)
        query = mysql_helpers.additions(query, where, order_by, start, amount)

        return (self._execute_queries([query], one_row=True)[0] if not multiple_rows
                else self._execute_queries([query])[0])

    def generic_insert(self, table, data, fetch_lastrowid=False, write_history=True):
        # when inserting a lot of rows, fetch the last inserted rowid, not the first
        # think about it. Though it's how the Oracle driver works
        if write_history:
            try:
                id_before = self.generic_select(table, ['id'], order_by={'id': 'desc'}, amount=1)['id']
            except TypeError:
                id_before = None

        columns = []
        values = []
        queries = []
        for k, v in data.items():
            columns.append('`{k}`'.format(k=k))
            values_list = []
            if isinstance(v, list):
                for item in v:
                    if isinstance(item, str):
                        s = "'{item}'".format(item=item)
                    elif isinstance(item, datetime.datetime):
                        s = "'{item}'".format(item=item.strftime("%Y-%m-%dT%H:%M:%S"))
                    else:
                        s = "{item}".format(item=item)
                    values_list.append(s)
            else:
                item = v
                if isinstance(item, str):
                    s = "'{item}'".format(item=item)
                elif isinstance(item, datetime.datetime):
                    s = "'{item}'".format(item=item.strftime("%Y-%m-%dT%H:%M:%S"))
                else:
                    s = "{item}".format(item=item)
                values_list.append(s)
            values.append(values_list)
        values_zipped = list(zip(*values))
        values_string = ", ".join(["({v_group})".format(v_group=", ".join([x for x in v_group]))
                                   for v_group in values_zipped])
        queries.append('insert into `{table}` ({columns}) values {values}'.format(
            table=table,
            columns=', '.join(columns),
            values=values_string
        ))
        result = self._execute_queries(queries, one_row=True, fetch_lastrowid=fetch_lastrowid)[0]

        if write_history:
            id_after = self.generic_select(table, ['id'], order_by={'id': 'desc'}, amount=1)['id']
            ids = list(range(id_before + 1 if id_before else 1, id_after + 1))
            self.write_history(ids, history.EventTypes.create, table)

        return result

    def delete_by_ids(self, table, ids, id_column='id', write_history=True):
        where = {id_column: {'values': ids}}
        result = self.generic_delete(table, where)
        if write_history:
            self.write_history(ids, history.EventTypes.delete, table)
        return result

    def generic_delete(self, table, where=None, order_by=None, amount=1000):
        queries = []
        query = 'DELETE FROM {table}'.format(table=table)
        query = mysql_helpers.additions(query, where, order_by, None, amount)
        queries.append(query)
        result = self._execute_queries(queries, one_row=True, fetch_lastrowid=False)
        return result

    def update_by_id(self, table, data, entry_id, id_column='id', write_history=True, smart_substitution=True):
        columns = []
        values = []
        queries = []
        for k, v in data.items():
            columns.append('`{k}`'.format(k=k))
            item = v
            if smart_substitution:
                if isinstance(item, str):
                    s = "'{item}'".format(item=item)
                elif isinstance(item, datetime.datetime):
                    s = "'{item}'".format(item=item.strftime("%Y-%m-%dT%H:%M:%S"))
                elif v is None:
                    s = 'NULL'
                else:
                    s = "{item}".format(item=item)
            else:
                s = "{item}".format(item=item)
            values.append(s)

        where = {id_column: {'values': entry_id}}
        zipped_values_columns = list(zip(columns, values))
        query = 'UPDATE {table} SET {cv}'.format(table=table, cv=','.join(
            ['='.join(x) for x in zipped_values_columns])
                                                 )
        query = mysql_helpers.additions(query, where, None, None, 1000)
        queries.append(query)
        result = self._execute_queries(queries, one_row=True, fetch_lastrowid=False)
        if write_history:
            self.write_history([entry_id], history.EventTypes.modify, table)
        return result

    def write_history(self, ids, event, table):
        try:
            data = mysql_helpers.form_query_history_data(ids, event, table)
        except mysql_helpers.MysqlHelperException as e:
            logging.error("Couldn't write history: %s" % str(e))
            return
        self.generic_insert('history', data, write_history=False)


