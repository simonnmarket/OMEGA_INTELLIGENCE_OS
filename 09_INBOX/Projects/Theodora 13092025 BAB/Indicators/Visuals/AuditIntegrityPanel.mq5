#property indicator_separate_window
#property indicator_buffers 0
#property indicator_plots   0
#property strict

// AuditIntegrityPanel.mq5 - Gera relatório de integridade do projeto Theodora

input string ReportDirectory = "AUDITOR";

int OnInit()
{
   string path = ReportDirectory + "/";
   if(!FolderCreate(path))
   {
      Print("[AUDIT] Falha ao criar diretório de relatório: ", GetLastError());
   }

   string filename = path + "RELATORIO_INTEGRIDADE_" + TimeToString(TimeCurrent(), TIME_DATE) + ".log";
   int handle = FileOpen(filename, FILE_WRITE|FILE_TXT|FILE_ANSI);
   if(handle == INVALID_HANDLE)
   {
      Print("[AUDIT] Falha ao abrir arquivo de relatório: ", GetLastError());
      return(INIT_FAILED);
   }

   // Verificações básicas
   bool web_ok = TerminalInfoInteger(TERMINAL_WEBREQUEST_ENABLED);
   FileWrite(handle, "WEBREQUEST_ENABLED=" + (web_ok?"1":"0"));

   // MT5 build
   FileWrite(handle, "BUILD=" + (string)TerminalInfoInteger(TERMINAL_BUILD));

   // Símbolos essenciais
   string required[] = {"BTCUSD","ETHUSD","SOLUSD"};
   for(int i=0;i<ArraySize(required);i++)
   {
      bool selected = SymbolSelect(required[i], true);
      FileWrite(handle, "SYMBOL_"+required[i]+"=" + (selected?"OK":"FAIL"));
   }

   FileClose(handle);
   // Também gravar em Common Files para facilitar localização
   string filename_common = path + "RELATORIO_INTEGRIDADE_COMMON_" + TimeToString(TimeCurrent(), TIME_DATE) + ".log";
   int handle_common = FileOpen(filename_common, FILE_WRITE|FILE_TXT|FILE_COMMON|FILE_ANSI);
   if(handle_common != INVALID_HANDLE)
   {
      FileWrite(handle_common, "WEBREQUEST_ENABLED=" + (web_ok?"1":"0"));
      FileWrite(handle_common, "BUILD=" + (string)TerminalInfoInteger(TERMINAL_BUILD));
      for(int j=0;j<ArraySize(required);j++)
      {
         bool sel = SymbolSelect(required[j], true);
         FileWrite(handle_common, "SYMBOL_"+required[j]+"=" + (sel?"OK":"FAIL"));
      }
      FileClose(handle_common);
   }

   // Informar caminhos absolutos
   string data_path = TerminalInfoString(TERMINAL_DATA_PATH);
   Print("[AUDIT] Relatório (Local Files): ", data_path, "\\MQL5\\Files\\", filename);
   Print("[AUDIT] Relatório (Common Files): ", TerminalInfoString(TERMINAL_COMMONDATA_PATH), "\\Files\\", filename_common);
   return(INIT_SUCCEEDED);
}

int OnCalculate(const int rates_total,
                const int prev_calculated,
                const int begin,
                const double &price[])
{
   return(rates_total);
}


