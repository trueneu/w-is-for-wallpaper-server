class RepackError(Exception):
    pass


def repack(structure, data):
    if isinstance(structure, dict):
        result = {}
        for k, v in structure.items():
            if isinstance(v, dict) or isinstance(v, list):
                result[k] = repack(v, data)
            else:
                data_item = data
                for part in v.split(':'):
                    try:
                        data_item = data_item[part]
                    except KeyError:
                        # raise RepackError("Error occured when repacking {data} to {structure}. "
                        #                   "Missing key {k}".format(
                        #     data=data, structure=structure, k=part
                        # ))
                        data_item = None
                        break
                if data_item is not None:
                    result[k] = data_item

    elif isinstance(structure, list):
        result = []
        for index, item in enumerate(structure):
            if isinstance(item, dict) or isinstance(item, list):
                result.append(repack(item, data))
            else:
                data_item = data
                for part in item.split(':'):
                    try:
                        data_item = data_item[part]
                    except KeyError:
                        # raise RepackError("Error occured when repacking {data} to {structure}. "
                        #                   "Missing key {k}".format(
                        #     data=data, structure=structure, k=part
                        # ))
                        data_item = None
                        break
                if data_item is not None:
                    result.append(data_item)

    return result
