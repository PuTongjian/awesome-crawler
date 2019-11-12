import re
import requests
import execjs
from urllib import parse

session = requests.session()

url = 'https://www.zhipin.com/c101270100-p100101/'
security_js = 'https://www.zhipin.com/web/common/security-js/{}.js'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/69.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Referer': 'https://www.zhipin.com/',
    'Upgrade-Insecure-Requests': '1',
    'TE': 'Trailers'
}


def get_boss_stoken(js: str) -> str:
    """
    生成token的算法
    """
    _reg = """
    	function test(seed,ts){
    		code = ABCZ(seed, parseInt(ts)+(480+new Date().getTimezoneOffset())*60*1000);
    		return code;
    	}
    \g<1>; function shift(aa) {
            while (--aa) {
                \g<2>['push'](\g<2>['shift']());
            };
            return \g<2>;
        };

    var _0x4c30_NEW = shift(\g<3> + 1);
    var _0x22a196 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=';
    function atob(_0x1ed846) {
                    var _0x17bad3 = String(_0x1ed846)['replace'](/=+$/, '');
                    for (var _0x5baa5b = 0x0, _0x232edd, _0x23a6cd, _0x3eeee5 = 0x0, _0x5b022c = ''; _0x23a6cd = _0x17bad3['charAt'](_0x3eeee5++); ~_0x23a6cd && (_0x232edd = _0x5baa5b % 0x4 ? _0x232edd * 0x40 + _0x23a6cd : _0x23a6cd,
                    _0x5baa5b++ % 0x4) ? _0x5b022c += String['fromCharCode'](0xff & _0x232edd >> (-0x2 * _0x5baa5b & 0x6)) : 0x0) {
                        _0x23a6cd = _0x22a196['indexOf'](_0x23a6cd);
                    }
                    return _0x5b022c;
                };
    function \g<4>(_0x1b34e2) {
    _0x1b34e2 = _0x1b34e2 - 0x0;
    var aa = _0x4c30_NEW[_0x1b34e2];
    return atob(aa);
    };
    function  ABCZ(
    """
    _js = re.sub(
        r"^(var\s*(\w+)=[^;]*?;)\s*\(function\([^\)]+,[^\)]+\)[\s\S]*?\w+\(\);\}\(\w+,\s*(\w+)\)\);\s*var\s*(\w+)[\s\S]*?ABC\[[^\]]*?]\['\w+'\]=function\(",
        _reg, js)
    _js = re.sub(r'\(document[\s\S]*?\)\)', r'(1)', _js)
    _js = re.sub(r'/function\|object[\s\S]*?\)\)', r'1)', _js)
    return _js


if __name__ == '__main__':
    # 起始请求
    response = session.get(url=url, headers=headers)
    # 302跳转 获取 seed, ts, name
    seed = re.match('.*seed=(.*?)&', parse.unquote(response.url)).group(1)
    ts = re.match('.*ts=(.*?)&', parse.unquote(response.url)).group(1)
    name = re.match('.*name=(.*?)&', parse.unquote(response.url)).group(1)
    # 获取生成token的js
    response = requests.get(url=security_js.format(name))
    # 生成token
    _js = get_boss_stoken(response.text)
    token = execjs.compile(_js).call('test', seed, ts)
    # 设置token至cookies
    cookies = {
        '__zp_stoken__': token
    }
    # 请求网页，获取职位信息
    response = session.get(url=url, headers=headers, cookies=cookies)
    print(response.text)
    print(response.headers)
    # 响应cookies中会返回seed, ts 用于生成下次请求的token
    print(session.cookies)
