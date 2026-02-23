//+------------------------------------------------------------------+
//| WinInet.mqh - Windows Internet Functions                          |
//+------------------------------------------------------------------+
#property copyright "Quantum Trading Labs"
#property link      "https://www.quantumtrading.foundation"
#property version   "1.0"
#property strict

// Constants
#define INTERNET_OPEN_TYPE_PRECONFIG 0
#define INTERNET_FLAG_RELOAD 0x80000000
#define INTERNET_FLAG_DONT_CACHE 0x04000000
#define INTERNET_FLAG_SECURE 0x00800000
#define INTERNET_FLAG_IGNORE_CERT_CN_INVALID 0x00001000
#define INTERNET_FLAG_IGNORE_CERT_DATE_INVALID 0x00002000
#define INTERNET_FLAG_IGNORE_REDIRECT_TO_HTTPS 0x00004000
#define INTERNET_FLAG_IGNORE_REDIRECT_TO_HTTP 0x00008000
#define INTERNET_FLAG_NO_AUTH 0x00040000
#define INTERNET_FLAG_NO_AUTO_REDIRECT 0x00200000
#define INTERNET_FLAG_NO_COOKIES 0x00080000
#define INTERNET_FLAG_NO_UI 0x00000200
#define INTERNET_FLAG_PRAGMA_NOCACHE 0x00000100
#define INTERNET_FLAG_RELOAD 0x80000000
#define INTERNET_FLAG_RESYNCHRONIZE 0x00000800
#define INTERNET_FLAG_TRANSFER_ASCII 0x00000001
#define INTERNET_FLAG_TRANSFER_BINARY 0x00000002

// Function declarations
#import "wininet.dll"
   int InternetOpenW(string lpszAgent, int dwAccessType, string lpszProxy, string lpszProxyBypass, int dwFlags);
   int InternetConnectW(int hInternet, string lpszServerName, int nServerPort, string lpszUserName, string lpszPassword, int dwService, int dwFlags, int dwContext);
   int HttpOpenRequestW(int hConnect, string lpszVerb, string lpszObjectName, string lpszVersion, string lpszReferrer, string lpszAcceptTypes, int dwFlags, int dwContext);
   int HttpSendRequestW(int hRequest, string lpszHeaders, int dwHeadersLength, string lpOptional, int dwOptionalLength);
   int InternetReadFile(int hFile, uchar &lpBuffer[], int dwNumberOfBytesToRead, int &lpdwNumberOfBytesRead);
   int InternetCloseHandle(int hInternet);
   int HttpQueryInfoW(int hRequest, int dwInfoLevel, string &lpvBuffer, int &lpdwBufferLength, int &lpdwIndex);
#import

// Wrapper functions
int InternetOpen(string agent, int accessType, string proxy, string proxyBypass, int flags) {
   return InternetOpenW(agent, accessType, proxy, proxyBypass, flags);
}

int InternetConnect(int hInternet, string serverName, int serverPort, string userName, string password, int service, int flags, int context) {
   return InternetConnectW(hInternet, serverName, serverPort, userName, password, service, flags, context);
}

int HttpOpenRequest(int hConnect, string verb, string objectName, string version, string referrer, string acceptTypes, int flags, int context) {
   return HttpOpenRequestW(hConnect, verb, objectName, version, referrer, acceptTypes, flags, context);
}

int HttpSendRequest(int hRequest, string headers, int headersLength, string optional, int optionalLength) {
   return HttpSendRequestW(hRequest, headers, headersLength, optional, optionalLength);
}

bool HttpQueryInfo(int hRequest, int infoLevel, string &buffer, int &bufferLength, int &index) {
   return HttpQueryInfoW(hRequest, infoLevel, buffer, bufferLength, index);
} 