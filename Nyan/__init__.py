import logging

from .api import APIConstants, APIFastAPI
from .api.services import ServiceYoutTubePlaylistDL, ServiceFiles, ServiceTest

from .core import NyanController, NyanDB, NyanData, NyanLogging, NyanConstants


class DB(NyanDB.Nyan_DB):
    def __init__(self, controller, db_dir, db_name):

        NyanDB.Nyan_DB.__init__(self, controller, db_dir, db_name)

    def _load_modules(self):
        pass

    def _unload_modules(self):

        self._modules = []

    def _create_db(self):

        # intentionally not IF NOT EXISTS here, to catch double-creation accidents early and on a good table
        self._execute("CREATE TABLE version ( version INTEGER );")
        self._execute(
            "CREATE TABLE IF NOT EXISTS options ( options TEXT_YAML );",
        )
        self._execute("INSERT INTO version ( version ) VALUES ( ? );", (core.SOFTWARE_VERSION,))

    def _init_external_databases(self):
        pass
        # self._db_filenames[ 'external_caches' ] = 'client.caches.db'
        # self._db_filenames[ 'external_mappings' ] = 'client.mappings.db'
        # self._db_filenames[ 'external_master' ] = 'client.master.db'

    def _init_caches(self):

        pass

    def _manage_db_error(self, job, e):

        raise NotImplementedError()

    def _read(self, action, *args, **kwargs):

        raise NotImplementedError()

    def _write(self, action, *args, **kwargs):

        raise NotImplementedError()

    def publish_status_update(self):

        pass


class Controller(NyanController.Nyan_Controller):
    def _init_db(self):
        return DB(self, self.db_dir, "main")


def __real_main():
    import uvicorn

    # uvicorn_error = logging.getLogger("uvicorn.error")
    # uvicorn_error.disabled = True
    # uvicorn_access = logging.getLogger("uvicorn.access")
    # uvicorn_access.disabled = True

    db_dir = "./db/"

    try:
        controller = Controller(db_dir)

        controller.boot_everything_base()

        app = APIFastAPI.Nyan_API()
        app.include_router(ServiceFiles.File_Service(controller))
        app.include_router(ServiceYoutTubePlaylistDL.Youtube_Playlist_DL_Service(controller))
        app.include_router(ServiceTest.Test_Service(controller))
        # app.include_router(APIRouting.Search_Routing(controller))
        # app.include_router(APIRouting.Static_Routing(controller))

        uvicorn.run(app, host=APIConstants.SERVER_IP, port=APIConstants.SERVER_PORT)

    except KeyboardInterrupt:
        pass

    except Exception as e:
        NyanData.print_exception(e, True)

    finally:

        controller.exit_everything_base()


def main():

    NyanLogging.setup_and_show_startup_message(log_file="./logs.log", log_level=logging.INFO)

    __real_main()
