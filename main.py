import os
from pesudo_main import pseudo_main
from flaml import oai
import json


def main():
    pseudo_main(config_list)


if __name__ == "__main__":
    config_list = None
    os.environ["WOLFRAM_ALPHA_APPID"] = open("wolfram.txt").read().strip()
    oai.retry_timeout = 3600
    main()
