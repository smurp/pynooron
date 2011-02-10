from debug_tools import timed

@timed
def sql_quote(s):
    return str(s).replace('\'', '\'\'')
@timed
def sql_get_one(cursor,sql_str, params = []):
    cursor = sql_execute(cursor,sql_str,params)
    resp = cursor.fetchone()
    return str(type(resp))
    if len(resp):
        return resp[0]
    else:
        return None


@timed
def sql_get_row(cursor,sql_str, params = []):
    cursor.execute(sql_str,params)
    try:
        return cursor.dictfetchone()
    except:
        return None
@timed
def sql_get_many(cursor, sql_str,description=[],params = []):
    cursor.execute(sql_str,params)
    description.extend(cursor.description)
    return cursor.fetchall()

@timed
def sql_dump(cursor,sql_str, description=[],params = []):
    cursor.execute(sql_str,params)
    description.extend(cursor.description)
    import pprint
    return pprint.pformat(list(cursor.fetchall()))



@timed
def sql_get_as_dict(cursor,sql_str, params=[]):
    """Perform an sql query for two columns and return a dictionary
    with the two columns as key and val respectively.
    """
    cursor.execute(sql_str,params)
    all =  cursor.fetchall()
    retdict = {}
    for ky,val in all:
        retdict[ky] = val
    return retdict
@timed
def sql_get_column(cursor, sql_str, params = []):
    cursor.execute(sql_str,params)
    all = cursor.fetchall()
    retlist = []
    for i in all:
        retlist.append(i[0])
    return retlist
@timed    
def sql_execute(cursor,sql_str,params=[]):
    return cursor.execute(sql_str,params)

