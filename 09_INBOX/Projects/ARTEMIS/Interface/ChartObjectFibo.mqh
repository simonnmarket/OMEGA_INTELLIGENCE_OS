#property copyright "Copyright 2024, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "1.00"
#property strict

#include <ChartObjects\ChartObject.mqh>

class ChartObjectFibo : public CChartObject {
private:
    datetime m_time1;
    datetime m_time2;
    double m_price1;
    double m_price2;
    color m_color;
    int m_width;
    ENUM_LINE_STYLE m_style;
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
    ChartObjectFibo(long chart_id, string name) : CChartObject(chart_id, name) {
        m_time1 = 0;
        m_time2 = 0;
        m_price1 = 0;
        m_price2 = 0;
        m_color = clrGreen;
        m_width = 1;
        m_style = STYLE_SOLID;
        m_is_created = false;
    }
    
    bool Create(long chart_id, datetime time1, double price1, datetime time2, double price2) {
        if(m_is_created) {
            Print("Fibonacci já existe: ", m_name);
            return false;
        }
        
        if(!ValidateTime(time1) || !ValidateTime(time2)) {
            Print("Tempo inválido");
            return false;
        }
        
        if(!ValidatePrice(price1) || !ValidatePrice(price2)) {
            Print("Preço inválido");
            return false;
        }
        
        if(!CChartObject::Create(chart_id, OBJ_FIBO, 0, time1, price1)) {
            Print("Erro ao criar Fibonacci: ", GetLastError());
            return false;
        }
        
        if(!Time1(time1)) return false;
        if(!Price1(price1)) return false;
        if(!Time2(time2)) return false;
        if(!Price2(price2)) return false;
        if(!Color(m_color)) return false;
        if(!Width(m_width)) return false;
        if(!Style(m_style)) return false;
        
        m_is_created = true;
        return true;
    }
    
    bool Time1(datetime time) {
        if(!m_is_created) return false;
        if(!ValidateTime(time)) {
            Print("Tempo 1 inválido: ", time);
            return false;
        }
        m_time1 = time;
        return ObjectSetInteger(m_chart_id, m_name, OBJPROP_TIME1, time);
    }
    
    bool Price1(double price) {
        if(!m_is_created) return false;
        if(!ValidatePrice(price)) {
            Print("Preço 1 inválido: ", price);
            return false;
        }
        m_price1 = price;
        return ObjectSetDouble(m_chart_id, m_name, OBJPROP_PRICE1, price);
    }
    
    bool Time2(datetime time) {
        if(!m_is_created) return false;
        if(!ValidateTime(time)) {
            Print("Tempo 2 inválido: ", time);
            return false;
        }
        m_time2 = time;
        return ObjectSetInteger(m_chart_id, m_name, OBJPROP_TIME2, time);
    }
    
    bool Price2(double price) {
        if(!m_is_created) return false;
        if(!ValidatePrice(price)) {
            Print("Preço 2 inválido: ", price);
            return false;
        }
        m_price2 = price;
        return ObjectSetDouble(m_chart_id, m_name, OBJPROP_PRICE2, price);
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
    
    bool Style(ENUM_LINE_STYLE style) {
        if(!m_is_created) return false;
        m_style = style;
        return ObjectSetInteger(m_chart_id, m_name, OBJPROP_STYLE, style);
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
    
    bool Move(datetime time1, double price1, datetime time2, double price2) {
        if(!m_is_created) return false;
        if(!ValidateTime(time1) || !ValidateTime(time2)) {
            Print("Tempos inválidos para movimento");
            return false;
        }
        if(!ValidatePrice(price1) || !ValidatePrice(price2)) {
            Print("Preços inválidos para movimento");
            return false;
        }
        if(!Time1(time1)) return false;
        if(!Price1(price1)) return false;
        if(!Time2(time2)) return false;
        if(!Price2(price2)) return false;
        return true;
    }
    
    datetime GetTime1() {
        if(!m_is_created) return 0;
        return (datetime)ObjectGetInteger(m_chart_id, m_name, OBJPROP_TIME1);
    }
    
    double GetPrice1() {
        if(!m_is_created) return 0;
        return ObjectGetDouble(m_chart_id, m_name, OBJPROP_PRICE1);
    }
    
    datetime GetTime2() {
        if(!m_is_created) return 0;
        return (datetime)ObjectGetInteger(m_chart_id, m_name, OBJPROP_TIME2);
    }
    
    double GetPrice2() {
        if(!m_is_created) return 0;
        return ObjectGetDouble(m_chart_id, m_name, OBJPROP_PRICE2);
    }
    
    color GetColor() {
        if(!m_is_created) return clrNONE;
        return (color)ObjectGetInteger(m_chart_id, m_name, OBJPROP_COLOR);
    }
    
    int GetWidth() {
        if(!m_is_created) return 0;
        return (int)ObjectGetInteger(m_chart_id, m_name, OBJPROP_WIDTH);
    }
    
    ENUM_LINE_STYLE GetStyle() {
        if(!m_is_created) return STYLE_SOLID;
        return (ENUM_LINE_STYLE)ObjectGetInteger(m_chart_id, m_name, OBJPROP_STYLE);
    }
    
    bool IsCreated() const {
        return m_is_created;
    }
}; 