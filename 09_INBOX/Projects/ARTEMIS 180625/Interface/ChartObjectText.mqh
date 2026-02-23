#property copyright "Copyright 2024, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "1.00"
#property strict

#include <ChartObjects\ChartObject.mqh>

enum ENUM_TEXT_ALIGN {
    TEXT_ALIGN_LEFT,
    TEXT_ALIGN_CENTER,
    TEXT_ALIGN_RIGHT
};

class ChartObjectText : public CChartObject {
private:
    datetime m_time;
    double m_price;
    string m_text;
    color m_color;
    int m_font_size;
    string m_font;
    ENUM_TEXT_ALIGN m_align;
    bool m_is_created;
    
    // Validações
    bool ValidateTime(datetime time) {
        return (time > 0);
    }
    
    bool ValidatePrice(double price) {
        return (price > 0);
    }
    
    bool ValidateFontSize(int size) {
        return (size > 0 && size <= 100);
    }
    
public:
    ChartObjectText(long chart_id, string name) : CChartObject(chart_id, name) {
        m_time = 0;
        m_price = 0;
        m_text = "";
        m_color = clrBlack;
        m_font_size = 10;
        m_font = "Arial";
        m_align = TEXT_ALIGN_LEFT;
        m_is_created = false;
    }
    
    bool Create(long chart_id, datetime time, double price, string text) {
        if(m_is_created) {
            Print("Texto já existe: ", m_name);
            return false;
        }
        
        if(!ValidateTime(time)) {
            Print("Tempo inválido");
            return false;
        }
        
        if(!ValidatePrice(price)) {
            Print("Preço inválido");
            return false;
        }
        
        if(!CChartObject::Create(chart_id, OBJ_TEXT, 0, time, price)) {
            Print("Erro ao criar texto: ", GetLastError());
            return false;
        }
        
        if(!Time(time)) return false;
        if(!Price(price)) return false;
        if(!Text(text)) return false;
        if(!Color(m_color)) return false;
        if(!FontSize(m_font_size)) return false;
        if(!Font(m_font)) return false;
        if(!Align(m_align)) return false;
        
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
    
    bool Text(string text) {
        if(!m_is_created) return false;
        m_text = text;
        return ObjectSetString(m_chart_id, m_name, OBJPROP_TEXT, text);
    }
    
    bool Color(color clr) {
        if(!m_is_created) return false;
        m_color = clr;
        return ObjectSetInteger(m_chart_id, m_name, OBJPROP_COLOR, clr);
    }
    
    bool FontSize(int size) {
        if(!m_is_created) return false;
        if(!ValidateFontSize(size)) {
            Print("Tamanho da fonte inválido: ", size);
            return false;
        }
        m_font_size = size;
        return ObjectSetInteger(m_chart_id, m_name, OBJPROP_FONTSIZE, size);
    }
    
    bool Font(string font) {
        if(!m_is_created) return false;
        m_font = font;
        return ObjectSetString(m_chart_id, m_name, OBJPROP_FONT, font);
    }
    
    bool Align(ENUM_TEXT_ALIGN align) {
        if(!m_is_created) return false;
        m_align = align;
        return ObjectSetInteger(m_chart_id, m_name, OBJPROP_ANCHOR, align);
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
            Print("Tempo inválido para movimento");
            return false;
        }
        if(!ValidatePrice(price)) {
            Print("Preço inválido para movimento");
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
    
    string GetText() {
        if(!m_is_created) return "";
        return ObjectGetString(m_chart_id, m_name, OBJPROP_TEXT);
    }
    
    color GetColor() {
        if(!m_is_created) return clrNONE;
        return (color)ObjectGetInteger(m_chart_id, m_name, OBJPROP_COLOR);
    }
    
    int GetFontSize() {
        if(!m_is_created) return 0;
        return (int)ObjectGetInteger(m_chart_id, m_name, OBJPROP_FONTSIZE);
    }
    
    string GetFont() {
        if(!m_is_created) return "";
        return ObjectGetString(m_chart_id, m_name, OBJPROP_FONT);
    }
    
    ENUM_TEXT_ALIGN GetAlign() {
        if(!m_is_created) return TEXT_ALIGN_LEFT;
        return (ENUM_TEXT_ALIGN)ObjectGetInteger(m_chart_id, m_name, OBJPROP_ANCHOR);
    }
    
    bool IsCreated() const {
        return m_is_created;
    }
}; 