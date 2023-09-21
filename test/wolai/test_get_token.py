from wolai.base import WolaiBase


def get_token():
    wolai_base = WolaiBase()
    wolai_base.init_token()
    print(wolai_base.token)


if __name__ == '__main__':
    get_token()
