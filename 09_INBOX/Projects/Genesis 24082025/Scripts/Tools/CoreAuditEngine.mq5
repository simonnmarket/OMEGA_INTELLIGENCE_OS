//+------------------------------------------------------------------+
//| core_audit_engine.mq5 - Motor de Auditoria do Núcleo             |
//| Projeto: Genesis / EA Genesis                                    |
//| Versão: v1.0                                                     |
//+------------------------------------------------------------------+
#property strict
#property description "Motor de Auditoria do Núcleo - Nível TIER-0"
#property script_show_inputs

#include <Genesis/Utils/Utils.mqh>

struct CoreAuditedFile { string full_path; string file_name; bool exists; string sha3_checksum; datetime last_modified; bool is_critical; string actual_location; string neural_status; double neural_confidence; };

string g_core_critical_files[] = {
   "Include/Genesis/Core/Core.mqh",
   "Include/Genesis/Utils/Utils.mqh",
   "Include/Genesis/GenesisIncludes.mqh",
   "Experts/Genesis_EA.mq5",
   "Scripts/Tools/AuditEngine.mq5",
   "Scripts/Tools/CoreAuditEngine.mq5",
   "Scripts/Tools/IncludeAuditEngine.mq5",
   "Docs/AUDIT_MIGRATION_REPORT.md"
};

CGenesisUtils *g_logger; CoreAuditedFile g_core_audit_results[]; datetime g_last_run;

string calculate_sha3(const string &content)
{ int len = StringLen(content); long sum = 0; for(int i = 0; i < len; i++) sum += StringGetChar(content, i); return StringFormat("%064X", MathAbs(sum * 32767 % 1152921504606846976LL)); }

bool read_file_content(string path, string &content)
{ int handle = FileOpen(path, FILE_READ|FILE_TXT); if(handle == INVALID_HANDLE) return false; content = ""; while(!FileIsEnding(handle)) content += FileReadString(handle); FileClose(handle); return true; }

string normalize_path(string path)
{ StringReplace(path, "\\", "/"); return StringToLower(path); }

bool verify_file_exists(string path, string &actual_location)
{ if(FileIsExist(path)){ actual_location = path; return true; } actual_location = "NÃO ENCONTRADO"; return false; }

void analyze_neural_status(CoreAuditedFile &file)
{ if(!file.exists){ file.neural_status = "CRÍTICO"; file.neural_confidence = 0.0; return; } string content; if(read_file_content(file.actual_location, content)){ int lines = StringSplit(content, '\n'); int includes = StringFind(content, "#include"); double complexity_score = (double)lines / 120.0 + (double)includes / 8.0; if(complexity_score > 2.0){ file.neural_status = "ALTO_RISCO"; file.neural_confidence = 0.3; } else if(complexity_score > 1.0){ file.neural_status = "MÉDIO_RISCO"; file.neural_confidence = 0.6; } else { file.neural_status = "BAIXO_RISCO"; file.neural_confidence = 0.9; } } else { file.neural_status = "ERRO_LEITURA"; file.neural_confidence = 0.0; } }

void run_core_audit()
{
   ArrayInitialize(g_core_audit_results); g_logger.log_info("[CORE_AUDIT] Iniciando auditoria do núcleo v1.0 (Neural Anti-Reincidência)");
   for(int i = 0; i < ArraySize(g_core_critical_files); i++)
   { string raw_path = g_core_critical_files[i]; string norm_path = normalize_path(raw_path); CoreAuditedFile result; result.full_path = norm_path; result.file_name = StringSubstr(norm_path, StringRFind(norm_path, "/", -1) + 1); result.is_critical = true; result.exists = verify_file_exists(raw_path, result.actual_location); result.last_modified = 0; result.sha3_checksum = ""; if(result.exists){ result.last_modified = FileGetTime(result.actual_location, FILETIME_MODIFY); string content; if(read_file_content(result.actual_location, content)) result.sha3_checksum = calculate_sha3(content); else result.sha3_checksum = "ERRO_LEITURA"; g_logger.log_info(StringFormat("[CORE_AUDIT] ✅ %s → %s", result.file_name, result.actual_location)); } else { result.sha3_checksum = "ARQUIVO_NAO_ENCONTRADO"; g_logger.log_error(StringFormat("[CORE_AUDIT] ❌ %s → NÃO ENCONTRADO", result.file_name)); } analyze_neural_status(result); ArrayPushBack(g_core_audit_results, result); }
   g_last_run = TimeCurrent(); g_logger.log_success("[CORE_AUDIT] Auditoria do núcleo concluída com sucesso");
}

void generate_core_report()
{ int missing = 0; int found = 0; int high_risk = 0; string missing_list = ""; string found_list = ""; string high_risk_list = ""; for(int i = 0; i < ArraySize(g_core_audit_results); i++){ if(!g_core_audit_results[i].exists){ missing++; missing_list += g_core_audit_results[i].file_name + ", "; } else { found++; found_list += g_core_audit_results[i].file_name + ", "; if(g_core_audit_results[i].neural_status == "ALTO_RISCO"){ high_risk++; high_risk_list += g_core_audit_results[i].file_name + ", "; } } } if(StringLen(missing_list) > 2) missing_list = StringSubstr(missing_list, 0, StringLen(missing_list) - 2); if(StringLen(found_list) > 2) found_list = StringSubstr(found_list, 0, StringLen(found_list) - 2); if(StringLen(high_risk_list) > 2) high_risk_list = StringSubstr(high_risk_list, 0, StringLen(high_risk_list) - 2); g_logger.log_info("=== RELATÓRIO DE AUDITORIA DO NÚCLEO ==="); g_logger.log_info(StringFormat("Data: %s", TimeToString(TimeCurrent(), TIME_DATE|TIME_SECONDS))); g_logger.log_info(StringFormat("Total de arquivos críticos: %d", ArraySize(g_core_audit_results))); g_logger.log_info(StringFormat("Arquivos encontrados: %d", found)); g_logger.log_info(StringFormat("Arquivos ausentes: %d", missing)); g_logger.log_info(StringFormat("Arquivos de alto risco: %d", high_risk)); g_logger.log_info(StringFormat("Encontrados: %s", found_list)); g_logger.log_info(StringFormat("Ausentes: %s", missing_list)); g_logger.log_info(StringFormat("Alto risco: %s", high_risk_list)); g_logger.log_info(StringFormat("Status final: %s", missing == 0 ? "TUDO OK" : "FALHA CRÍTICA")); if(missing == 0) g_logger.log_success("[CORE_AUDIT] Todos os arquivos críticos do núcleo estão presentes."); else g_logger.log_critical("[CORE_AUDIT] SISTEMA COMPROMETIDO: Arquivos críticos do núcleo ausentes."); }

int OnStart()
{ g_logger = new logger_institutional("CoreAuditEngine"); if(!g_logger.is_initialized()){ Print("[CORE_AUDIT] Falha ao inicializar logger"); return 1; } run_core_audit(); generate_core_report(); string log_path = "Files/CoreAuditReport_" + TimeToString(TimeCurrent(), TIME_DATE) + ".txt"; g_logger.export_logs(log_path); g_logger.log_info("[CORE_AUDIT] Relatório salvo em: " + log_path); return 0; }


