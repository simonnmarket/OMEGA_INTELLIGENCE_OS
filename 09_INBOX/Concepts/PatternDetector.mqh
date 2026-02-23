//+------------------------------------------------------------------+
//| Constructor                                                      |
//+------------------------------------------------------------------+
CPatternDetector::CPatternDetector()
{
    m_data_updater = NULL;
    m_physics_engine = NULL;
    m_logger = NULL;
    
    // Default parameters optimized for EUR/USD
    m_min_bars = 5;
    m_max_bars = 50;
    m_min_height = 0.0020; // 20 pips
    m_max_height = 0.1000; // 1000 pips
    m_min_width = 5.0;
    m_max_width = 500.0;
    m_min_strength = 50.0;
    m_volume_threshold = 1.1; // Volume excess threshold for EUR/USD
    m_momentum_threshold = 0.005; // 0.5% momentum
    m_volatility_threshold = 0.0080; // 80 pips ATR
    
    m_pattern_count = 0;
    ArrayResize(m_patterns, 0);
    
    // EUR/USD key levels
    double levels[] = {1.0500, 1.0700, 1.1000, 1.1200};
    ArrayCopy(m_key_levels, levels);
}

//+------------------------------------------------------------------+
//| Destructor                                                       |
//+------------------------------------------------------------------+
CPatternDetector::~CPatternDetector()
{
    ClearPatterns();
} 