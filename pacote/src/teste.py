import alforria.__main__ as __main__

# print(alforria._PATHS_PATH)

print(__main__._PATHS_PATH)
__main__.set_config_path("./teste")
print(__main__._PATHS_PATH)

print(__main__.__version__)
