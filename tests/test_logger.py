from src.app_logs import StructuredLogger, configure_logging, get_logger

def test_structured_logger_info_debug():
    logger = StructuredLogger('test')
    logger.info('info message', foo='bar')
    logger.debug('debug message', foo='baz')
    logger.warning('warn message', foo='warn')
    logger.error('error message', foo='err')
    logger.exception('exception message', exc_info=Exception('fail'))
    assert isinstance(logger, StructuredLogger)

def test_configure_logging_levels():
    configure_logging('DEBUG')
    configure_logging('INFO')
    configure_logging('WARN')
    configure_logging('ERROR')
    configure_logging('INVALID')
    assert True

def test_get_logger():
    logger = get_logger('mylogger')
    assert isinstance(logger, StructuredLogger)
