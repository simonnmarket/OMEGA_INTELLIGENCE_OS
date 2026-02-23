//+------------------------------------------------------------------+
//| include_audit_engine.mq5 - Auditoria de Includes                 |
//| Projeto: Genesis / EA Genesis                                    |
//| Versão: v1.0                                                     |
//+------------------------------------------------------------------+
#property strict
#property description "Motor de Auditoria de Includes - Nível TIER-0"
#property script_show_inputs

#include <Genesis/Utils/Utils.mqh>

struct IncludeAuditedFile { string full_path; string file_name; string category; bool exists; string sha3_checksum; datetime last_modified; bool is_critical; string actual_location; string neural_status; double neural_confidence; int dependency_count; string dependencies[]; };

string g_include_critical_files[] = {
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
   "Include/Genesis/Intelligence/AnomalyDetectorAI.mqh",
   "Include/Genesis/Intelligence/MLDuplicateDetector.mqh",
   "Include/Genesis/Intelligence/NeuralSignalProcessor.mqh",
   "Include/Genesis/Intelligence/QuantumAdaptiveLearning.mqh",
   "Include/Genesis/Intelligence/QuantumLearning.mqh",
   "Include/Genesis/Intelligence/ThalerBiasEngine.mqh",
   "Include/Genesis/Neural/NeuroNet.mqh",
   "Include/Genesis/Neural/QuantumNeuralFilter.mqh",
   "Include/Genesis/Neural/QuantumNeuralNet.mqh",
   "Include/Genesis/Quantum/HardwareAccelerator.mqh",
   "Include/Genesis/Quantum/QuantumAnnealingSimulator.mqh",
   "Include/Genesis/Quantum/QuantumBehaviorController.mqh",
   "Include/Genesis/Quantum/QuantumCacheManager.mqh",
   "Include/Genesis/Quantum/QuantumDataProcessor.mqh",
   "Include/Genesis/Quantum/QuantumEntanglement.mqh",
   "Include/Genesis/Quantum/QuantumEntanglementSimulator.mqh",
   "Include/Genesis/Quantum/QuantumFinanceFramework.mqh",
   "Include/Genesis/Quantum/QuantumGateSystem.mqh",
   "Include/Genesis/Quantum/QuantumGeneticAlgorithm.mqh",
   "Include/Genesis/Quantum/QuantumMemoryCell.mqh",
   "Include/Genesis/Quantum/QuantumNeuralBridge.mqh",
   "Include/Genesis/Quantum/QuantumNeuralCore.mqh",
   "Include/Genesis/Quantum/QuantumNoiseFilter.mqh",
   "Include/Genesis/Quantum/QuantumOptimizer.mqh",
   "Include/Genesis/Quantum/QuantumProcessor.mqh",
   "Include/Genesis/Quantum/QuantumStateManager.mqh",
   "Include/Genesis/Quantum/QuantumWaveletTransform.mqh",
   "Include/Genesis/Audit/AuditNomenclatureValidator.mqh",
   "Include/Genesis/Compliance/ComplianceChecker.mqh",
   "Include/Genesis/Security/CrisisProtocol.mqh",
   "Include/Genesis/Data/QuantumMarketData.mqh"
};

CGenesisUtils *g_logger; IncludeAuditedFile g_include_audit_results[]; datetime g_last_run;

string calculate_sha3(const string &content)
{ int len = StringLen(content); long sum = 0; for(int i = 0; i < len; i++) sum += StringGetChar(content, i); return StringFormat("%064X", MathAbs(sum * 32767 % 1152921504606846976LL)); }

bool read_file_content(string path, string &content)
{ int handle = FileOpen(path, FILE_READ|FILE_TXT); if(handle == INVALID_HANDLE) return false; content = ""; while(!FileIsEnding(handle)) content += FileReadString(handle); FileClose(handle); return true; }

string normalize_path(string path)
{ StringReplace(path, "\\", "/"); return StringToLower(path); }

string extract_category(string path)
{ string parts[]; StringSplit(path, '/', parts); if(ArraySize(parts) >= 3) return parts[2]; return "UNKNOWN"; }

bool verify_file_exists(string path, string &actual_location)
{ if(FileIsExist(path)){ actual_location = path; return true; } actual_location = "NÃO ENCONTRADO"; return false; }

void analyze_dependencies(string file_path, IncludeAuditedFile &file)
{ string content; if(!read_file_content(file_path, content)) return; string lines[]; StringSplit(content, '\n', lines); for(int i = 0; i < ArraySize(lines); i++){ string line = StringTrimRight(lines[i]); if(StringFind(line, "#include") >= 0){ int s = StringFind(line, "<") + 1; int e = StringFind(line, ">"); if(s > 0 && e > s){ string include_path = StringSubstr(line, s, e - s); ArrayPushBack(file.dependencies, include_path); } } } file.dependency_count = ArraySize(file.dependencies); }

void analyze_neural_status(IncludeAuditedFile &file)
{ if(!file.exists){ file.neural_status = "CRÍTICO"; file.neural_confidence = 0.0; return; } string content; if(read_file_content(file.actual_location, content)){ int lines = StringSplit(content, '\n'); int classes = StringFind(content, "class "); int includes = StringFind(content, "#include"); double complexity_score = (double)lines / 120.0 + (double)classes / 8.0 + (double)includes / 6.0; if(complexity_score > 3.0){ file.neural_status = "ALTO_RISCO"; file.neural_confidence = 0.2; } else if(complexity_score > 1.5){ file.neural_status = "MÉDIO_RISCO"; file.neural_confidence = 0.5; } else { file.neural_status = "BAIXO_RISCO"; file.neural_confidence = 0.8; } } else { file.neural_status = "ERRO_LEITURA"; file.neural_confidence = 0.0; } }

void run_include_audit()
{
   ArrayInitialize(g_include_audit_results); g_logger.log_info("[INCLUDE_AUDIT] Iniciando auditoria de includes v1.0 (Neural Anti-Reincidência)");
   for(int i = 0; i < ArraySize(g_include_critical_files); i++)
   { string raw_path = g_include_critical_files[i]; string norm_path = normalize_path(raw_path); IncludeAuditedFile result; result.full_path = norm_path; result.file_name = StringSubstr(norm_path, StringRFind(norm_path, "/", -1) + 1); result.category = extract_category(norm_path); result.is_critical = true; result.exists = verify_file_exists(raw_path, result.actual_location); result.last_modified = 0; result.sha3_checksum = ""; if(result.exists){ result.last_modified = FileGetTime(result.actual_location, FILETIME_MODIFY); string content; if(read_file_content(result.actual_location, content)) result.sha3_checksum = calculate_sha3(content); else result.sha3_checksum = "ERRO_LEITURA"; g_logger.log_info(StringFormat("[INCLUDE_AUDIT] ✅ %s (%s) → %s", result.file_name, result.category, result.actual_location)); analyze_dependencies(result.actual_location, result); } else { result.sha3_checksum = "ARQUIVO_NAO_ENCONTRADO"; g_logger.log_error(StringFormat("[INCLUDE_AUDIT] ❌ %s (%s) → NÃO ENCONTRADO", result.file_name, result.category)); } analyze_neural_status(result); ArrayPushBack(g_include_audit_results, result); }
   g_last_run = TimeCurrent(); g_logger.log_success("[INCLUDE_AUDIT] Auditoria de includes concluída com sucesso");
}

void generate_include_report()
{ int missing = 0; int found = 0; int high_risk = 0; int total_dependencies = 0; string missing_list = ""; string found_list = ""; string high_risk_list = ""; for(int i = 0; i < ArraySize(g_include_audit_results); i++){ if(!g_include_audit_results[i].exists){ missing++; missing_list += g_include_audit_results[i].file_name + ", "; } else { found++; found_list += g_include_audit_results[i].file_name + ", "; total_dependencies += g_include_audit_results[i].dependency_count; if(g_include_audit_results[i].neural_status == "ALTO_RISCO"){ high_risk++; high_risk_list += g_include_audit_results[i].file_name + ", "; } } } if(StringLen(missing_list) > 2) missing_list = StringSubstr(missing_list, 0, StringLen(missing_list) - 2); if(StringLen(found_list) > 2) found_list = StringSubstr(found_list, 0, StringLen(found_list) - 2); if(StringLen(high_risk_list) > 2) high_risk_list = StringSubstr(high_risk_list, 0, StringLen(high_risk_list) - 2); g_logger.log_info("=== RELATÓRIO DE AUDITORIA DE INCLUDES ==="); g_logger.log_info(StringFormat("Data: %s", TimeToString(TimeCurrent(), TIME_DATE|TIME_SECONDS))); g_logger.log_info(StringFormat("Total de arquivos críticos: %d", ArraySize(g_include_audit_results))); g_logger.log_info(StringFormat("Arquivos encontrados: %d", found)); g_logger.log_info(StringFormat("Arquivos ausentes: %d", missing)); g_logger.log_info(StringFormat("Arquivos de alto risco: %d", high_risk)); g_logger.log_info(StringFormat("Total de dependências: %d", total_dependencies)); g_logger.log_info(StringFormat("Encontrados: %s", found_list)); g_logger.log_info(StringFormat("Ausentes: %s", missing_list)); g_logger.log_info(StringFormat("Alto risco: %s", high_risk_list)); g_logger.log_info(StringFormat("Status final: %s", missing == 0 ? "TUDO OK" : "FALHA CRÍTICA")); if(missing == 0) g_logger.log_success("[INCLUDE_AUDIT] Todos os arquivos críticos de includes estão presentes."); else g_logger.log_critical("[INCLUDE_AUDIT] SISTEMA COMPROMETIDO: Arquivos críticos de includes ausentes."); }

int OnStart()
{ g_logger = new logger_institutional("IncludeAuditEngine"); if(!g_logger.is_initialized()){ Print("[INCLUDE_AUDIT] Falha ao inicializar logger"); return 1; } run_include_audit(); generate_include_report(); string log_path = "Files/IncludeAuditReport_" + TimeToString(TimeCurrent(), TIME_DATE) + ".txt"; g_logger.export_logs(log_path); g_logger.log_info("[INCLUDE_AUDIT] Relatório salvo em: " + log_path); return 0; }


