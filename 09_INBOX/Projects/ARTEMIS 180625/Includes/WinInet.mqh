//+------------------------------------------------------------------+
//|                                                      WinInet.mqh |
//|                             Copyright 2009-2021, MetaQuotes Software Corp. |
//|                                       https://www.mql5.com                    |
//+------------------------------------------------------------------+

#include <WinAPI.mqh>

//--- InternetOpen() flags
#define INTERNET_OPEN_TYPE_PRECONFIG              0
#define INTERNET_OPEN_TYPE_DIRECT                 1
#define INTERNET_OPEN_TYPE_PROXY                  3

//--- InternetConnect() service types
#define INTERNET_SERVICE_FTP                      1
#define INTERNET_SERVICE_GOPHER                   2
#define INTERNET_SERVICE_HTTP                     3

//--- HttpOpenRequest() flags
#define INTERNET_FLAG_RELOAD                      0x80000000
#define INTERNET_FLAG_RAW_DATA                    0x40000000
#define INTERNET_FLAG_EXISTING_CONNECTION         0x20000000
#define INTERNET_FLAG_SECURE                      0x00800000

//--- Security protocols
#define WININET_FLAG_USE_SECURITY_PROTOCOL_TLS1_0  0x00000001
#define WININET_FLAG_USE_SECURITY_PROTOCOL_TLS1_1  0x00000002
#define WININET_FLAG_USE_SECURITY_PROTOCOL_TLS1_2  0x00000004
#define WININET_FLAG_USE_SECURITY_PROTOCOL_ANY      (WININET_FLAG_USE_SECURITY_PROTOCOL_TLS1_0 | \
                                                     WININET_FLAG_USE_SECURITY_PROTOCOL_TLS1_1 | \
                                                     WININET_FLAG_USE_SECURITY_PROTOCOL_TLS1_2)

//--- InternetOpen() - initializes the WinInet functions
int InternetOpenW(string agent, int access_type, string proxy = "", string proxy_bypass = "", int flags = 0)
{
   return(WinAPI_InternetOpenW(agent, access_type, proxy, proxy_bypass, flags));
}

//--- InternetConnect() - connects to an Internet server
int InternetConnectW(int h_connect, string server_name, int server_port, string username = "", string password = "", int service = 0, int flags = 0, int context = 0)
{
   return(WinAPI_InternetConnectW(h_connect, server_name, server_port, username, password, service, flags, context));
}

//--- HttpOpenRequest() - opens an HTTP request handle
int HttpOpenRequestW(int h_connect, string verb, string object_name, string version = "", string referrer = "", string* accept_types = NULL, int flags = 0, int context = 0)
{
   return(WinAPI_HttpOpenRequestW(h_connect, verb, object_name, version, referrer, accept_types, flags, context));
}

//--- HttpSendRequest() - sends the HTTP request to the server
bool HttpSendRequestW(int h_request, string headers = "", string optional = "", int optional_total = 0)
{
   return(WinAPI_HttpSendRequestW(h_request, headers, optional, optional_total));
}

//--- InternetReadFile() - reads data from an open Internet file handle
string InternetReadFileW(int h_file, int bytes_to_read = 65536)
{
   char buffer[];
   uint total_bytes_read = 0;
   string result = "";

   while(true)
   {
      uint bytes_read = 0;
      if(!WinAPI_InternetReadFile(h_file, buffer, MathMin(bytes_to_read, ArraySize(buffer)), bytes_read))
         break;

      if(bytes_read == 0)
         break;

      total_bytes_read += bytes_read;
      result += CharArrayToString(buffer, 0, bytes_read);
      if(total_bytes_read >= bytes_to_read)
         break;
   }

   return(result);
}

//--- InternetCloseHandle() - closes an open Internet handle
bool InternetCloseHandle(int h_handle)
{
   return(WinAPI_InternetCloseHandle(h_handle));
}

//--- HttpAddRequestHeaders() - adds HTTP headers to a request
bool HttpAddRequestHeadersW(int h_request, string headers, int dwModifiers = 0)
{
   return(WinAPI_HttpAddRequestHeadersW(h_request, headers, StringLen(headers), dwModifiers));
}

//--- HttpSendRequestEx() - sends HTTP request header
bool HttpSendRequestExW(int h_request, int total_length = -1, int context = 0)
{
   return(WinAPI_HttpSendRequestExW(h_request, total_length, context));
}

//--- HttpEndRequest() - ends an HTTP request
bool HttpEndRequestW(int h_request, int context = 0)
{
   return(WinAPI_HttpEndRequestW(h_request, context));
}

//--- InternetSetOption() - sets options for handles
bool InternetSetOptionW(int h_request, int option, void* buffer, int buffer_length)
{
   return(WinAPI_InternetSetOptionW(h_request, option, buffer, buffer_length));
}

//--- Utility: Converts char array to string
string CharArrayToString(char &arr[], int start = 0, int count = -1)
{
   if(count == -1)
      count = ArraySize(arr) - start;

   uchar ustr[];
   ArrayResize(ustr, count);

   for(int i = 0; i < count; i++)
      ustr[i] = arr[start + i];

   return(UShortArrayToString(ustr));
}

//--- Utility: Converts UShort array to string
string UShortArrayToString(uchar &arr[])
{
   string res = "";
   for(int i = 0; i < ArraySize(arr); i++)
      res += ShortToString(arr[i], 0);
   return(res);
} 