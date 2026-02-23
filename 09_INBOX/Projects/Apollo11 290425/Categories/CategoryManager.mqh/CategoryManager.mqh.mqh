#property copyright "Quantum Sensory Trading System"
#property link      "https://www.quantumsensory.com"
#property version   "4.0"

#include "../Core/BaseInterfaces.mqh"

class CCategoryManager {
private:
    IInsightCategory* categories[];
    int categoryCount;
    
public:
    CCategoryManager() : categoryCount(0) {
        ArrayResize(categories, 0);
    }
    
    ~CCategoryManager() {
        for(int i = 0; i < categoryCount; i++) {
            if(categories[i] != NULL) {
                delete categories[i];
                categories[i] = NULL;
            }
        }
        ArrayFree(categories);
    }
    
    bool RegisterCategory(IInsightCategory* category) {
        if(category == NULL) return false;
        
        int newSize = categoryCount + 1;
        if(ArrayResize(categories, newSize) != newSize) return false;
        
        categories[categoryCount] = category;
        categoryCount++;
        return true;
    }
    
    bool UpdateAllCategories() {
        for(int i = 0; i < categoryCount; i++) {
            if(categories[i] != NULL) {
                if(!categories[i].Update()) return false;
            }
        }
        return true;
    }
    
    bool GetCategorySignals(const int index, InsightSignal &signals[]) {
        if(index < 0 || index >= categoryCount) return false;
        if(categories[index] == NULL) return false;
        
        return categories[index].GetSignals(signals);
    }
    
    int GetCategoryCount() const {
        return categoryCount;
    }
}; 