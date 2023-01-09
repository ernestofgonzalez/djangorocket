import shortuuid


def default_uuid():
    return shortuuid.uuid()[:7]
