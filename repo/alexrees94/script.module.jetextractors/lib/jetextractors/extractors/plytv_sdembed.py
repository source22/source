import requests, re, base64

from ..models.Extractor import Extractor
from ..models.Link import Link
from ..util.hunter import hunter

class PlyTv(Extractor):
    def __init__(self) -> None:
        self.domains = ["plytv.me", "www.plytv.me", "tvply.me", "www.tvply.me"]

    def getAuthUrl(self, embed):
        re_auth = re.compile(r'authUrl = formauthurl\({"scode": "(.+?)", "ts": (.+?)}\);').findall(embed)[0]
        re_stream = re.compile(r"strName = '(.+?)'").findall(embed)[0]
        return "https://key.seckeyserv.me/?stream=%s&scode=%s&expires=%s" % (re_stream, re_auth[0], re_auth[1])

    def plytv_sdembed(self, base_url, origin):
        if not base_url.startswith("http"):
            base_url = "https://www.tvply.me/sdembed?v=" + base_url
        r_embed = requests.post(base_url, headers={"Origin": origin, "Referer": origin, "User-Agent": self.user_agent}).text
        re_hunter = re.compile(r'decodeURIComponent\(escape\(r\)\)}\("(.+?)",(.+?),"(.+?)",(.+?),(.+?),(.+?)\)').findall(r_embed)
        if len(re_hunter) > 0:
            re_hunter = re_hunter[0]
            deobfus = hunter(re_hunter[0], int(re_hunter[1]), re_hunter[2], int(re_hunter[3]), int(re_hunter[4]), int(re_hunter[5]))
            re_b64 = re.compile(r"const (?:strmUrl|soureUrl) = '(.+?)';").findall(deobfus)[0]
            url = base64.b64decode(re_b64).decode("UTF-8")
            try:
                auth_url = self.getAuthUrl(deobfus)
                auth = requests.get(auth_url, headers={"Referer": base_url, "User-Agent": self.user_agent, "Origin": "https://www.tvply.me"}).text
            except:
                pass
        else:
            re_b64 = re.compile(r"const (?:strmUrl|soureUrl) = '(.+?)';").findall(r_embed)[0]
            url = base64.b64decode(re_b64).decode("UTF-8")
            try:
                auth_url = self.getAuthUrl(r_embed)
                requests.get(auth_url, headers={"Referer": base_url, "User-Agent": self.user_agent}).text
            except:
                pass
        return Link(address=url, headers={"Referer": "https://www.tvply.me/", "User-Agent": self.user_agent})

    def get_link(self, url):
        if "&origin=" not in url:
            return ""
        else:
            origin = url[url.index("&origin=") + 8:]
            return self.plytv_sdembed(url, origin)
