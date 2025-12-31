from src.app_logs import StructuredLogger, configure_logging, get_logger

def test_structured_logger_methods():
    logger = StructuredLogger('test')
    logger.info('info')
    logger.warning('warn')
    logger.error('err')
    logger.debug('debug')
    logger.exception('exc', exc_info=Exception('fail'))
    assert isinstance(logger, StructuredLogger)

def test_configure_logging_and_get_logger():
    configure_logging('DEBUG')
    logger = get_logger('mylogger')
    assert isinstance(logger, StructuredLogger)
