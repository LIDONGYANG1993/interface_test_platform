defaultParams = {
    "id": 1,
    "name": "主包测试",
    "value": {
        "url_rpc": "http://testapitest.wb-intra.com/rpc/test",
        "appType": "main",
        "url_api": "http://testapitest.wb-intra.com/api/test",
        "initParams": {},
        "url_webapi": "http://testapitest.wb-intra.com/webApi/test",
        "environment": "test"
    }
}



class response:
    def __init__(self):
        self.result = {"code": 0, "msg": "访问成功！", "data": {}}
        self.request_error = {"code": -10000, "msg": "访问接口异常，请检查参数！", "data": {}}
        self.params_error = {"code": -10001, "msg": "缺少必要参数！", "data": {}}
        self.cat_id_error = {"code": -20001, "msg": "找不到对应cat_id！", "data": {}}
