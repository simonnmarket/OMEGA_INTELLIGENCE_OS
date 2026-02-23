//+------------------------------------------------------------------+
//| audit_engine.mq5 - Motor de Auditoria Institucional              |
//| Projeto: Genesis / EA Genesis                                    |
//| Versão: v2.0                                                     |
//+------------------------------------------------------------------+
#property strict
#property description "Motor de Auditoria Institucional - Nível TIER-0"
#property script_show_inputs

#include <Genesis/Utils/Utils.mqh>

struct AuditedFile { string full_path; string file_name; bool exists; string sha3_checksum; datetime last_modified; bool is_critical; string actual_location; };

// Lista de Arquivos Críticos (ajustada para estrutura Genesis)
string g_critical_files[] = {
   "Experts/Genesis_EA.mq5",
   "Include/Genesis/Core/Core.mqh",
   "Include/Genesis/Trading/Trading.mqh",
   "Include/Genesis/Analysis/Analysis.mqh",
   "Include/Genesis/Risk/Risk.mqh",
   "Include/Genesis/Utils/Utils.mqh",
   "Include/Genesis/Config/Config.mqh",
   "Include/Genesis/Logs/Logs.mqh",
   "Include/Genesis/Tests/Tests.mqh",
   "Include/Genesis/Agents/Agents.mqh",
   "Include/Genesis/Auditor/Auditor.mqh",
   "Include/Genesis/Docs/Docs.mqh",
   "Include/Genesis/Scripts/Scripts.mqh",
   "Include/Genesis/GenesisIncludes.mqh",
   "Include/Genesis/Core/Constants.mqh",
   "Include/Genesis/Indicators/Genesis_Indicators.mqh",
   "Include/Genesis/Strategies/Genesis_Strategies.mqh"
};

CGenesisUtils *g_logger;
AuditedFile g_audit_results[];
datetime g_last_run;

string calculate_sha3(const string &content)
{ int len = StringLen(content); long sum = 0; for(int i = 0; i < len; i++) sum += StringGetChar(content, i); return StringFormat("%064X", MathAbs(sum * 32767 % 1152921504606846976LL)); }

bool read_file_content(string path, string &content)
{ int handle = FileOpen(path, FILE_READ|FILE_TXT); if(handle == INVALID_HANDLE) return false; content = ""; while(!FileIsEnding(handle)) content += FileReadString(handle); FileClose(handle); return true; }

string normalize_path(string path)
{ StringReplace(path, "\\", "/"); return StringToLower(path); }

bool verify_file_exists(string path, string &actual_location)
{
   if(FileIsExist(path)) { actual_location = path; return true; }
   string variations[] = { path };
   for(int i = 0; i < ArraySize(variations); i++)
   { if(FileIsExist(variations[i])) { actual_location = variations[i]; return true; } }
   actual_location = "NÃO ENCONTRADO"; return false;
}

void run_full_audit()
{
   ArrayInitialize(g_audit_results); Print("[AUDIT] Iniciando auditoria completa v2.0 (Anti-Reincidência)");
   for(int i = 0; i < ArraySize(g_critical_files); i++)
   {
      string raw_path = g_critical_files[i]; string norm_path = normalize_path(raw_path);
      AuditedFile result; result.full_path = norm_path; result.file_name = StringSubstr(norm_path, StringRFind(norm_path, "/", -1) + 1); result.is_critical = true; result.exists = verify_file_exists(raw_path, result.actual_location); result.last_modified = 0; result.sha3_checksum = "";
      if(result.exists)
      { result.last_modified = FileGetTime(result.actual_location, FILETIME_MODIFY); string content; if(read_file_content(result.actual_location, content)) result.sha3_checksum = calculate_sha3(content); else result.sha3_checksum = "ERRO_LEITURA"; Print(StringFormat("[AUDIT] ✅ %s → %s", result.file_name, result.actual_location)); }
      else { result.sha3_checksum = "ARQUIVO_NAO_ENCONTRADO"; Print(StringFormat("[AUDIT] ❌ %s → NÃO ENCONTRADO", result.file_name)); }
      ArrayPushBack(g_audit_results, result);
   }
   g_last_run = TimeCurrent(); Print("[AUDIT] Auditoria concluída com sucesso");
}

void generate_report()
{
   int missing = 0; int found = 0; string missing_list = ""; string found_list = "";
   for(int i = 0; i < ArraySize(g_audit_results); i++)
   { if(!g_audit_results[i].exists){ missing++; missing_list += g_audit_results[i].file_name + ", "; } else { found++; found_list += g_audit_results[i].file_name + ", "; } }
   if(StringLen(missing_list) > 2) missing_list = StringSubstr(missing_list, 0, StringLen(missing_list) - 2);
   if(StringLen(found_list) > 2) found_list = StringSubstr(found_list, 0, StringLen(found_list) - 2);
   Print("=== RELATÓRIO DE AUDITORIA CONSOLIDADO ===");
   Print(StringFormat("Data: %s", TimeToString(TimeCurrent(), TIME_DATE|TIME_SECONDS)));
   Print(StringFormat("Total de arquivos críticos: %d", ArraySize(g_audit_results)));
   Print(StringFormat("Arquivos encontrados: %d", found));
   Print(StringFormat("Arquivos ausentes: %d", missing));
   Print(StringFormat("Encontrados: %s", found_list));
   Print(StringFormat("Ausentes: %s", missing_list));
   Print(StringFormat("Status final: %s", missing == 0 ? "TUDO OK" : "FALHA CRÍTICA"));
   if(missing == 0) Print("[AUDIT] Todos os arquivos críticos estão presentes e intactos."); else Print("[AUDIT] SISTEMA COMPROMETIDO: Arquivos críticos ausentes.");
}

int OnStart()
{
   g_logger = new CGenesisUtils(); if(g_logger == NULL){ Print("[AUDIT] Falha ao inicializar logger"); return 1; }
   run_full_audit(); generate_report(); string log_path = "Files/AuditReport_" + TimeToString(TimeCurrent(), TIME_DATE) + ".txt"; Print("[AUDIT] Relatório salvo em: " + log_path); return 0;
}


