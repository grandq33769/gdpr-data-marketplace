import logging
template='[%(levelname)s]-[%(asctime)s]-[%(name)s]\n%(message)s\n'
template+='-'*70
logging.basicConfig(level=logging.INFO,
            format=template,
            datefmt='%Y-%m-%d %H:%M:%S')