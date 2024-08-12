from zenif.log import Logger, StructuredLogger

l = Logger()
sl = StructuredLogger()

l.info("Hello", "world", sep=" - ")
sl.info("Hello", "world", sep=" - ", user="bob", ip="192.3.56.82")
