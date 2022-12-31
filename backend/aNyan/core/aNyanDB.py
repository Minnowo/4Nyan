import sqlite3
import collections
import logging
import queue
import os
import time
import traceback

from . import aNyanGlobals
from . import aNyanData
from . import aNyanExceptions
from . import aNyanPaths
from . import aNyanController


class Temporary_Integer_Table_Name_Cache(object):

    """
    A table name cache used in the Temporary_Integer_Table class

    This class gets and caches table names

    Example usage:
    ```
    # connect to our database
    conn = sqlite3.connect("sample.sqlite")

    # make the cursor
    cursor = conn.cursor()

    # make sure you've got something as 'mem'
    cursor.execute( 'ATTACH ":memory:" AS mem;' )

    # get / create the instance
    titnc = Temporary_Integer_Table_Name_Cache.instance()

    # choose a column name
    column_name = "user_id"

    # get a table name
    (initialised, table_name) = titnc.get_name(column_name)

    # if the table was not initialised we should create it
    if not initialised:

        cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ( {column_name} INTEGER PRIMARY KEY );")

    # do stuff with your table here

    # return our table to the cache
    titnc.release_name(column_name, table_name)
    ```
    """

    my_instance = None

    def __init__(self):

        if Temporary_Integer_Table_Name_Cache.my_instance is not None:
            raise Exception("This class is a singleton")

        Temporary_Integer_Table_Name_Cache.my_instance = self

        self._column_names_to_table_names = collections.defaultdict(collections.deque)
        self._column_names_counter = collections.Counter()

    @staticmethod
    def instance() -> "Temporary_Integer_Table_Name_Cache":

        if Temporary_Integer_Table_Name_Cache.my_instance is None:

            Temporary_Integer_Table_Name_Cache()

        return Temporary_Integer_Table_Name_Cache.my_instance

    def clear(self):

        self._column_names_to_table_names = collections.defaultdict(collections.deque)
        self._column_names_counter = collections.Counter()

    def get_name(self, column_name: str):

        table_names = self._column_names_to_table_names[column_name]

        initialised = True

        if len(table_names) == 0:

            initialised = False

            i = self._column_names_counter[column_name]

            table_name = "mem.temp_int_{}_{}".format(column_name, i)

            table_names.append(table_name)

            self._column_names_counter[column_name] += 1

        table_name = table_names.pop()

        return (initialised, table_name)

    def release_name(self, column_name: str, table_name: str):

        self._column_names_to_table_names[column_name].append(table_name)


class Temporary_Integer_Table(object):

    """
    A temporary integer database table

    This class should be used in 'with' blocks to write a iterable of integers to a temporary db table
    in the given column

    Ensure you've got something as 'mem' because this uses Temporary_Integer_Table_Name_Cache
    which returns table names in the format 'mem.temp_int_{}_{}'

    Example usage:
    ```
    # connect to our database
    conn = sqlite.connect("sample.sqlite")

    # make the cursor
    cursor = conn.cursor()

    # make sure you've got something as 'mem'
    cursor.execute( 'ATTACH ":memory:" AS mem;' )

    # some fake data, and a column in our db
    some_int_data = list(range(10))
    column = "user_id"

    # dump the 'some_int_data' into a temporary in memory db and get the table name
    with Temporary_Integer_Table(cursor, some_int_data, column) as table:

        # show the temp table name that is created / used
        print(table)

        # selects from 'my_table' anything inserted into the temp table above
        dat = cursor.execute(f'SELECT * FROM my_table CROSS JOIN {table} USING ( {column} );')

        # print off the values
        for i in dat:
            print(i)
    ```
    """

    def __init__(self, cursor: sqlite3.Cursor, integer_iterable, column_name: str):

        if not isinstance(integer_iterable, set):

            integer_iterable = set(integer_iterable)

        self._cursor = cursor
        self._integer_iterable = integer_iterable
        self._column_name = column_name

        (self._initialised, self._table_name) = Temporary_Integer_Table_Name_Cache.instance().get_name(self._column_name)

    def __enter__(self):

        if not self._initialised:

            self._cursor.execute(
                "CREATE TABLE IF NOT EXISTS {} ( {} INTEGER PRIMARY KEY );".format(self._table_name, self._column_name)
            )

        self._cursor.executemany(
            "INSERT INTO {} ( {} ) VALUES ( ? );".format(self._table_name, self._column_name),
            ((i,) for i in self._integer_iterable),
        )

        return self._table_name

    def __exit__(self, exc_type, exc_val, exc_tb):

        self._cursor.execute("DELETE FROM {};".format(self._table_name))

        Temporary_Integer_Table_Name_Cache.instance().release_name(self._column_name, self._table_name)

        return False


class DB_Base(object):

    """
    A base database class wrapper for the sqlite3.Cursor
    """

    def __init__(self):

        self._cursor: sqlite3.Cursor = None

    def _close_cursor(self):

        if self._cursor is not None:

            self._cursor.close()

            del self._cursor

            self._cursor = None

    def _create_index(self, table_name: str, columns: list[str], unique: bool = False):

        if unique:

            create_phrase = "CREATE UNIQUE INDEX IF NOT EXISTS"

        else:

            create_phrase = "CREATE INDEX IF NOT EXISTS"

        index_name = self._generate_index_name(table_name, columns)

        if "." in table_name:

            table_name_simple = table_name.split(".")[1]

        else:

            table_name_simple = table_name

        statement = "{} {} ON {} ({});".format(create_phrase, index_name, table_name_simple, ", ".join(columns))

        self._execute(statement)

    def _execute(self, query: str, *args) -> sqlite3.Cursor:

        # if aNyanGlobals.query_planner_mode and query not in aNyanGlobals.queries_planned:

        #     plan_lines = self._cursor.execute("EXPLAIN QUERY PLAN {}".format(query), *args).fetchall()

        #     aNyanGlobals.query_planner_query_count += 1

        #     aNyanGlobals.controller.PrintQueryPlan(query, plan_lines)

        return self._cursor.execute(query, *args)

    def _execute_many(self, query: str, args_iterator):

        # if aNyanGlobals.query_planner_mode and query not in aNyanGlobals.queries_planned:

        #     args_iterator = list(args_iterator)

        #     if len(args_iterator) > 0:

        #         plan_lines = self._cursor.execute("EXPLAIN QUERY PLAN {}".format(query), args_iterator[0]).fetchall()

        #         aNyanGlobals.query_planner_query_count += 1

        #         aNyanGlobals.controller.PrintQueryPlan(query, plan_lines)

        self._cursor.executemany(query, args_iterator)

    def _generate_index_name(self, table_name: str, columns: list[str]) -> str:

        return "{}_{}_index".format(table_name, "_".join(columns))

    def _get_attached_database_names(self, include_temp: bool = False) -> list[str]:

        if include_temp:

            f = lambda schema_name, path: True

        else:

            f = lambda schema_name, path: schema_name != "temp" and path != ""

        names = [schema_name for (number, schema_name, path) in self._execute("PRAGMA database_list;") if f(schema_name, path)]

        return names

    def _get_last_row_id(self) -> int:

        return self._cursor.lastrowid

    def _get_row_count(self) -> int:

        row_count = self._cursor.rowcount

        if row_count == -1:

            return 0

        else:

            return row_count

    def _index_exists(self, table_name: str, columns: list[str]) -> bool:

        index_name = self._generate_index_name(table_name, columns)

        return self._table_or_index_exists(index_name, "index")

    def _make_temporary_integer_table(self, integer_iterable, column_name):

        return Temporary_Integer_Table(self._cursor, integer_iterable, column_name)

    def _set_cursor(self, c: sqlite3.Cursor):

        self._cursor = c

    def _strip_singleton_tuples_to_iterator(self, iterable_cursor):

        # strip singleton tuples to an iterator

        return (item for (item,) in iterable_cursor)

    def _strip_singleton_tuples_to_list(self, iterable_cursor):

        # strip singleton tuples to a list

        return [item for (item,) in iterable_cursor]

    def _strip_singleton_tuples_to_set(self, iterable_cursor):

        # strip singleton tuples to a set

        return {item for (item,) in iterable_cursor}

    def _table_exists(self, table_name: str) -> bool:

        return self._table_or_index_exists(table_name, "table")

    def _table_or_index_exists(self, name: str, item_type: str) -> bool:

        if "." in name:

            (schema, name) = name.split(".", 1)

            search_schemas = [schema]

        else:

            search_schemas = self._get_attached_database_names()

        for schema in search_schemas:

            result = self._execute(
                "SELECT 1 FROM {}.sqlite_master WHERE name = ? AND type = ?;".format(schema), (name, item_type)
            ).fetchone()

            if result is not None:

                return True

        return False


class DB_Cursor_Transaction_Wrapper(DB_Base):
    def __init__(self, c: sqlite3.Cursor, transaction_commit_period: int):

        DB_Base.__init__(self)

        self._set_cursor(c)

        self._transaction_commit_period = transaction_commit_period

        self._transaction_start_time = 0
        self._in_transaction = False
        self._transaction_contains_writes = False

        self._last_mem_refresh_time = aNyanData.time_now()
        self._last_wal_checkpoint_time = aNyanData.time_now()

        self._pubsubs = []

    def begin_immediate(self):

        if not self._in_transaction:

            self._execute("BEGIN IMMEDIATE;")
            self._execute("SAVEPOINT muh_savepoint;")

            self._transaction_start_time = aNyanData.time_now()
            self._in_transaction = True
            self._transaction_contains_writes = False

    def clean_pub_subs(self):

        self._pubsubs = []

    def commit(self):

        if not self._in_transaction:

            logging.warning("Received a call to commit, but was not in a transaction!")
            return

        self.do_pub_subs()

        self.clean_pub_subs()

        self._execute("COMMIT;")

        self._in_transaction = False
        self._transaction_contains_writes = False

        if aNyanGlobals.db_journal_mode == "WAL" and aNyanData.time_has_passed(self._last_wal_checkpoint_time + 1800):

            self._execute("PRAGMA wal_checkpoint(PASSIVE);")

            self._last_wal_checkpoint_time = aNyanData.time_now()

        if aNyanData.time_has_passed(self._last_mem_refresh_time + 600):

            self._execute("DETACH mem;")
            self._execute('ATTACH ":memory:" AS mem;')

            Temporary_Integer_Table_Name_Cache.instance().clear()

            self._last_mem_refresh_time = aNyanData.time_now()

    def commit_and_begin(self):

        if self._in_transaction:

            self.commit()

            self.begin_immediate()

    def do_pub_subs(self):

        for (topic, args, kwargs) in self._pubsubs:

            aNyanGlobals.controller.pub(topic, *args, **kwargs)

    def in_transaction(self):

        return self._in_transaction

    def notify_write_occuring(self):

        self._transaction_contains_writes = True

    def pub_after_job(self, topic, *args, **kwargs):

        if len(args) == 0 and len(kwargs) == 0:

            if (topic, args, kwargs) in self._pubsubs:

                return

        self._pubsubs.append((topic, args, kwargs))

    def rollback(self):

        if self._in_transaction:

            self._execute("ROLLBACK TO muh_savepoint;")

            # any temp int tables created in this lad will be rolled back, so 'initialised' can't be trusted. just reset, no big deal
            Temporary_Integer_Table_Name_Cache.instance().clear()

            # still in transaction
            # transaction may no longer contain writes, but it isn't important to figure out that it doesn't

        else:

            logging.warning("Received a call to rollback, but was not in a transaction!")

    def save(self):

        if self._in_transaction:

            try:

                self._execute("RELEASE muh_savepoint;")

            except sqlite3.OperationalError:

                logging.warning("Tried to release a database savepoint, but failed!")

            self._execute("SAVEPOINT muh_savepoint;")

        else:

            logging.warning("Received a call to save, but was not in a transaction!")

    def time_to_commit(self):

        return (
            self._in_transaction
            and self._transaction_contains_writes
            and aNyanData.time_has_passed(self._transaction_start_time + self._transaction_commit_period)
        )


JOURNAL_SIZE_LIMIT = 128 * 1024 * 1024
JOURNAL_ZERO_PERIOD = 900
MEM_REFRESH_PERIOD = 600
WAL_PASSIVE_CHECKPOINT_PERIOD = 300
WAL_TRUNCATE_CHECKPOINT_PERIOD = 900


class Nyan_DB(DB_Base):
    def __init__(self, controller: aNyanController.Nyan_Controller, db_dir: str, db_name: str):

        DB_Base.__init__(self)

        self._db_dir = db_dir
        self._db_name = db_name
        self._controller = controller

        main_db_filename = db_name

        if not main_db_filename.endswith(".db"):

            main_db_filename += ".db"

        self._db_filenames = {"main": main_db_filename}

        self._durable_temp_db_filename = db_name + ".temp.db"

        durable_temp_db_path = os.path.join(self._db_dir, self._durable_temp_db_filename)

        if os.path.exists(durable_temp_db_path):

            aNyanPaths.delete_path(durable_temp_db_path)

            wal_lad = durable_temp_db_path + "-wal"

            if os.path.exists(wal_lad):

                aNyanPaths.delete_path(wal_lad)

            shm_lad = durable_temp_db_path + "-shm"

            if os.path.exists(shm_lad):

                aNyanPaths.delete_path(shm_lad)

            logging.info("Found and deleted the durable temporary database on boot. The last exit was probably not clean.")

        self._init_external_databases()

        self._is_first_start = False
        self._is_db_updated = False
        self._local_shutdown = False
        self._pause_and_disconnect = False
        self._loop_finished = False
        self._ready_to_serve_requests = False
        self._could_not_initialise = False

        self._jobs = queue.Queue()

        self._currently_doing_job = False
        self._current_status = ""
        self._current_job_name = ""

        self._db = None
        self._is_connected = False

        self._cursor_transaction_wrapper = None

        if os.path.exists(os.path.join(self._db_dir, self._db_filenames["main"])):

            # open and close to clean up in case last session didn't close well

            self._init_db()
            self._close_db_connection()

        self._init_db()

        (version,) = self._execute("SELECT version FROM version;").fetchone()

        logging.info(f"Database version: {version}")

        self._close_db_connection()

        self._controller.call_to_thread_long_running(self.MainLoop)

        while not self._ready_to_serve_requests:

            time.sleep(0.1)

            if self._could_not_initialise:

                raise Exception("Could not initialise the db! Error written to the log!")

    def _init_db(self):

        db_path = os.path.join(self._db_dir, self._db_filenames["main"])

        create_db = not os.path.exists(db_path)

        if create_db:

            external_db_paths = [
                os.path.join(self._db_dir, self._db_filenames[db_name]) for db_name in self._db_filenames if db_name != "main"
            ]

            existing_external_db_paths = [
                external_db_path for external_db_path in external_db_paths if os.path.exists(external_db_path)
            ]

            if len(existing_external_db_paths) > 0:

                message = 'Although the external files, "{}" do exist, the main database file, "{}", does not! This makes for an invalid database, and the program will now quit. Please contact hydrus_dev if you do not know how this happened or need help recovering from hard drive failure.'

                message = message.format(", ".join(existing_external_db_paths), db_path)

                raise aNyanExceptions.DB_Access_Exception(message)

        self._init_db_connection()

        result = self._execute("SELECT 1 FROM sqlite_master WHERE type = ? AND name = ?;", ("table", "version")).fetchone()

        if create_db or result is None:

            self._is_first_start = True

            self._create_db()

            self._cursor_transaction_wrapper.commit_and_begin()

    def _init_db_connection(self):

        db_path = os.path.join(self._db_dir, self._db_filenames["main"])

        if os.path.exists(db_path) and not aNyanPaths.file_is_writeable(db_path):

            raise aNyanExceptions.DB_Access_Exception(f"the database: {db_path} seems to be read-only!")

        try:

            self._db = sqlite3.connect(db_path, isolation_level=None, detect_types=sqlite3.PARSE_DECLTYPES)

            self._set_cursor(self._db.cursor())

            self._is_connected = True

            self._cursor_transaction_wrapper = DB_Cursor_Transaction_Wrapper(self._c, aNyanGlobals.db_transaction_commit_period)

            if aNyanGlobals.no_db_temp_files:

                # use memory for temp store exclusively
                self._execute("PRAGMA temp_store = 2;")

            self._attach_external_databases()

            self._load_modules()

            self._execute('ATTACH ":memory:" AS mem;')

        except aNyanExceptions.DB_Access_Exception:

            raise

        except Exception as e:

            message = f"Could not connect to the database! Error follows:" + os.linesep * 2 + str(e)

            raise aNyanExceptions.DB_Access_Exception(message)

        Temporary_Integer_Table_Name_Cache.instance().clear()

        # durable_temp is not excluded here
        db_names = [name for (index, name, path) in self._execute("PRAGMA database_list;") if name not in ("mem", "temp")]

        for db_name in db_names:

            # MB -> KB
            cache_size = aNyanGlobals.db_cache_size * 1024

            self._execute(f"PRAGMA {db_name}.cache_size = -{cache_size};")

            self._execute(f"PRAGMA {db_name}.journal_mode = {aNyanGlobals.db_journal_mode};")

            if aNyanGlobals.db_journal_mode in ("PERSIST", "WAL"):

                # We tried 1GB here, but I have reports of larger ones that don't seem to truncate ever?
                # Not sure what that is about, but I guess the db sometimes doesn't want to (expensively?) recover pages from the journal and just appends more data
                # In any case, this pragma is not a 'don't allow it to grow larger than', it's a 'after commit, truncate back to this', so no need to make it so large
                # default is -1, which means no limit

                self._execute(f"PRAGMA {db_name}.journal_size_limit = {JOURNAL_SIZE_LIMIT};")

            self._execute(f"PRAGMA {db_name}.synchronous = {aNyanGlobals.db_synchronous };")

            try:

                self._execute(f"SELECT * FROM {db_name}.sqlite_master;").fetchone()

            except sqlite3.OperationalError as e:

                message = (
                    "The database seemed valid, but reading basic data failed."
                    + " You may need to run the program in a different journal mode using --db_journal_mode."
                    + " Full error information:"
                    + os.linesep * 2
                    + str(e)
                )

                logging.debug(message)

                raise aNyanExceptions.DB_Access_Exception(message)

        try:

            self._cursor_transaction_wrapper.begin_immediate()

        except Exception as e:

            if "locked" in str(e):

                message = (
                    "Database appeared to be locked."
                    + " Please ensure there is not another client already running on this database,"
                    + " and then try restarting the client."
                )

                logging.debug(message, e)

                raise aNyanExceptions.DB_Access_Exception(message)

            raise aNyanExceptions.DB_Access_Exception(str(e))

    def _attach_external_databases(self):

        for (name, filename) in self._db_filenames.items():

            if name == "main":
                continue

            db_path = os.path.join(self._db_dir, filename)

            if os.path.exists(db_path) and not aNyanPaths.file_is_writeable(db_path):

                raise aNyanExceptions.DB_Access_Exception(f"the database: {db_path} seems to be read-only!")

            self._execute(f"ATTACH ? AS {name};", (db_path,))

        db_path = os.path.join(self._db_dir, self._durable_temp_db_filename)

        self._execute("ATTACH ? AS durable_temp;", (db_path,))

    def _close_db_connection(self):

        Temporary_Integer_Table_Name_Cache.instance().clear()

        if self._db is None:
            return

        if self._cursor_transaction_wrapper.in_transaction():

            self._cursor_transaction_wrapper.commit()

        self._close_cursor()

        self._db.close()

        del self._db

        self._db = None

        self._is_connected = False

        self._cursor_transaction_wrapper = None

        self._unload_modules()

    def _load_modules(self):
        pass

    def _unload_modules(self):

        self._modules = []

    def _create_db(self):

        raise NotImplementedError()

    def _init_external_databases(self):

        pass

    def _init_caches(self):

        pass

    def _display_catastrophic_error(self, text):

        message = (
            "The db encountered a serious error! "
            + "This is going to be written to the log as well, but here it is for a screenshot:"
            + os.linesep * 2
            + text
        )

        logging.critical(message)

    def _process_job(self, job):

        job_type = job.GetType()

        (action, args, kwargs) = job.GetCallableTuple()

        try:

            if job_type in ("read_write", "write"):

                self._current_status = "db write locked"

                self._cursor_transaction_wrapper.notify_write_occuring()

            else:

                self._current_status = "db read locked"

            self.publish_status_update()

            if job_type in ("read", "read_write"):

                result = self._Read(action, *args, **kwargs)

            elif job_type in ("write"):

                result = self._Write(action, *args, **kwargs)

            if job.IsSynchronous():

                job.PutResult(result)

            self._cursor_transaction_wrapper.save()

            if self._cursor_transaction_wrapper.time_to_commit():

                self._current_status = "db committing"

                self.publish_status_update()

                self._cursor_transaction_wrapper.commit_and_begin()

            self._DoAfterJobWork()

        except Exception as e:

            self._manage_db_error(job, e)

            try:

                self._cursor_transaction_wrapper.rollback()

            except Exception as rollback_e:

                logging.error(
                    "When the transaction failed, attempting to rollback the database failed. Please restart the client as soon as is convenient."
                )

                self._close_db_connection()

                self._init_db_connection()

                aNyanData.print_exception(rollback_e)

        finally:

            self._clean_after_job_work()

            self._current_status = ""

            self.publish_status_update()

    def _clean_after_job_work(self):

        self._cursor_transaction_wrapper.clean_pub_subs()

    def _DoAfterJobWork(self):

        self._cursor_transaction_wrapper.do_pub_subs()

    def _manage_db_error(self, job, e):

        raise NotImplementedError()

    def publish_status_update(self):

        pass

    def main_loop(self):

        try:

            # have to reinitialise because the thread id has changed
            self._init_db_connection()

            self._init_caches()

        except:

            self._display_catastrophic_error(traceback.format_exc())

            self._could_not_initialise = True

            return

        self._ready_to_serve_requests = True

        error_count = 0

        while not ((self._local_shutdown or aNyanGlobals.model_shutdown) and self._jobs.empty()):

            try:

                job = self._jobs.get(timeout=1)

                self._currently_doing_job = True
                self._current_job_name = job.ToString()

                self.publish_status_update()

                try:

                    if aNyanGlobals.db_report_mode:

                        summary = "Running db job: " + job.ToString()

                        logging.info(summary)

                    # if aNyanGlobals.profile_mode:

                    #     summary = "Profiling db job: " + job.ToString()

                    #     HydrusData.Profile(
                    #         summary,
                    #         "self._ProcessJob( job )",
                    #         globals(),
                    #         locals(),
                    #         min_duration_ms=aNyanGlobals.db_profile_min_job_time_ms,
                    #     )

                    # else:

                    self._process_job(job)

                    error_count = 0

                except:

                    error_count += 1

                    if error_count > 5:

                        raise

                    self._jobs.put(job)  # couldn't lock db; put job back on queue

                    time.sleep(5)

                self._currently_doing_job = False
                self._current_job_name = ""

                self.publish_status_update()

            except queue.Empty:

                if self._cursor_transaction_wrapper.time_to_commit():

                    self._cursor_transaction_wrapper.commit_and_begin()

            if self._pause_and_disconnect:

                self._init_db_connection()

                while self._pause_and_disconnect:

                    if self._local_shutdown or aNyanGlobals.model_shutdown:

                        break

                    time.sleep(1)

                self._init_db_connection()

        self._close_db_connection()

        temp_path = os.path.join(self._db_dir, self._durable_temp_db_filename)

        aNyanPaths.delete_path(temp_path)

        self._loop_finished = True
