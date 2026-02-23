#property copyright "Copyright 2024, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "1.00"
#property strict

#include <ChartObjects\ChartObject.mqh>

class ChartObjectEdit : public CChartObject {
private:
    string m_text;
    color m_color;
    color m_background_color;
    color m_border_color;
    int m_font_size;
    string m_font;
    ENUM_BASE_CORNER m_corner;
    int m_x_distance;
    int m_y_distance;
    int m_x_size;
    int m_y_size;
    int m_max_length;
    bool m_is_created;
    
    // Validações
    bool ValidateFontSize(int size) {
        return (size > 0 && size <= 72);
    }
    
    bool ValidateCoordinates(int x, int y) {
        return (x >= 0 && y >= 0);
    }
    
    bool ValidateSize(int size) {
        return (size > 0);
    }
    
    bool ValidateMaxLength(int length) {
        return (length > 0 && length <= 1000);
    }
    
public:
    ChartObjectEdit(long chart_id, string name) : CChartObject(chart_id, name) {
        m_text = "";
        m_color = clrBlack;
        m_background_color = clrWhite;
        m_border_color = clrBlack;
        m_font_size = 10;
        m_font = "Arial";
        m_corner = CORNER_LEFT_UPPER;
        m_x_distance = 0;
        m_y_distance = 0;
        m_x_size = 100;
        m_y_size = 20;
        m_max_length = 100;
        m_is_created = false;
    }
    
    bool Create(long chart_id, int x, int y) {
        if(m_is_created) {
            Print("Campo de edição já existe: ", m_name);
            return false;
        }
        
        if(!ValidateCoordinates(x, y)) {
            Print("Coordenadas inválidas: x=", x, ", y=", y);
            return false;
        }
        
        if(!CChartObject::Create(chart_id, OBJ_EDIT, 0, x, y)) {
            Print("Erro ao criar campo de edição: ", GetLastError());
            return false;
        }
        
        if(!Text(m_text)) return false;
        if(!Color(m_color)) return false;
        if(!BackgroundColor(m_background_color)) return false;
        if(!BorderColor(m_border_color)) return false;
        if(!FontSize(m_font_size)) return false;
        if(!Font(m_font)) return false;
        if(!Corner(m_corner)) return false;
        if(!X_Distance(m_x_distance)) return false;
        if(!Y_Distance(m_y_distance)) return false;
        if(!X_Size(m_x_size)) return false;
        if(!Y_Size(m_y_size)) return false;
        if(!MaxLength(m_max_length)) return false;
        
        m_is_created = true;
        return true;
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
    
    bool BackgroundColor(color clr) {
        if(!m_is_created) return false;
        m_background_color = clr;
        return ObjectSetInteger(m_chart_id, m_name, OBJPROP_BGCOLOR, clr);
    }
    
    bool BorderColor(color clr) {
        if(!m_is_created) return false;
        m_border_color = clr;
        return ObjectSetInteger(m_chart_id, m_name, OBJPROP_BORDER_COLOR, clr);
    }
    
    bool FontSize(int size) {
        if(!m_is_created) return false;
        if(!ValidateFontSize(size)) {
            Print("Tamanho de fonte inválido: ", size);
            return false;
        }
        m_font_size = size;
        return ObjectSetInteger(m_chart_id, m_name, OBJPROP_FONTSIZE, size);
    }
    
    bool Font(string font) {
        if(!m_is_created) return false;
        if(font == "") {
            Print("Nome da fonte inválido");
            return false;
        }
        m_font = font;
        return ObjectSetString(m_chart_id, m_name, OBJPROP_FONT, font);
    }
    
    bool Corner(ENUM_BASE_CORNER corner) {
        if(!m_is_created) return false;
        m_corner = corner;
        return ObjectSetInteger(m_chart_id, m_name, OBJPROP_CORNER, corner);
    }
    
    bool X_Distance(int distance) {
        if(!m_is_created) return false;
        if(!ValidateCoordinates(distance, m_y_distance)) {
            Print("Distância X inválida: ", distance);
            return false;
        }
        m_x_distance = distance;
        return ObjectSetInteger(m_chart_id, m_name, OBJPROP_XDISTANCE, distance);
    }
    
    bool Y_Distance(int distance) {
        if(!m_is_created) return false;
        if(!ValidateCoordinates(m_x_distance, distance)) {
            Print("Distância Y inválida: ", distance);
            return false;
        }
        m_y_distance = distance;
        return ObjectSetInteger(m_chart_id, m_name, OBJPROP_YDISTANCE, distance);
    }
    
    bool X_Size(int size) {
        if(!m_is_created) return false;
        if(!ValidateSize(size)) {
            Print("Tamanho X inválido: ", size);
            return false;
        }
        m_x_size = size;
        return ObjectSetInteger(m_chart_id, m_name, OBJPROP_XSIZE, size);
    }
    
    bool Y_Size(int size) {
        if(!m_is_created) return false;
        if(!ValidateSize(size)) {
            Print("Tamanho Y inválido: ", size);
            return false;
        }
        m_y_size = size;
        return ObjectSetInteger(m_chart_id, m_name, OBJPROP_YSIZE, size);
    }
    
    bool MaxLength(int length) {
        if(!m_is_created) return false;
        if(!ValidateMaxLength(length)) {
            Print("Tamanho máximo inválido: ", length);
            return false;
        }
        m_max_length = length;
        return ObjectSetInteger(m_chart_id, m_name, OBJPROP_MAXLEN, length);
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
    
    bool Move(int x, int y) {
        if(!m_is_created) return false;
        if(!ValidateCoordinates(x, y)) {
            Print("Coordenadas inválidas para movimento: x=", x, ", y=", y);
            return false;
        }
        if(!X_Distance(x)) return false;
        if(!Y_Distance(y)) return false;
        return true;
    }
    
    bool Resize(int x_size, int y_size) {
        if(!m_is_created) return false;
        if(!ValidateSize(x_size) || !ValidateSize(y_size)) {
            Print("Tamanhos inválidos para redimensionamento: x=", x_size, ", y=", y_size);
            return false;
        }
        if(!X_Size(x_size)) return false;
        if(!Y_Size(y_size)) return false;
        return true;
    }
    
    string GetText() {
        if(!m_is_created) return "";
        return ObjectGetString(m_chart_id, m_name, OBJPROP_TEXT);
    }
    
    color GetColor() {
        if(!m_is_created) return clrNONE;
        return (color)ObjectGetInteger(m_chart_id, m_name, OBJPROP_COLOR);
    }
    
    color GetBackgroundColor() {
        if(!m_is_created) return clrNONE;
        return (color)ObjectGetInteger(m_chart_id, m_name, OBJPROP_BGCOLOR);
    }
    
    color GetBorderColor() {
        if(!m_is_created) return clrNONE;
        return (color)ObjectGetInteger(m_chart_id, m_name, OBJPROP_BORDER_COLOR);
    }
    
    int GetFontSize() {
        if(!m_is_created) return 0;
        return (int)ObjectGetInteger(m_chart_id, m_name, OBJPROP_FONTSIZE);
    }
    
    string GetFont() {
        if(!m_is_created) return "";
        return ObjectGetString(m_chart_id, m_name, OBJPROP_FONT);
    }
    
    ENUM_BASE_CORNER GetCorner() {
        if(!m_is_created) return CORNER_LEFT_UPPER;
        return (ENUM_BASE_CORNER)ObjectGetInteger(m_chart_id, m_name, OBJPROP_CORNER);
    }
    
    int GetXDistance() {
        if(!m_is_created) return 0;
        return (int)ObjectGetInteger(m_chart_id, m_name, OBJPROP_XDISTANCE);
    }
    
    int GetYDistance() {
        if(!m_is_created) return 0;
        return (int)ObjectGetInteger(m_chart_id, m_name, OBJPROP_YDISTANCE);
    }
    
    int GetXSize() {
        if(!m_is_created) return 0;
        return (int)ObjectGetInteger(m_chart_id, m_name, OBJPROP_XSIZE);
    }
    
    int GetYSize() {
        if(!m_is_created) return 0;
        return (int)ObjectGetInteger(m_chart_id, m_name, OBJPROP_YSIZE);
    }
    
    int GetMaxLength() {
        if(!m_is_created) return 0;
        return (int)ObjectGetInteger(m_chart_id, m_name, OBJPROP_MAXLEN);
    }
    
    bool IsCreated() const {
        return m_is_created;
    }
}; 