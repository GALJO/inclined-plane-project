import logging


def catcher(f):
    def wrap():
        try:
            logging.debug("The Catcher: awaiting disturbance.")
            f()
        except Exception as e:
            logging.critical("The Catcher: unexpected disturbance detected -- SHUTTING DOWN.")
            logging.critical("!!!!!!!!!!!!!!!!!!!!!!!! CRASH !!!!!!!!!!!!!!!!!!!!!!!!")
            logging.critical(e, exc_info=True)
            logging.critical("!!!!!!!!!!!!!!!!!!!!!!!! CRASH !!!!!!!!!!!!!!!!!!!!!!!!")
            raise e

    return wrap
