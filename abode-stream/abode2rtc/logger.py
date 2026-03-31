from logging import Logger
from colorlog import StreamHandler, ColoredFormatter, getLogger, INFO, DEBUG  # noqa: F401


handler = StreamHandler()
handler.setFormatter(ColoredFormatter('%(log_color)s%(asctime)s %(name)s [%(levelname)s] %(message)s'))

log: Logger = getLogger("abode2rtc")
log.setLevel(INFO)
log.addHandler(handler)

go2rtc_log: Logger = getLogger('go2rtc')
go2rtc_log.setLevel(INFO)
go2rtc_log.addHandler(handler)
