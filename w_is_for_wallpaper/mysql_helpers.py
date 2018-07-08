from datetime import datetime
from w_is_for_wallpaper import history


class MysqlHelperException(Exception):
    pass


def form_query_select_left_join(tables, columns, joins):
    """
    Formed queries' column and table names are always aliased!

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
    :return: query string
    """

    select_columns = []
    for i, columns_per_table in enumerate(columns):
        for column in columns_per_table:
            select_columns.append("{table}.{column} as {alias}".format(table=tables[i][1],
                                                                       column=column,
                                                                       alias="{table}_{column}".format(
                                                                           table=tables[i][1],
                                                                           column=column
                                                                       )
                                                                       ))
    select_columns_string = ", ".join(select_columns)
    from_table_name, from_table_alias = tables[0][0], tables[0][1]

    join_rules = []
    for join in joins:
        (table_left_id, column_left), sign, (table_right_id, column_right) = join
        join_rules.append("{table_left_full} as {table_left_alias} on "
                          "{table_left_alias}.{column_left} {sign} "
                          "{table_right_alias}.{column_right}".format(
                            table_left_full=tables[table_left_id][0],
                            table_left_alias=tables[table_left_id][1],
                            table_right_full=tables[table_right_id][0],
                            table_right_alias=tables[table_right_id][1],
                            sign=sign,
                            column_left=column_left,
                            column_right=column_right
                                                                     ))
    join_rules_str = " left join ".join(join_rules)
    result = "select {columns} from {table} as {alias} left join {joins}".format(
        columns=select_columns_string,
        table=from_table_name,
        alias=from_table_alias,
        joins=join_rules_str
    )
    return result


def add_where(query, where):
    if where:
        condition_parts = []
        for k, v in where.items():
            if not ('values' in v):
                raise MysqlHelperException('Where helper: you must supply "values" field.')
            values = v['values']
            operator = v.get('operator', '=')
            if operator == '=' and isinstance(values, list):
                condition_parts.append('{k} in ({values})'.format(k=k, values=', '.join(map(str, values))))
            else:
                if isinstance(values, datetime):
                    condition_parts.append("{k} {o} '{v}'".format(k=k, o=operator,
                                                                  v=values.strftime("%Y-%m-%dT%H:%M:%S.%f")))
                elif isinstance(values, str) and not (values.startswith('%') and values.endswith('%')):
                    condition_parts.append("{k} {o} '{v}'".format(k=k, o=operator, v=values))
                elif isinstance(values, str):
                    condition_parts.append('{k} {o} {v}'.format(k=k, o=operator, v=values.replace('%', '')))
                else:
                    condition_parts.append('{k} {o} {v}'.format(k=k, o=operator, v=values))
        condition = ' AND '.join(condition_parts)
        return '{query} where {condition}'.format(query=query, condition=condition)
    else:
        return query


def add_order_by(query, order_by):
    if order_by:
        order_by_parts = ["{k} {v}".format(k=k, v=v) for k, v in order_by.items()]
        return '{query} order by {order}'.format(
            query=query, order=', '.join(order_by_parts))
    else:
        return query


def add_limit(query, start, amount):
    if start:
        addition = "limit {start}, {amount}".format(start=start, amount=amount)
    else:
        addition = "limit {amount}".format(amount=amount)

    return "{query} {addition}".format(query=query, addition=addition)


def additions(query, where, order_by, start, amount):
    result = add_where(query, where)
    result = add_order_by(result, order_by)
    result = add_limit(result, start, amount)
    return result


def form_query_history_data(entity_ids, event_type, table):
    """
    A helper function to form data to be used in INSERT query to 'history' table.

    :param entity_ids: entity ids to be written
    :param event_type: event type (see history.py)
    :param table: table that was modified
    :return: data to use in generic_insert method of mysqlpool.py
    """
    result = {}
    try:
        entity_type = history.table_entity_mapping[table]
    except KeyError:
        raise MysqlHelperException("Couldn't form history data. Unknown event type "
                                   "'{ev_type}' or entity type for table '{table}'".format(
                                    ev_type=event_type, table=table
                                   ))

    dt = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')

    count = len(entity_ids)
    result['event_type'] = [event_type.value] * count
    result['entity_type'] = [entity_type.value] * count
    result['entity_id'] = entity_ids
    result['date'] = [dt] * count
    return result

