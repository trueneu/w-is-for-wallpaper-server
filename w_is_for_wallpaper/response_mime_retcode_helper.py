"""
(c) Pavel Gurkov aka trueneu, 2016, All Rights Reserved
"""

import flask

HTTP_OK = 200
HTTP_INT_SRV_ERR = 500
HTTP_NOT_FOUND = 404


def json_200(payload):
    return flask.Response(response=payload,
                          status=HTTP_OK,
                          mimetype="application/json")


def json_500(payload):
    return flask.Response(response=payload,
                          status=HTTP_INT_SRV_ERR,
                          mimetype="application/json")


def json_404(payload):
    return flask.Response(response=payload,
                          status=HTTP_NOT_FOUND,
                          mimetype="application/json")
