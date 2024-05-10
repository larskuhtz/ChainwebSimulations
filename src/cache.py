from functools import wraps
import gzip
import pickle
import sqlite3

# ############################################################################ #

def to_pickle(path, d):
    # with gzip.open(path, 'wb') as handle:
    with open(path, 'wb') as handle:
        pickle.dump(d, handle, protocol=pickle.HIGHEST_PROTOCOL)

def from_pickle(path):
    # with gzip.open(path, 'rb') as handle:
    with open(path, 'rb') as handle:
        return pickle.load(handle)

def cached(dir, name, refresh = False):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            r = refresh

            # set suffix
            suffix_prop = 'cache_suffix'
            suffix = ""
            if suffix_prop in kwargs:
                suffix = f".{kwargs[suffix_prop]}"
                del kwargs[suffix_prop]
            
            # set refresh
            refresh_prop = 'cache_refresh'
            if refresh_prop in kwargs:
                r = kwargs[refresh_prop]
                del kwargs[refresh_prop]

            path = f"{dir}/{name}{suffix}.pkl.gz"

            # try to get cached value
            if not r:
                try:
                    data = from_pickle(path)
                    return data
                except:
                    pass

            # refresh data
            data = fn(*args, **kwargs)

            to_pickle(path, data)
            return data
        return wrapper
    return decorator

# ############################################################################ #

# Can handle only pandas DataFrames with primitive types that are supported by 
# sqlite.

def sqlite_cached(dbpath, table, refresh=False):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if 'cache_suffix' in kwargs:
                tbl = f"{table}__{kwargs['cache_suffix']}"
                del kwargs['cache_suffix']
            else:
                tbl = table
            con = sqlite3.connect(dbpath)
            try:
                df = pd.DataFrame()
                if not refresh:
                    try:
                        df = pd.read_sql_query(f'SELECT * FROM "{tbl}"', con)
                    except:
                        pass
                if df.empty:
                    df = fn(*args, **kwargs)
                    df.to_sql(tbl, con, if_exists="replace")
            finally:
                con.close()
            return df
        return wrapper
    return decorator