#property copyright "Copyright 2024, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "1.00"
#property strict

#include "ChartObjectLabel.mqh"
#include "ChartObjectRect.mqh"

class HUD {
private:
    long m_chart_id;
    ChartObjectLabel* m_label;
    ChartObjectRect* m_background;
    bool m_is_created;
    
public:
    HUD(long chart_id) {
        m_chart_id = chart_id;
        m_label = NULL;
        m_background = NULL;
        m_is_created = false;
    }
    
    ~HUD() {
        Delete();
    }
    
    bool Create(string text, int x, int y, int width, int height) {
        if(m_is_created) {
            Print("HUD já existe");
            return false;
        }
        
        // Criar background
        m_background = new ChartObjectRect(m_chart_id, "HUD_Background");
        if(!m_background.Create(m_chart_id, 0, 0, 0, 0)) {
            Print("Erro ao criar background do HUD");
            delete m_background;
            m_background = NULL;
            return false;
        }
        
        // Configurar background
        if(!m_background.BackgroundColor(clrDarkSlateGray)) {
            Print("Erro ao configurar cor do background");
            m_background.Delete();
            delete m_background;
            m_background = NULL;
            return false;
        }
        
        if(!m_background.BorderColor(clrBlack)) {
            Print("Erro ao configurar cor da borda");
            m_background.Delete();
            delete m_background;
            m_background = NULL;
            return false;
        }
        
        if(!m_background.Width(1)) {
            Print("Erro ao configurar largura da borda");
            m_background.Delete();
            delete m_background;
            m_background = NULL;
            return false;
        }
        
        // Criar label
        m_label = new ChartObjectLabel(m_chart_id, "HUD_Label");
        if(!m_label.Create(m_chart_id, x, y, text)) {
            Print("Erro ao criar label do HUD");
            m_background.Delete();
            delete m_background;
            m_background = NULL;
            delete m_label;
            m_label = NULL;
            return false;
        }
        
        // Configurar label
        if(!m_label.Color(clrWhite)) {
            Print("Erro ao configurar cor do texto");
            m_background.Delete();
            delete m_background;
            m_background = NULL;
            m_label.Delete();
            delete m_label;
            m_label = NULL;
            return false;
        }
        
        if(!m_label.FontSize(10)) {
            Print("Erro ao configurar tamanho da fonte");
            m_background.Delete();
            delete m_background;
            m_background = NULL;
            m_label.Delete();
            delete m_label;
            m_label = NULL;
            return false;
        }
        
        m_is_created = true;
        return true;
    }
    
    bool Delete() {
        if(!m_is_created) return false;
        
        if(m_background != NULL) {
            m_background.Delete();
            delete m_background;
            m_background = NULL;
        }
        
        if(m_label != NULL) {
            m_label.Delete();
            delete m_label;
            m_label = NULL;
        }
        
        m_is_created = false;
        return true;
    }
    
    bool UpdateText(string text) {
        if(!m_is_created || m_label == NULL) return false;
        return m_label.Text(text);
    }
    
    bool UpdatePosition(int x, int y) {
        if(!m_is_created || m_label == NULL) return false;
        return m_label.Move(x, y);
    }
    
    bool IsCreated() const {
        return m_is_created;
    }
}; 