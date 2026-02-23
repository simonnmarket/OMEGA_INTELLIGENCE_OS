#property copyright "Copyright 2024, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "1.00"
#property strict

#include <ChartObjects\ChartObject.mqh>

class ChartObjectArrow : public CChartObject {
private:
    datetime m_time;
    double m_price;
    ENUM_ARROW_ANCHOR m_anchor;
    color m_color;
    int m_width;
    bool m_is_created;
    
    // Validações
    bool ValidateTime(datetime time) {
        return (time > 0);
    }
    
    bool ValidatePrice(double price) {
        return (price > 0);
    }
    
    bool ValidateWidth(int width) {
        return (width > 0 && width <= 10);
    }
    
public:
    ChartObjectArrow(long chart_id, string name) : CChartObject(chart_id, name) {
        m_time = 0;
        m_price = 0;
        m_anchor = ANCHOR_TOP;
        m_color = clrRed;
        m_width = 1;
        m_is_created = false;
    }
    
    bool Create(long chart_id, datetime time, double price) {
        if(m_is_created) {
            Print("Seta já existe: ", m_name);
            return false;
        }
        
        if(!ValidateTime(time)) {
            Print("Tempo inválido: ", time);
            return false;
        }
        
        if(!ValidatePrice(price)) {
            Print("Preço inválido: ", price);
            return false;
        }
        
        if(!CChartObject::Create(chart_id, OBJ_ARROW, 0, time, price)) {
            Print("Erro ao criar seta: ", GetLastError());
            return false;
        }
        
        if(!Time(m_time)) return false;
        if(!Price(m_price)) return false;
        if(!Anchor(m_anchor)) return false;
        if(!Color(m_color)) return false;
        if(!Width(m_width)) return false;
        
        m_is_created = true;
        return true;
    }
    
    bool Time(datetime time) {
        if(!m_is_created) return false;
        if(!ValidateTime(time)) {
            Print("Tempo inválido: ", time);
            return false;
        }
        m_time = time;
        return ObjectSetInteger(m_chart_id, m_name, OBJPROP_TIME, time);
    }
    
    bool Price(double price) {
        if(!m_is_created) return false;
        if(!ValidatePrice(price)) {
            Print("Preço inválido: ", price);
            return false;
        }
        m_price = price;
        return ObjectSetDouble(m_chart_id, m_name, OBJPROP_PRICE, price);
    }
    
    bool Anchor(ENUM_ARROW_ANCHOR anchor) {
        if(!m_is_created) return false;
        m_anchor = anchor;
        return ObjectSetInteger(m_chart_id, m_name, OBJPROP_ANCHOR, anchor);
    }
    
    bool Color(color clr) {
        if(!m_is_created) return false;
        m_color = clr;
        return ObjectSetInteger(m_chart_id, m_name, OBJPROP_COLOR, clr);
    }
    
    bool Width(int width) {
        if(!m_is_created) return false;
        if(!ValidateWidth(width)) {
            Print("Largura inválida: ", width);
            return false;
        }
        m_width = width;
        return ObjectSetInteger(m_chart_id, m_name, OBJPROP_WIDTH, width);
    }
    
    bool Delete() {
        if(!m_is_created) return false;
        bool result = ObjectDelete(m_chart_id, m_name);
        if(result) m_is_created = false;
        return result;
    }
    
    bool Select() {
        if(!m_is_created) return false;
        return ObjectSelect(m_chart_id, m_name);
    }
    
    bool Deselect() {
        if(!m_is_created) return false;
        return ObjectSelect(m_chart_id, m_name, false);
    }
    
    bool Move(datetime time, double price) {
        if(!m_is_created) return false;
        if(!ValidateTime(time)) {
            Print("Tempo inválido para movimento: ", time);
            return false;
        }
        if(!ValidatePrice(price)) {
            Print("Preço inválido para movimento: ", price);
            return false;
        }
        if(!Time(time)) return false;
        if(!Price(price)) return false;
        return true;
    }
    
    datetime GetTime() {
        if(!m_is_created) return 0;
        return (datetime)ObjectGetInteger(m_chart_id, m_name, OBJPROP_TIME);
    }
    
    double GetPrice() {
        if(!m_is_created) return 0;
        return ObjectGetDouble(m_chart_id, m_name, OBJPROP_PRICE);
    }
    
    ENUM_ARROW_ANCHOR GetAnchor() {
        if(!m_is_created) return ANCHOR_TOP;
        return (ENUM_ARROW_ANCHOR)ObjectGetInteger(m_chart_id, m_name, OBJPROP_ANCHOR);
    }
    
    color GetColor() {
        if(!m_is_created) return clrNONE;
        return (color)ObjectGetInteger(m_chart_id, m_name, OBJPROP_COLOR);
    }
    
    int GetWidth() {
        if(!m_is_created) return 0;
        return (int)ObjectGetInteger(m_chart_id, m_name, OBJPROP_WIDTH);
    }
    
    bool IsCreated() const {
        return m_is_created;
    }
}; 