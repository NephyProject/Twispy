# coding=utf-8
import binascii
import datetime
import hashlib
import hmac
import json
import time
import urllib.parse
import uuid
from collections import OrderedDict


def escape(text):
	if isinstance(text, dict):
		text = json.dumps(text, ensure_ascii=False).replace(" ", "")
	return urllib.parse.quote(text, safe="~")

def getCurrentEpochTime():
	return int(time.mktime(datetime.datetime.now().timetuple()))

def getUUID():
	return str(uuid.uuid4()).upper()

def makeHeader(method, url, uuid=None, deviceId=None, headerType=None):
	if not headerType:
		headerType = 0

	header = OrderedDict()
	if headerType == 0:
		header["Host"] = url.replace("https://", "").split("/")[0]
		header["Authorization"] = None
		header["X-Twitter-Client-Version"] = "6.59.3"
		header["Accept"] = "*/*"
		header["X-Client-UUID"] = uuid if uuid else getUUID()
		header["X-Twitter-Client-Language"] = "ja"
		header["X-B3-TraceId"] = hashlib.md5(str(getCurrentEpochTime()).encode()).hexdigest()[0:16]
		header["Accept-Language"] = "ja"
		header["Accept-Encoding"] = "gzip, deflate"
		header["X-Twitter-Client-DeviceID"] = deviceId if deviceId else getUUID()
		if method == "POST":
			header["Content-Type"] = "application/x-www-form-urlencoded"
			header["Content-Length"] = None
		header["User-Agent"] = "Twitter-iPhone/6.59.3 iOS/9.3.3 (Apple;iPhone8,2;;;;;1)"
		header["X-Twitter-Client-Limit-Ad-Tracking"] = "1"
		header["X-Twitter-API-Version"] = "5"
		header["X-Twitter-Client"] = "Twitter-iPhone"
	elif headerType == 1:
		header["Host"] = url.replace("https://", "").split("/")[0]
		header["Authorization"] = None
		header["X-Twitter-Client-Version"] = "6.59.3"
		header["X-Twitter-Polling"] = "true"
		header["X-Client-UUID"] = uuid if uuid else getUUID()
		header["X-Twitter-Client-Language"] = "ja"
		header["X-B3-TraceId"] = hashlib.md5(str(getCurrentEpochTime()).encode()).hexdigest()[0:16]
		header["x-spdy-bypass"] = "1"
		header["Accept"] = "*/*"
		header["Accept-Language"] = "ja"
		header["Accept-Encoding"] = "gzip, deflate"
		header["X-Twitter-Client-DeviceID"] = deviceId if deviceId else getUUID()
		header["User-Agent"] = "Twitter-iPhone/6.59.3 iOS/9.3.3 (Apple;iPhone8,2;;;;;1)"
		header["X-Twitter-API-Version"] = "5"
		header["X-Twitter-Client-Limit-Ad-Tracking"] = "1"
		header["X-Twitter-Client"] = "Twitter-iPhone"
	return header

def makeImageHeader(url):
	# https://abs.twimg.com/sticky/default_profile_images/default_profile_[0-6]_400x400.png
	header = OrderedDict()
	header["Host"] = url.replace("https://", "").split("/")[0]
	header["Accept"] = "*/*"
	header["User-Agent"] = "Twitter/6.59.3 CFNetwork/758.5.3 Darwin/15.6.0"
	header["Accept-Language"] = "ja-jp"
	header["Accept-Encoding"] = "gzip, deflate"
	return header

def makeVideoHeader(url, sessionId):
	# http://amp.twimg.com/prod/multibr_v_1/video/2016/08/30/14/770627528612536321-libx264-baseline-1264k_00000.ts
	# http://amp.twimg.com/prod/multibr_v_1/video/2016/08/30/14/770627528612536321-libx264-baseline-1264k.m3u8?doxj4Q2mMk%2FyasGp9MQivv8BeYAJbs3%2Fi0Lf70X4hZY%3D HTTP/1.1
	header = OrderedDict()
	header["Host"] = url.replace("https://", "").split("/")[0]
	header["X-Playback-Session-Id"] = sessionId
	header["Accept"] = "*/*"
	header["User-Agent"] = "AppleCoreMedia/1.0.0.13G34 (iPhone; U; CPU OS 9_3_3 like Mac OS X; ja_jp)"
	header["Accept-Language"] = "ja-jp"
	header["Accept-Encoding"] = "identity"
	return header

def makeVmapHeader(url):
	# https://amp.twimg.com/prod/multibr_v_1/vmap/2016/08/30/14/770627528612536321/0a1b6b69-d4cc-4b0f-86fb-a04678c99760.vmap
	header = OrderedDict()
	header["Host"] = url.replace("https://", "").split("/")[0]
	header["Accept"] = "*/*"
	header["User-Agent"] = "Twitter-iPhone/6.59.3 iOS/9.3.3 (Apple;iPhone8,2)"
	header["Accept-Language"] = "ja-jp"
	header["Accept-Encoding"] = "gzip, deflate"
	return header

def makeAuthorizationData(ck, at):
	authorizationData = OrderedDict()
	authorizationData["oauth_signature"] = None
	authorizationData["oauth_nonce"] = getUUID()
	authorizationData["oauth_timestamp"] = str(getCurrentEpochTime())
	authorizationData["oauth_consumer_key"] = ck
	authorizationData["oauth_token"] = at
	authorizationData["oauth_version"] = "1.0"
	authorizationData["oauth_signature_method"] = "HMAC-SHA1"
	return authorizationData

def makeSignatureBase(method, header, data, authorizationData, ck, at):
	signatureBase = []
	if (method.upper() == "POST" and header["Content-Type"] == "application/x-www-form-urlencoded") or method.upper() != "POST":
		for key, value in data.items():
			signatureBase.append([escape(key), escape(value)])

	signatureBase.append(["oauth_consumer_key", ck])
	signatureBase.append(["oauth_nonce", authorizationData["oauth_nonce"]])
	signatureBase.append(["oauth_signature_method", "HMAC-SHA1"])
	signatureBase.append(["oauth_timestamp", authorizationData["oauth_timestamp"]])
	signatureBase.append(["oauth_version", "1.0"])
	signatureBase.append(["oauth_token", at])
	signatureBase.sort()
	return signatureBase

def makeSignatureBaseString(method, url, signatureBase):
	return "{}&{}&{}".format(method.upper(), escape(url), escape("&".join(["{}={}".format(key, value) for key, value in signatureBase])))

def makeSigningKey(cs, ats):
	return "{}&{}".format(escape(cs), escape(ats))

def makeOAuthSignature(signingKey, signatureBaseString):
	return escape(binascii.b2a_base64(hmac.new(signingKey.encode(), signatureBaseString.encode(), hashlib.sha1).digest())[:-1])

def makeAuthorizationHeader(authorizationData):
	return "OAuth " + ", ".join(["{key}=\"{value}\"".format(key=x, value=y) for x, y in authorizationData.items()])
