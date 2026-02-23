#property copyright "Quantum Sensory Trading System"
#property link      "https://www.quantumsensory.com"
#property version   "4.0"

// Market state enumeration
enum ENUM_MARKET_STATE {
    STATE_ACCUMULATION,
    STATE_DISTRIBUTION,
    STATE_MANIPULATION,
    STATE_TRENDING,
    STATE_RANGING,
    STATE_UNDEFINED
};

// Zone type enumeration
enum ENUM_ZONE_TYPE {
    ZONE_ACCUMULATION,
    ZONE_DISTRIBUTION,
    ZONE_SUPPLY,
    ZONE_DEMAND,
    ZONE_NEUTRAL
};

// Signal structure for insights
struct InsightSignal {
    string   categoryName;
    string   signalName;
    double   strength;
    double   confidence;
    datetime timestamp;
    string   description;
    bool     isValid;
    int      priority;
    double   impact;
};

// Base interface for insight categories
interface IInsightCategory {
    bool Update();
    bool Validate();
    double GetInsightScore();
    bool GetSignals(InsightSignal &signals[]);
};