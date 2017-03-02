def merge_properties(dst, src):
    """
    Merge the given src dict into dst dict.
    """
    if len(dst) == 0:
        dst.update(src)
        return

    for key in src.keys():
        dst_value = dst.get(key)
        src_value = src.get(key)

        if src_value is None or dst_value is None:
            dst[key] = src_value

        elif type(src_value) != type(dst_value):
            continue

        elif type(dst_value) == dict:
            merge_properties(dst_value, src_value)

        else:
            dst[key] = src_value
