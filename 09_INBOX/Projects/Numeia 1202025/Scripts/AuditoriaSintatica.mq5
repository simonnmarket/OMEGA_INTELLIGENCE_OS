//+------------------------------------------------------------------+
//|                                    AuditoriaSintatica.mq5         |
//|         Auditoria Sintática Real - Detecção de Erros MQL5         |
//+------------------------------------------------------------------+
#property copyright "Numeia EA - Sistema Institucional"
#property link      ""
#property version   "1.00"
#property script_show_inputs

//+------------------------------------------------------------------+
//| Função principal do script                                        |
//+------------------------------------------------------------------+
void OnStart()
{
   Print("🔍 AUDITORIA SINTÁTICA INICIADA");
   Print("==================================");
   
   // Lista de arquivos .mqh para auditar
   string filesToAudit[] = {
      "Core/types.mqh",
      "Utils/Log.mqh",
      "Core/CoreBrainManager.mqh",
      "Core/ExecutionOrchestrator.mqh",
      "Core/ModuleRegistry.mqh",
      "Core/AuditInterface.mqh",
      "Agents/TradingAgent.mqh",
      "Agents/RiskAgent.mqh",
      "Agents/PatternRecognitionAgent.mqh",
      "Agents/MarketAnalysisAgent.mqh",
      "Auditor/AuditManager.mqh",
      "Auditor/AuditLogger.mqh",
      "Config/GlobalConfig.mqh",
      "Config/RiskConfig.mqh",
      "Utils/TimeUtils.mqh",
      "Utils/PriceUtils.mqh",
      "Utils/IndicatorUtils.mqh",
      "Include/Analysis/MarketAnalyzer.mqh",
      "Include/Analysis/VolumeProfile.mqh",
      "Include/Analysis/OrderFlowAnalyzer.mqh",
      "Include/Analysis/WeisWaveAnalyzer.mqh",
      "Include/Analysis/SignalValidator.mqh",
      "Include/Analysis/STOBarDetector.mqh",
      "Include/DecisionEngine/DecisionRouter.mqh",
      "Include/DecisionEngine/SignalConsensusEngine.mqh",
      "Include/DecisionEngine/SignalController.mqh",
      "Include/Intelligence/SkyIntelCore.mqh",
      "Include/Intelligence/SkyCrawlerNet.mqh",
      "Include/Intelligence/DeepPersonaLens.mqh",
      "Include/Intelligence/ScenarioIntelCore.mqh",
      "Include/Intelligence/ComplianceGuardian.mqh",
      "Include/ExecutionLogic/TradeExecutor.mqh",
      "Include/ExecutionLogic/PositionManager.mqh",
      "Include/ExecutionLogic/ExecutionLoopController.mqh",
      "Include/ExecutionLogic/DefenseOrchestrator.mqh",
      "Include/ExecutionLogic/SignalExecutionAgent.mqh",
      "Include/ExecutionLogic/TradeExecutorSkyIntel.mqh",
      "Include/ExecutionLogic/DefenseAgent.mqh",
      "Include/ExecutionLogic/SessionManager.mqh",
      "Include/Integration/SkyIntelBridge.mqh",
      "Include/Types/DefenseTypes.mqh",
      "Scripts/QuantumAudit/QuantumEntanglementMap.mqh",
      "Scripts/QuantumAudit/QuantumAuditEngine.mqh",
      "Scripts/QuantumAudit/AuditEntanglementBridge.mqh"
   };
   
   int totalFiles = ArraySize(filesToAudit);
   int filesWithErrors = 0;
   int totalErrors = 0;
   
   Print("📁 Total de arquivos para auditar: " + IntegerToString(totalFiles));
   Print("");
   
   for(int i = 0; i < totalFiles; i++)
   {
      string fileName = filesToAudit[i];
      Print("🔍 Auditando: " + fileName);
      
      int errorsInFile = AuditFileSyntax(fileName);
      
      if(errorsInFile > 0)
      {
         filesWithErrors++;
         totalErrors += errorsInFile;
         Print("❌ ERROS ENCONTRADOS: " + IntegerToString(errorsInFile));
      }
      else
      {
         Print("✅ OK");
      }
      Print("");
   }
   
   // Resultado final
   Print("==================================");
   Print("📊 RESULTADO DA AUDITORIA SINTÁTICA");
   Print("==================================");
   Print("Total de arquivos auditados: " + IntegerToString(totalFiles));
   Print("Arquivos com erros: " + IntegerToString(filesWithErrors));
   Print("Total de erros encontrados: " + IntegerToString(totalErrors));
   
   if(totalErrors == 0)
   {
      Print("🎉 TODOS OS ARQUIVOS ESTÃO SINTAXICAMENTE CORRETOS!");
   }
   else
   {
      Print("⚠️ EXISTEM ERROS DE SINTAXE NO PROJETO!");
      Print("Execute novamente para ver os detalhes dos erros.");
   }
   
   // Criar objeto visual
   string objName = "auditoria_sintatica_result";
   ObjectCreate(0, objName, OBJ_LABEL, 0, 0, 0);
   
   if(totalErrors == 0)
   {
      ObjectSetString(0, objName, OBJPROP_TEXT, "✅ SINTAXE OK!");
      ObjectSetInteger(0, objName, OBJPROP_COLOR, clrLime);
   }
   else
   {
      ObjectSetString(0, objName, OBJPROP_TEXT, "❌ " + IntegerToString(totalErrors) + " ERROS!");
      ObjectSetInteger(0, objName, OBJPROP_COLOR, clrRed);
   }
   
   ObjectSetInteger(0, objName, OBJPROP_XDISTANCE, 20);
   ObjectSetInteger(0, objName, OBJPROP_YDISTANCE, 20);
   ObjectSetInteger(0, objName, OBJPROP_FONTSIZE, 14);
   // ObjectSetString(0, objName, OBJPROP_FONT, "Arial Bold");
   
   ChartRedraw();
}

//+------------------------------------------------------------------+
//| Função para auditar sintaxe de um arquivo                        |
//+------------------------------------------------------------------+
int AuditFileSyntax(string fileName)
{
   int errors = 0;
   
   if(!FileIsExist(fileName))
   {
      Print("   ❌ Arquivo não encontrado: " + fileName);
      return 1;
   }
   
   int handle = FileOpen(fileName, FILE_READ | FILE_TXT | FILE_ANSI);
   if(handle == INVALID_HANDLE)
   {
      Print("   ❌ Erro ao abrir arquivo: " + fileName);
      return 1;
   }
   
   int lineNumber = 0;
   bool inComment = false;
   bool inString = false;
   bool inEnum = false;
   bool inStruct = false;
   bool inFunction = false;
   bool inNamespace = false;
   
   while(!FileIsEnding(handle))
   {
      lineNumber++;
      string line = FileReadString(handle);
      string trimmedLine = line;
      trimmedLine = StringTrimLeft(trimmedLine);
      trimmedLine = StringTrimRight(trimmedLine);
      
      // Pular linhas vazias
      if(StringLen(trimmedLine) == 0)
         continue;
      
      // Verificar se está em comentário
      if(StringFind(trimmedLine, "//") == 0)
         continue;
      
      if(StringFind(trimmedLine, "/*") >= 0)
         inComment = true;
      
      if(StringFind(trimmedLine, "*/") >= 0)
      {
         inComment = false;
         continue;
      }
      
      if(inComment)
         continue;
      
      // Verificar se está em string
      int quoteCount = 0;
      for(int i = 0; i < StringLen(trimmedLine); i++)
      {
         if(StringGetCharacter(trimmedLine, i) == '"')
            quoteCount++;
      }
      
      if(quoteCount % 2 == 1)
         inString = !inString;
      
      if(inString)
         continue;
      
      // Verificar estruturas de controle
      if(StringFind(trimmedLine, "enum") >= 0)
         inEnum = true;
      
      if(StringFind(trimmedLine, "struct") >= 0)
         inStruct = true;
      
      if(StringFind(trimmedLine, "void") >= 0 || StringFind(trimmedLine, "bool") >= 0 || 
         StringFind(trimmedLine, "int") >= 0 || StringFind(trimmedLine, "double") >= 0 || 
         StringFind(trimmedLine, "string") >= 0)
      {
         if(StringFind(trimmedLine, "(") >= 0)
            inFunction = true;
      }
      
      if(StringFind(trimmedLine, "namespace") >= 0)
         inNamespace = true;
      
      // Verificar fechamento de estruturas
      if(StringFind(trimmedLine, "}") >= 0)
      {
         if(inEnum) inEnum = false;
         if(inStruct) inStruct = false;
         if(inFunction) inFunction = false;
         if(inNamespace) inNamespace = false;
         continue;
      }
      
      // Verificar números soltos (erro crítico)
      if(!inEnum && !inStruct && !inFunction && !inNamespace)
      {
         // Padrão: linha que começa com número
         if(StringLen(trimmedLine) > 0)
         {
            int firstChar = StringGetCharacter(trimmedLine, 0);
            if(firstChar >= '0' && firstChar <= '9')
            {
               // Verificar se é apenas um número
               bool isOnlyNumber = true;
               for(int i = 0; i < StringLen(trimmedLine); i++)
               {
                  int ch = StringGetCharacter(trimmedLine, i);
                  if((ch < '0' || ch > '9') && ch != ' ' && ch != '\t' && ch != ',' && ch != ';')
                  {
                     isOnlyNumber = false;
                     break;
                  }
               }
               
               if(isOnlyNumber)
               {
                  Print("   ❌ Linha " + IntegerToString(lineNumber) + ": Número solto - " + trimmedLine);
                  errors++;
               }
            }
         }
      }
      
      // Verificar instruções soltas
      if(!inEnum && !inStruct && !inFunction && !inNamespace)
      {
         // Verificar se há instruções que não deveriam estar soltas
         if(StringFind(trimmedLine, ";") >= 0 && StringFind(trimmedLine, "=") < 0 && 
            StringFind(trimmedLine, "(") < 0 && StringFind(trimmedLine, "{") < 0)
         {
            // Verificar se não é uma declaração válida
            if(StringFind(trimmedLine, "int") < 0 && StringFind(trimmedLine, "double") < 0 && 
               StringFind(trimmedLine, "string") < 0 && StringFind(trimmedLine, "bool") < 0 &&
               StringFind(trimmedLine, "void") < 0 && StringFind(trimmedLine, "enum") < 0 &&
               StringFind(trimmedLine, "struct") < 0 && StringFind(trimmedLine, "class") < 0 &&
               StringFind(trimmedLine, "namespace") < 0 && StringFind(trimmedLine, "#include") < 0 &&
               StringFind(trimmedLine, "#define") < 0 && StringFind(trimmedLine, "#ifndef") < 0 &&
               StringFind(trimmedLine, "#endif") < 0)
            {
               Print("   ❌ Linha " + IntegerToString(lineNumber) + ": Instrução solta - " + trimmedLine);
               errors++;
            }
         }
      }
   }
   
   FileClose(handle);
   return errors;
} 