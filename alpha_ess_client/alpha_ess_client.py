from dataclasses import dataclass
import time
import hashlib
from typing import Any, Dict

import requests


JsonType = Dict[str, Any]


RETURN_CODE_DICT = {
    6001: "Parameter error",
    6002: "The SN is not bound to the user",
    6003: "You have bound this SN",
    6004: "CheckCode error",
    6005: "This appId is not bound to the SN",
    6006: "Timestamp error",
    6007: "Sign verification error",
    6008: "Set failed",
    6009: "Whitelist verification failed",
    6010: "Sign is empty",
    6011: "Timestamp is empty",
    6012: "AppId is empty",
    6016: "Data does not exist or has been deleted",
    6026: "Internal error",
    6029: "Operation failed",
    6038: "System SN does not exist",
    6042: "System offline",
    6046: "Verification code error",
    6053: "The request was too fast, please try again later",
}


@dataclass
class AlphaEssClient:
    """
    Simple client for the Open AlphaESS API (https://open.alphaess.com/api)
    Endpoint documentation: https://open.alphaess.com/developmentManagement/apiList
    AppID and AppSecret: https://open.alphaess.com/developmentManagement/developerInformation
    """

    appID: str
    appSecret: str
    base_url: str = "https://openapi.alphaess.com/api"

    def _headers(self):
        timestamp = str(int(time.time()))
        return {
            "Content-Type": "application/json",
            "Connection": "keep-alive",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Cache-Control": "no-cache",
            "timestamp": f"{timestamp}",
            "sign": f"{str(hashlib.sha512((str(self.appID) + str(self.appSecret) + str(timestamp)).encode('ascii')).hexdigest())}",
            "appId": self.appID,
            "timeStamp": timestamp,
        }

    def _request(self, path: str, params: Dict[str, Any], method="GET") -> JsonType:
        """Send GET request"""
        url = f"{self.base_url}/{path}"
        headers = self._headers()
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, data=params)
        else:
            raise ValueError(f"Unknown request method {method}")
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        jdata: JsonType = response.json()
        code = jdata.get("code")
        if not isinstance(code, int):
            raise ValueError(
                f"Response is missing an integer return code when calling {url}: {jdata}"
            )
        if code in RETURN_CODE_DICT:
            raise ValueError(
                f"Response contains error code {code} '{RETURN_CODE_DICT[code]}' when calling {url}: {jdata}"
            )
        if jdata.get("data") is None:
            raise ValueError(
                f"Response is missing 'data' field returned when calling {url}: {jdata}"
            )
        return jdata["data"]

    def getEvChargerConfigList(self, sysSn: str) -> JsonType:
        """Obtain the SN of the charging pile according to the SN, and set the model"""
        params = dict(sysSn=sysSn)
        return self._request("getEvChargerConfigList", params)

    def getEvChargerCurrentsBySn(self, sysSn: str) -> JsonType:
        """Obtain the current setting of charging pile household according to SN"""
        params = dict(sysSn=sysSn)
        return self._request("getEvChargerCurrentsBySn", params)

    def setEvChargerCurrentsBySn(self, sysSn: str, currentsetting: float) -> JsonType:
        """Set charging pile household current setting according to SN"""
        params = dict(sysSn=sysSn, currentsetting=currentsetting)
        return self._request("setEvChargerCurrentsBySn", params, method="POST")

    def getEvChargerStatusBySn(self, synSn: str, evchargerSn: str) -> JsonType:
        """Obtain charging pile status according to SN+charging pile SN"""
        params = dict(synSn=synSn, evchargerSn=evchargerSn)
        return self._request("getEvChargerStatusBySn", params)

    def remoteControlEvCharger(
        self, synSn: str, evchargerSn: str, controlMode: int
    ) -> JsonType:
        """According to SN+ charging pile SN remote control charging pile to start charging/stop charging"""
        params = dict(synSn=synSn, evchargerSn=evchargerSn, controlMode=controlMode)
        return self._request("remoteControlEvCharger", params, method="POST")

    def getSumDataForCustomer(self, sysSn: str) -> JsonType:
        """According SN to get System Summary data"""
        params = dict(sysSn=sysSn)
        return self._request("getSumDataForCustomer", params)

    def getESSList(self) -> JsonType:
        """According to SN to get system list data"""
        return self._request("getEssList", dict())

    def getLastPowerData(self, sysSn: str) -> JsonType:
        """According SN to get real-time power data"""
        params = dict(sysSn=sysSn)
        return self._request("getLastPowerData", params)

    def getOneDayPowerBySn(self, sysSn: str, queryDate: str) -> JsonType:
        """According SN to get system power data"""
        params = dict(sysSn=sysSn, queryDate=queryDate)
        return self._request("getOneDayPowerBySn", params)

    def getOneDateEnergyBySn(self, sysSn: str, queryDate: str) -> JsonType:
        """According SN to get System Energy Data"""
        params = dict(sysSn=sysSn, queryDate=queryDate)
        return self._request("getOneDateEnergyBySn", params)

    def getChargeConfigInfo(self, sysSn: str) -> JsonType:
        """According SN to get charging setting information"""
        params = dict(synSn=sysSn)
        return self._request("getChargeConfigInfo", params)

    def updateChargeConfigInfo(
        self,
        sysSn: str,
        batHighCap: float,
        gridCharge: int,
        timeChae1: str,
        timeChae2: str,
        timeChaf1: str,
        timeChaf2: str,
    ) -> JsonType:
        """According SN to Set charging information"""
        params = dict(
            sysSn=sysSn,
            batHighCap=batHighCap,
            gridCharge=gridCharge,
            timeChae1=timeChae1,
            timeChae2=timeChae2,
            timeChaf1=timeChaf1,
            timeChaf2=timeChaf2,
        )
        return self._request("updateChargeConfigInfo", params, method="POST")

    def getDisChargeConfigInfo(self, sysSn: str) -> JsonType:
        """According to SN discharge setting information"""
        params = dict(synSn=sysSn)
        return self._request("getDisChargeConfigInfo", params)

    def updateDisChargeConfigInfo(
        self,
        sysSn: str,
        batUseCap: float,
        ctrDis: int,
        timeDise1: str,
        timeDise2: str,
        timeDisf1: str,
        timeDisf2: str,
    ) -> JsonType:
        """According SN to Set discharge information"""
        params = dict(
            sysSn=sysSn,
            batUseCap=batUseCap,
            ctrDis=ctrDis,
            timeDise1=timeDise1,
            timeDise2=timeDise2,
            timeDisf1=timeDisf1,
            timeDisf2=timeDisf2,
        )
        return self._request("updateDisChargeConfigInfo", params, method="POST")

    def getVerificationCode(self, sysSn: str, checkCode: str) -> JsonType:
        """According to SN get the check code according to SN"""
        params = dict(sysSn=sysSn, checkCode=checkCode)
        return self._request("getVerificationCode", params)

    def bindSn(self, synSn: str, code: str) -> JsonType:
        """According to SN and check code Bind the system bind the system"""
        params = dict(synSn=synSn, code=code)
        return self._request("bindSn", params, method="POST")

    def unBindSn(self, synSn: str) -> JsonType:
        """According to SN and check code Unbind the system"""
        params = dict(synSn=synSn)
        return self._request("unBindSn", params)
