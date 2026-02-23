//+------------------------------------------------------+
//| Interface Base para Modelos de Padrões               |
//+------------------------------------------------------+
#pragma once

class IPatternModel {
public:
    virtual string GetName() = 0;
    virtual bool CheckPattern() = 0;
};
