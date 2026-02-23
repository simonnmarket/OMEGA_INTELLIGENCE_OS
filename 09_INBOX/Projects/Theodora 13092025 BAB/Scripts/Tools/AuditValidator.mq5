//+------------------------------------------------------------------+
//| Script: AuditValidator.mq5 - Theodora v3.0 Pre-Activation Audit  |
//| Descrição: Validação completa do ambiente antes da ativação      |
//|            do sistema Theodora v3.0                              |
//+------------------------------------------------------------------+
#property copyright "Theodora Quantum Trading"
#property link      "https://www.theodora-quantum.com"
#property version   "3.0"
#property strict
#property description "Validador de ambiente para Theodora v3.0 - Verifica todas as condições críticas"
#property description "Executar antes de ativar o sistema principal"
#property script_show_inputs

//--- Inputs configuráveis
input string   BackendURL         = "http://127.0.0.1:5000/health";  // URL do backend Theodora
input string   SymbolsCSV         = "BTCUSD,ETHUSD,SOLUSD,XAUUSD,EURUSD"; // Símbolos para validar
input int      WebRequestTimeout  = 5000;                            // Timeout em ms
input bool     EnableDetailedLogs = true;                            // Logs detalhados
input bool     CreateFiles        = true;                            // Criar arquivos de log

//--- Constantes
const string   AUDIT_FOLDER       = "TheodoraAudit/";
const string   COMMON_FOLDER      = "TheodoraAudit/Common/";

//+------------------------------------------------------------------+
//| Função de log melhorada                                          |
//+------------------------------------------------------------------+
void PrintResult(string label, bool ok, string details = "")
{
   string status = ok ? "OK" : "FAIL";
   string message = StringFormat("[AUDIT] %-25s = %s", label, status);
   
   if(details != "")
      message += " | " + details;
   
   Print(message);
}

//+------------------------------------------------------------------+
//| Função para trim de string                                       |
//+------------------------------------------------------------------+
string StringTrim(string str)
{
   StringTrimLeft(str);
   StringTrimRight(str);
   return str;
}

//+------------------------------------------------------------------+
//| Verificar conexão WebRequest                                     |
//+------------------------------------------------------------------+
bool TestWebRequest(string url, int timeout, int &error_code, string &response)
{
   uchar data[];
   uchar result_data[];
   string result_headers;
   ResetLastError();
   
   int status = WebRequest("GET", url, "", timeout, data, result_data, result_headers);
   error_code = GetLastError();
   
   if(status == 200)
   {
      response = CharArrayToString(result_data);
      return true;
   }
   
   return false;
}

//+------------------------------------------------------------------+
//| Verificar saúde do backend                                       |
//+------------------------------------------------------------------+
bool TestBackendHealth(string url, int timeout)
{
   int error_code;
   string response;
   
   if(!TestWebRequest(url, timeout, error_code, response))
      return false;
   
   // Múltiplos padrões de resposta possíveis
   string patterns[] = {
      "\"status\":\"ok\"",
      "\"status\": \"ok\"", 
      "\"healthy\":true",
      "\"online\":true",
      "ok",
      "success"
   };
   
   for(int i = 0; i < ArraySize(patterns); i++)
   {
      if(StringFind(response, patterns[i]) >= 0)
         return true;
   }
   
   return false;
}

//+------------------------------------------------------------------+
//| Validar símbolos                                                 |
//+------------------------------------------------------------------+
bool ValidateSymbols(string symbols_csv, string &missing_symbols[])
{
   string symbols[];
   int count = StringSplit(symbols_csv, ',', symbols);
   bool all_ok = true;
   
   ArrayResize(missing_symbols, 0);
   
   for(int i = 0; i < count; i++)
   {
      string sym = StringTrim(symbols[i]);
      if(StringLen(sym) == 0)
         continue;
         
      // Tentar selecionar o símbolo
      bool symbol_available = SymbolSelect(sym, true);
      
      if(!symbol_available)
      {
         all_ok = false;
         ArrayResize(missing_symbols, ArraySize(missing_symbols) + 1);
         missing_symbols[ArraySize(missing_symbols) - 1] = sym;
      }
      
      // Verificar informações adicionais do símbolo
      if(symbol_available)
      {
         double bid = SymbolInfoDouble(sym, SYMBOL_BID);
         double ask = SymbolInfoDouble(sym, SYMBOL_ASK);
         bool prices_ok = (bid > 0 && ask > 0 && ask > bid);
         
         PrintResult("SYMBOL_" + sym, symbol_available, 
                    prices_ok ? "Prices OK" : "No prices");
      }
      else
      {
         PrintResult("SYMBOL_" + sym, false, "Not available");
      }
   }
   
   return all_ok;
}

//+------------------------------------------------------------------+
//| Verificar permissões de trading                                  |
//+------------------------------------------------------------------+
bool CheckTradingPermissions()
{
   // Verificar se trading é permitido
   if(!TerminalInfoInteger(TERMINAL_TRADE_ALLOWED))
   {
      PrintResult("TRADING_ALLOWED", false, "Terminal não permite trading");
      return false;
   }
   
   // Verificar permissões da conta
   if(!AccountInfoInteger(ACCOUNT_TRADE_EXPERT))
   {
      PrintResult("EXPERT_TRADING", false, "Conta não permite EAs");
      return false;
   }
   
   // Verificar se conta é demo ou real
   int trade_mode = (int)AccountInfoInteger(ACCOUNT_TRADE_MODE);
   bool is_demo = (trade_mode == ACCOUNT_TRADE_MODE_DEMO);
   PrintResult("ACCOUNT_TYPE", true, is_demo ? "DEMO" : "REAL");
   
   return true;
}

//+------------------------------------------------------------------+
//| Verificar recursos do sistema                                    |
//+------------------------------------------------------------------+
void CheckSystemResources()
{
   // Memória disponível
   long free_mem = TerminalInfoInteger(TERMINAL_MEMORY_AVAILABLE);
   PrintResult("MEMORY_AVAILABLE", free_mem > 100000000, 
              StringFormat("%.1f MB", free_mem / 1024.0 / 1024.0));
   
   // CPU cores
   int cpu_cores = (int)TerminalInfoInteger(TERMINAL_CPU_CORES);
   PrintResult("CPU_CORES", cpu_cores >= 2, 
              StringFormat("%d cores", cpu_cores));
   
   // Build version
   int build = (int)TerminalInfoInteger(TERMINAL_BUILD);
   PrintResult("MT5_BUILD", build >= 2000, 
              StringFormat("Build %d", build));
}

//+------------------------------------------------------------------+
//| Salvar resultados em arquivo                                     |
//+------------------------------------------------------------------+
void SaveAuditResults(bool web_ok, bool backend_ok, bool symbols_ok, 
                     bool trading_ok, string &missing_symbols[])
{
   if(!CreateFiles)
      return;
   
   // Criar pastas se não existirem
   FolderCreate(AUDIT_FOLDER);
   FolderCreate(COMMON_FOLDER);
   
   string timestamp = TimeToString(TimeCurrent(), TIME_DATE|TIME_MINUTES);
   // Sanitizar timestamp para nome de arquivo (evita ':' e espaço)
   StringReplace(timestamp, ":", "-");
   StringReplace(timestamp, " ", "_");
   string filename_local = AUDIT_FOLDER + "AUDIT_" + timestamp + ".log";
   // Em Common Files, use nome plano; FILE_COMMON não cria subpastas
   string filename_common_plain = "THEODORA_AUDIT_" + timestamp + ".log";
   
   // Salvar em arquivo local
   int fh = FileOpen(filename_local, FILE_WRITE|FILE_TXT|FILE_ANSI);
   if(fh != INVALID_HANDLE)
   {
      FileWrite(fh, "THEODORA v3.0 AUDIT REPORT");
      FileWrite(fh, "Timestamp: " + timestamp);
      FileWrite(fh, "========================================");
      FileWrite(fh, "WEBREQUEST_ENABLED=" + (web_ok ? "1" : "0"));
      FileWrite(fh, "BACKEND_HEALTH=" + (backend_ok ? "1" : "0"));
      FileWrite(fh, "SYMBOLS_AVAILABLE=" + (symbols_ok ? "1" : "0"));
      FileWrite(fh, "TRADING_PERMISSIONS=" + (trading_ok ? "1" : "0"));
      FileWrite(fh, "OVERALL_RESULT=" + (web_ok && backend_ok && symbols_ok && trading_ok ? "PASS" : "FAIL"));
      
      if(!symbols_ok && ArraySize(missing_symbols) > 0)
      {
         FileWrite(fh, "MISSING_SYMBOLS: " + ArrayToString(missing_symbols, ","));
      }
      
      FileWrite(fh, "========================================");
      FileClose(fh);
   }
   
   // Salvar em Common Files (pasta raiz comum)
   int fh_common = FileOpen(filename_common_plain, FILE_WRITE|FILE_TXT|FILE_COMMON|FILE_ANSI);
   if(fh_common != INVALID_HANDLE)
   {
      FileWrite(fh_common, "THEODORA v3.0 AUDIT REPORT (COMMON)");
      FileWrite(fh_common, "Timestamp: " + timestamp);
      FileWrite(fh_common, "========================================");
      FileWrite(fh_common, "WEBREQUEST_ENABLED=" + (web_ok ? "1" : "0"));
      FileWrite(fh_common, "BACKEND_HEALTH=" + (backend_ok ? "1" : "0"));
      FileWrite(fh_common, "SYMBOLS_AVAILABLE=" + (symbols_ok ? "1" : "0"));
      FileWrite(fh_common, "TRADING_PERMISSIONS=" + (trading_ok ? "1" : "0"));
      FileWrite(fh_common, "OVERALL_RESULT=" + (web_ok && backend_ok && symbols_ok && trading_ok ? "PASS" : "FAIL"));
      FileClose(fh_common);
      Print("[AUDIT] COMMON salvo: ", TerminalInfoString(TERMINAL_COMMONDATA_PATH), "\\Files\\", filename_common_plain);
   }
   else
   {
      Print("[AUDIT] Falha ao abrir COMMON: ", filename_common_plain, ", err=", GetLastError());
      Print("[AUDIT] Common base: ", TerminalInfoString(TERMINAL_COMMONDATA_PATH), "\\Files\\");
   }
}

//+------------------------------------------------------------------+
//| Funções utilitárias                                              |
//+------------------------------------------------------------------+
string ArrayToString(string &array[], string delimiter)
{
   string result = "";
   for(int i = 0; i < ArraySize(array); i++)
   {
      if(i > 0) result += delimiter;
      result += array[i];
   }
   return result;
}

//+------------------------------------------------------------------+
//| Função principal                                                 |
//+------------------------------------------------------------------+
void OnStart()
{
   Print("========================================================");
   Print("THEODORA v3.0 - AUDIT VALIDATOR");
   Print("Iniciando validação completa do ambiente...");
   Print("========================================================");
   
   int error_code;
   string response;
   string missing_symbols[];
   
   // 1. Testar WebRequest
   bool web_ok = TestWebRequest(BackendURL, WebRequestTimeout, error_code, response);
   PrintResult("WEBREQUEST_CAPABILITY", web_ok, 
              web_ok ? "Connected" : "Error: " + IntegerToString(error_code));
   
   // 2. Testar Backend Health
   bool backend_ok = false;
   if(web_ok)
   {
      backend_ok = TestBackendHealth(BackendURL, WebRequestTimeout);
      PrintResult("BACKEND_HEALTH", backend_ok, 
                 backend_ok ? "Online" : "Offline or invalid response");
   }
   else
   {
      PrintResult("BACKEND_HEALTH", false, "WebRequest failed");
   }
   
   // 3. Validar símbolos
   bool symbols_ok = ValidateSymbols(SymbolsCSV, missing_symbols);
   PrintResult("ALL_SYMBOLS_AVAILABLE", symbols_ok,
              symbols_ok ? "All symbols ready" : "Missing symbols detected");
   
   // 4. Verificar permissões de trading
   bool trading_ok = CheckTradingPermissions();
   
   // 5. Verificar recursos do sistema
   CheckSystemResources();
   
   // 6. Resultado final
   bool overall_result = web_ok && backend_ok && symbols_ok && trading_ok;
   Print("========================================================");
   PrintResult("OVERALL_AUDIT_RESULT", overall_result,
              overall_result ? "SYSTEM READY FOR THEODORA v3.0" : "SYSTEM NOT READY");
   Print("========================================================");
   
   // 7. Salvar resultados
   SaveAuditResults(web_ok, backend_ok, symbols_ok, trading_ok, missing_symbols);
   
   // 8. Recomendações se falhou
   if(!overall_result)
   {
      Print("RECOMENDAÇÕES:");
      
      if(!web_ok)
         Print("• Habilite WebRequest em: Tools > Options > Expert Advisors");
      
      if(web_ok && !backend_ok)
         Print("• Verifique se o backend Theodora está rodando em: " + BackendURL);
      
      if(!symbols_ok)
         Print("• Adicione os símbolos faltantes ao Market Watch: " + ArrayToString(missing_symbols, ", "));
      
      if(!trading_ok)
         Print("• Verifique permissões de trading na conta");
   }
   else
   {
      Print("✅ Ambiente validado com sucesso!");
      Print("Theodora v3.0 pode ser ativado com segurança.");
   }
}
//+------------------------------------------------------------------+