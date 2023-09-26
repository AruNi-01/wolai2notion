from wolai.base import WolaiBase


def get_token():
    wolai_base = WolaiBase()
    print(wolai_base.token)


if __name__ == '__main__':
    get_token()
