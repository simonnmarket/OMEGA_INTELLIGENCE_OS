//+------------------------------------------------------------------+
//|                                                  All_Channel.mq4 |
//+------------------------------------------------------------------+
#property copyright "Inkov Evgeni ew123@mail.ru"
#property link      "8-918-600-11-33"

#property indicator_chart_window
//=======================================================================
#define           Razm_Mas_Fract         500
//=======================================================================
extern int        Fr_bars_M1           = 7;     //
extern int        Fr_bars_M5           = 7;     //
extern int        Fr_bars_M15          = 7;     //
extern int        Fr_bars_M30          = 7;     //
extern int        Fr_bars_H1           = 7;     //
extern int        Fr_bars_H4           = 7;     //
extern int        Fr_bars_D1           = 7;     //
extern int        Fr_bars_W1           = 7;     //
extern int        Fr_bars_MN           = 7;     //
//+------------------------------------------------------------------+
extern int        Voln_end_M1          = 3;     //
extern int        Voln_end_M5          = 3;     //
extern int        Voln_end_M15         = 3;     //
extern int        Voln_end_M30         = 3;     //
extern int        Voln_end_H1          = 3;     //
extern int        Voln_end_H4          = 3;     //
extern int        Voln_end_D1          = 3;     //
extern int        Voln_end_W1          = 3;     //
extern int        Voln_end_MN          = 3;     //
//+------------------------------------------------------------------+
extern color      Color_M1              = Green;     //
extern color      Color_M5              = Red;     //
extern color      Color_M15             = Magenta;     //
extern color      Color_M30             = Brown;     //
extern color      Color_H1              = Blue;     //
extern color      Color_H4              = Black;     //
extern color      Color_D1              = GreenYellow;     //
extern color      Color_W1              = BlueViolet;     //
extern color      Color_MN              = Orange;     //
//+------------------------------------------------------------------+
extern bool       Out_Grafic           = true;  //             -            
extern bool       comm                 = true;  //                              
//+------------------------------------------------------------------+
int         mas_Fr_bars   [9];
int         mas_Voln_end  [9];
int         mas_beg_bar   [9];
int         mas_end_bar   [9];
datetime    mas_time_line1[9];
datetime    mas_time_line2[9];
double      mas_extrem [Razm_Mas_Fract][2][9];   // 0 -                , 1 -                      
int         mas_kol_mas_extr[9];                //      .                      mas_extrem
double      mas_pr1_min[9];
double      mas_pr1_max[9];
double      mas_pr0 [9];
color       mas_color[9];
//..........................
double      mas_tg    [9];
int         mas_proboi[9];
int         mas_TF[9]={PERIOD_M1,PERIOD_M5,PERIOD_M15,PERIOD_M30,PERIOD_H1,PERIOD_H4,PERIOD_D1,PERIOD_W1,PERIOD_MN1};
double      gran_up=0,gran_dw=0;
//+------------------------------------------------------------------+
int         Na4_Bar_Fract        = 1;     //           ,                                     
int         kol_mas_extr, end_bar,beg_bar;
datetime    time_line2, time_line1;
double      tg,pr1_min,pr1_max, pr0;
int         proboi;
double      pr1,pr2;
//+------------------------------------------------------------------+
int init()
{
   IndicatorShortName("All_Channel");
   //---------------------------------------------------------------------------------------
   put_mas (mas_Fr_bars,  Fr_bars_M1, Fr_bars_M5, Fr_bars_M15, Fr_bars_M30, Fr_bars_H1,
            Fr_bars_H4, Fr_bars_D1, Fr_bars_W1, Fr_bars_MN);
   put_mas (mas_Voln_end, Voln_end_M1,Voln_end_M5,Voln_end_M15,Voln_end_M30,Voln_end_H1,
            Voln_end_H4,Voln_end_D1,Voln_end_W1,Voln_end_MN);
   put_mas (mas_color,Color_M1,Color_M5,Color_M15,Color_M30,Color_H1,Color_H4,Color_D1,Color_W1,Color_MN);

   
   return(0);
}
//+------------------------------------------------------------------+
void put_mas (int& mas[9],int n1,int n2,int n3,int n4,int n5,int n6,int n7,int n8,int n9)
{
   mas[0]=n1; mas[1]=n2; mas[2]=n3; mas[3]=n4; mas[4]=n5; mas[5]=n6; mas[6]=n7; mas[7]=n8; mas[8]=n9;
}
//+------------------------------------------------------------------+
int deinit()
{
   if (UninitializeReason()!=REASON_CHARTCHANGE) //               TF
      for (int i=0;i<9;i++)
      {
         del_obj(i);
         ObjectDelete("TL_max" +str_TF(i));
         ObjectDelete("TL_cenr"+str_TF(i));
         ObjectDelete("TL_min" +str_TF(i));
         Comment("");   //                             
      }

   return(0);
}
//+------------------------------------------------------------------+
int start()
{
   for (int n_TF=0;n_TF<9;n_TF++)   //                     
      if (mas_Fr_bars[n_TF]>0 && mas_Voln_end[n_TF]>0)
      {
         kol_mas_extr= mas_kol_mas_extr[n_TF];
         end_bar     = mas_end_bar[n_TF];
         beg_bar     = mas_beg_bar[n_TF];
         time_line2  = mas_time_line2[n_TF];
         time_line1  = mas_time_line1[n_TF];
         tg          = mas_tg[n_TF];
         proboi      = mas_proboi[n_TF];
         pr1_min     = mas_pr1_min[n_TF];
         pr1_max     = mas_pr1_max[n_TF];
         pr0         = mas_pr0[n_TF];

         Out_Kanal(mas_TF[n_TF], mas_Fr_bars[n_TF], mas_extrem, n_TF, kol_mas_extr, 
                   mas_color[n_TF], Out_Grafic, end_bar, beg_bar, time_line2, time_line1, 
                   mas_color[n_TF],tg, proboi,pr1_min, pr1_max, mas_Voln_end[n_TF], pr0);
                
         mas_kol_mas_extr[n_TF]  = kol_mas_extr;
         mas_end_bar[n_TF]       = end_bar;
         mas_beg_bar[n_TF]       = beg_bar;
         mas_time_line2[n_TF]    = time_line2;
         mas_time_line1[n_TF]    = time_line1;
         mas_tg[n_TF]            = tg;
         mas_proboi[n_TF]        = proboi;
         mas_pr1_min[n_TF]       = pr1_min;
         mas_pr1_max[n_TF]       = pr1_max;
         mas_pr0[n_TF]           = pr0;
      }
      
   if  (comm)Out_Comm();
   return(0);
}
//+------------------------------------------------------------------+
void Out_Comm()
{
   string ccc="";
   ccc=ccc+"\n            ";
   for (int j=0;j<9;j++)ccc=ccc+str_TF(j)+" ";
   
   ccc=ccc+"\n"+"      :  ";
   string s;
   for (j=0;j<9;j++)
   {
      if (mas_proboi[j]>0)
         s="1";
      else
         if (mas_proboi[j]<0)
            s="0";
         else
            s="`";
      ccc=ccc+s+"    ";
   }
   ccc=ccc+"\n"+"     :    ";
   for (j=0;j<9;j++)
   {
      bool t=mas_tg[j]>=0.0;
      s=DoubleToStr(t,0);
      ccc=ccc+s+"    ";
   }
   Comment(ccc);
}
//==========================================================================
bool Put_mas_fract_and_extr(int TF,int Fractal_Bars, color col_UP,color col_DW,
                            int nom_ind, double& mas_extremum[][][], int& kol_mas_extr, bool Out_Graf, int kol_voln)
{
   int i;

   double long [Razm_Mas_Fract];
   double short[Razm_Mas_Fract];
   int na4_bar,kol_bar;

   ArrayInitialize(long,0);
   ArrayInitialize(short,0);
//----
   
   if (Fractal_Bars<=0)Fractal_Bars=1;
   
   int HighBar = -1;
   int LowBar  = -1;
   
   //               
   int kol_bars=MathMin(Razm_Mas_Fract,iBars(Symbol(),TF)-1);
   
   int tek_kol_voln;
   for(i=Na4_Bar_Fract;i<=kol_bars;i++) //                    .             
   {
      //                   :           .    .    i-Fractal_Bars          .=Fractal_Bars*2+1,  . . i +- Fractal_Bars
      na4_bar=i-Fractal_Bars;
      if (na4_bar<0)
      {
         continue;
//         kol_bar=Fractal_Bars*2+1+na4_bar;
//         na4_bar=0;
      }
      else
         kol_bar=Fractal_Bars*2+1;
      if (i==iLowest(Symbol(),TF,MODE_LOW,kol_bar,na4_bar))  
      {
         switch(HighLow(LowBar,HighBar))
         {
            case -1:
            {
               if (NormalizeDouble(iLow(Symbol(),TF,i),Digits)<NormalizeDouble(iLow(Symbol(),TF,LowBar),Digits))
               {
                  long[i]=iLow(Symbol(),TF,i);
                  long[LowBar]=0;
                  LowBar=i;
//                  tek_kol_voln++;
               }
               break;
            }
            case 1:  //          
            {
               if (NormalizeDouble(iLow(Symbol(),TF,i),Digits)<NormalizeDouble(iHigh(Symbol(),TF,HighBar),Digits))
               {
                  long[i]=iLow(Symbol(),TF,i);
                  LowBar=i;
                  tek_kol_voln++;
               }
               break;
            }
            case 0:    //           .
            {
               long[i]=iLow(Symbol(),TF,i);
               LowBar=i;
               tek_kol_voln++;
               break;
            }
         }
      }
      //                    
      na4_bar=i-Fractal_Bars;
      if (na4_bar<0)
      {
         kol_bar=Fractal_Bars*2+1+na4_bar;
         na4_bar=0;
      }
      else
         kol_bar=Fractal_Bars*2+1;
      if (i==iHighest(Symbol(),TF,MODE_HIGH,kol_bar,na4_bar) && long[i]==0)  
      {
         switch(HighLow(LowBar,HighBar))
         {
            case 1:  //            
            {
               if (NormalizeDouble(iHigh(Symbol(),TF,i),Digits)>NormalizeDouble(iHigh(Symbol(),TF,HighBar),Digits))
               {
                  short[i]=iHigh(Symbol(),TF,i);
                  short[HighBar]=0;
                  HighBar=i;
//                  tek_kol_voln++;
               }
               break;
            }
            case -1:
            {
               if (NormalizeDouble(iHigh(Symbol(),TF,i),Digits)>NormalizeDouble(iLow(Symbol(),TF,LowBar),Digits))
               {
                  short[i]=iHigh(Symbol(),TF,i);
                  HighBar=i;
                  tek_kol_voln++;
               }
               break;
            }
            case 0:  //            .
            {
               short[i]=iHigh(Symbol(),TF,i);
               HighBar=i;
               tek_kol_voln++;
               break;
            }
         }
      }
      if (tek_kol_voln>kol_voln)break;
   }

   kol_bars=i;
   if (Out_Graf) //              
   {
      if (Period()<=TF)
      {
         del_obj(nom_ind);
         int LastExtremumBar     = -1;
         for(i=kol_bars;i>=Na4_Bar_Fract;i--)
         {
            if (long[i]!=0 || short[i]!=0)
            {
               if (LastExtremumBar!=-1)
               {
                  if (long[i]!=0)
                  {
                     int Nom_Bar1= iBarShift(Symbol(),Period(),iTime(Symbol(),TF,LastExtremumBar));
                     int Nom_Bar12= iBarShift(Symbol(),Period(),iTime(Symbol(),TF,LastExtremumBar-1));
                     if (LastExtremumBar==0)Nom_Bar12=0;
                     int j1=Nom_Bar1;
                     if (Nom_Bar1<=MathMin(kol_bars,Bars-1))
                     {
                        for (j1=Nom_Bar1;j1>=Nom_Bar12;j1--)if (short[LastExtremumBar]==High[j1])break;
                        if (j1<Nom_Bar12)j1=Nom_Bar1;
                     }
                  
                     int Nom_Bar2= iBarShift(Symbol(),Period(),iTime(Symbol(),TF,i));
                     Nom_Bar12= iBarShift(Symbol(),Period(),iTime(Symbol(),TF,i-1));
                     if (i==0)Nom_Bar12=0;
                     int j2=Nom_Bar2;
                     if (Nom_Bar2<=MathMin(kol_bars,Bars-1))
                     {
                        for (j2=Nom_Bar2;j2>=Nom_Bar12;j2--)if (long[i]==Low[j2])break;
                        if (j2<Nom_Bar12)j2=Nom_Bar2;
                     }
                  
                     ObjectCreate(StringConcatenate("Trend_",nom_ind,"_",i),OBJ_TREND,0,
                        Time[j1],short[LastExtremumBar],Time[j2],long[i]);
                     ObjectSet(StringConcatenate("Trend_",nom_ind,"_",i),OBJPROP_COLOR,col_DW);
                  }
                  if (short[i]!=0)
                  {
                     Nom_Bar1= iBarShift(Symbol(),Period(),iTime(Symbol(),TF,LastExtremumBar));
                     Nom_Bar12= iBarShift(Symbol(),Period(),iTime(Symbol(),TF,LastExtremumBar-1));
                     if (LastExtremumBar==0)Nom_Bar12=0;
                     j1=Nom_Bar1;
                     if (Nom_Bar1<=MathMin(kol_bars,Bars-1))
                     {
                        for (j1=Nom_Bar1;j1>=Nom_Bar12;j1--)if (long[LastExtremumBar]==Low[j1])break;
                        if (j1<Nom_Bar12)j1=Nom_Bar1;
                     }
                     
                     Nom_Bar2= iBarShift(Symbol(),Period(),iTime(Symbol(),TF,i));
                     Nom_Bar12= iBarShift(Symbol(),Period(),iTime(Symbol(),TF,i-1));
                     if (i==0)Nom_Bar12=0;
                     j2=Nom_Bar2;
                     if (Nom_Bar2<=MathMin(kol_bars,Bars-1))
                     {
                        for (j2=Nom_Bar2;j2>=Nom_Bar12;j2--)if (short[i]==High[j2])break;
                        if (j2<Nom_Bar12)j2=Nom_Bar2;
                     }

                     ObjectCreate(StringConcatenate("Trend_",nom_ind,"_",i),OBJ_TREND,0,
                        Time[j1],long[LastExtremumBar],Time[j2],short[i]);
                     ObjectSet(StringConcatenate("Trend_",nom_ind,"_",i),OBJPROP_COLOR,col_UP);
                  }
                  ObjectSet(StringConcatenate("Trend_",nom_ind,"_",i),OBJPROP_RAY,0);
                  ObjectSet(StringConcatenate("Trend_",nom_ind,"_",i),OBJPROP_WIDTH,1);
               }
               LastExtremumBar=i;
            }
         }
      }
   }
   else
      del_obj(nom_ind);
   
   for(i=0;i<Razm_Mas_Fract;i++)
   {
      if (short[i]!=0) long[i]=short[i];
      mas_extremum[i][0][nom_ind]=0.0;
      mas_extremum[i][1][nom_ind]=0.0;
   }
   
   kol_mas_extr=0;
   for(i=0;i<Razm_Mas_Fract;i++)
      if (long[i]!=0)
      {
         mas_extremum[kol_mas_extr][0][nom_ind]=NormalizeDouble(long[i],Digits);
         mas_extremum[kol_mas_extr][1][nom_ind]=NormalizeDouble(i,0);
         kol_mas_extr++;
      }
      
   return(0);
}
//+------------------------------------------------------------------+
int HighLow(int L, int H)
{
         //               
   if (L == -1 && H >=  0) return(1);  //                  ,               ,               
   if (L >=  0 && H == -1) return(-1); //                  ,               ,              
         //                    
   if (L >=  0 && H >=  0)
   {
      if (L < H) return(1);   //                    
      if (L > H) return(-1);  //                    
   }
   return(0);  // (L==-1   H==-1)           .        . -               
}
//------------------------------------------------------------------------
void del_obj(int nom)
{
   for(int i=Razm_Mas_Fract;i>=0;i--)
      if (ObjectFind(StringConcatenate("Trend_",nom,"_",i))!=-1)
         ObjectDelete(StringConcatenate("Trend_",nom,"_",i));
}
//=============================================================
bool Out_Kanal(int TF, int Fr_Bars, double& mas_ext[][][], int nom_graf, int& kol_mas_ext, color col_fract, bool out_gr,
               int& end_bar, int& beg_bar, datetime& time2, datetime& time1, color col_kanal, 
               double& tg, int& proboi, double& pr1_min, double& pr1_max, int nom_voln_end, double& pr0)
{   
   //                              
   Put_mas_fract_and_extr(TF, Fr_Bars, col_fract,col_fract,nom_graf, mas_ext,kol_mas_ext, out_gr, nom_voln_end+5);

   beg_bar=mas_ext[0][1][nom_graf];
   time1=iTime(Symbol(),TF,beg_bar);
   end_bar=mas_ext[nom_voln_end][1][nom_graf];
   time2=iTime(Symbol(),TF,end_bar);
   
   opred_gran_kanala(TF, nom_graf, end_bar, beg_bar, tg, time2, time1,col_kanal, pr1_min, pr1_max, proboi, pr0);
   
   return(0);
}
//+------------------------------------------------------------------+
bool opred_gran_kanala(int TF, int k, int& end_bar, int& beg_bar, double& tg,
                       datetime& time_line2, datetime& time_line1, color col_kan,
                       double& pr1_min, double& pr1_max, int& proboi, double& pr0)
{ 
   bool out;
   double pr_min, pr_max;
   double pr1, pr2, max_d;
       
   while (true) 
   {
      out=form_channel(TF, k, end_bar, beg_bar, time_line2, time_line1, tg, pr1_min, pr1_max, col_kan, pr0, pr_min, pr_max, pr1, pr2, max_d);
      
      proboi=proboi_kanala(TF,  beg_bar, pr_min, pr_max);
      
      if (proboi!=0)break;  //                  ,      
      if (beg_bar<=1)
      {
         if (beg_bar<1)
         {
            beg_bar=1;
            out=form_channel(TF, k, end_bar, beg_bar, time_line2, time_line1, tg, pr1_min, pr1_max, col_kan, pr0, pr_min, pr_max, pr1, pr2, max_d);
         }
         break;
      }
      beg_bar--;
      time_line1=iTime(Symbol(),TF,beg_bar);
   }
         //                       
   if (out)out_channel(TF, k, pr1, pr2, max_d, time_line1, time_line2, col_kan);

   return(out);
}
//+------------------------------------------------------------------+
int proboi_kanala(int TF, int beg_bar, double pr_min, double pr_max)
{
   int out=0;
   if (beg_bar >= 1)
   {
      if (iClose(Symbol(),TF,beg_bar-1)>pr_max)
         out =  1;
      else
         if (iClose(Symbol(),TF,beg_bar-1)<pr_min)
            out = -1;
   }
   return(out);
}
//+------------------------------------------------------------------+
bool form_channel(int TF, int n, int& end_bar, int& beg_bar, datetime& time_line2, datetime& time_line1, double& tg,
               double& pr0_min, double& pr0_max, color col_kanl, double& pr0, double& pr_min, double& pr_max,
               double& pr1, double& pr2, double& max_d)
{
   pr1=0.0; //                         
   pr2=0.0; // pr1 -            ,                        ; pr2 -        
   
         //                                          ,                           
   if (time_line1<=time_line2)time_line1=iTime(Symbol(),TF,1);

   beg_bar=iBarShift(Symbol(),TF,time_line1);
   end_bar=iBarShift(Symbol(),TF,time_line2);
   
        //                                  
   if  (!opred_MNK(TF, beg_bar, end_bar, pr1, pr2))return(0); //                     
      
      //                         
   tg=(pr1-pr2)/(end_bar-beg_bar); // >0 -             , <0 -            
   
      //                            (                                        ): max_d
   double d, pr_bar;
   max_d=0;
   for(int i=beg_bar;i<=end_bar;i++)
   {
      pr_bar=pr1+tg*(beg_bar-i);  //                                                             i-       
      d=MathAbs(pr_bar-iClose(Symbol(),TF,i));
      if (d>max_d)max_d=d;
   }
      //---------------------------
         //                      .                                             
   pr_max=pr1+max_d;
   pr_min=pr1-max_d;
   
   pr0_max=pr_max;
   pr0_min=pr_min;

   return(1);
}
//---------------------------
void out_channel(int TF, int n, double pr1, double pr2, double max_d, double time_line1, double time_line2, color col_kanl)
{
      //                         
   double pr1_max=pr1+max_d;
   double pr1_min=pr1-max_d;
   
      //                         
   double pr2_max=pr2+max_d;
   double pr2_min=pr2-max_d;
   
   if (Period() <= TF)
   {
      out_TL("TL_max" +str_TF(n), pr1_max, pr2_max, time_line1, time_line2, col_kanl, 2, STYLE_SOLID);
      out_TL("TL_cenr"+str_TF(n), pr1,     pr2,     time_line1, time_line2, col_kanl, 1, STYLE_DASH);
      out_TL("TL_min" +str_TF(n), pr1_min, pr2_min, time_line1, time_line2, col_kanl, 1, STYLE_SOLID);
   }
   else
   {
      del_obj(n);
      ObjectDelete("TL_max" +str_TF(n));
      ObjectDelete("TL_cenr"+str_TF(n));
      ObjectDelete("TL_min" +str_TF(n));
   }
}
//---------------------------
void out_TL(string name, double pr1, double pr2, datetime t1, datetime t2, color col, int width, int style)
{
   if (ObjectFind(name)<0)ObjectCreate(name, OBJ_TREND, 0, t2, pr2, t1, pr2);
   ObjectSet(name,OBJPROP_COLOR, col);
   ObjectSet(name,OBJPROP_RAY, true);
   ObjectSet(name,OBJPROP_WIDTH, width);
   ObjectSet(name,OBJPROP_STYLE, style);
   ObjectSet(name,OBJPROP_TIME1, t2);
   ObjectSet(name,OBJPROP_TIME2, t1);
   ObjectSet(name,OBJPROP_PRICE1,pr2);
   ObjectSet(name,OBJPROP_PRICE2,pr1);
}
//--------------------------------------
string str_TF(int n)
{
   switch(n)
   {
      case 0: return("M1");
      case 1: return("M5");
      case 2: return("M15");
      case 3: return("M30");
      case 4: return("H1");
      case 5: return("H4");
      case 6: return("D1");
      case 7: return("W1");
      case 8: return("MN");
   }
   return("??");
}
//--------------------------------------
bool opred_MNK(int TF, int bar_na4, int bar_kon, double& pr1, double& pr2)
{     //                                                           (MNK) http://multitest.semico.ru/mnk.htm
      //  . .               y=a*x+b                                Sxy=a*Sx2+b*Sx, Sy=a*Sx+n*b
   bool revers;
   if (bar_na4>bar_kon)
   {
      int k=bar_na4;
      bar_na4=bar_kon;
      bar_kon=k;
      revers=true;
   }
   double sum_x=0,sum_y=0,sum_x2=0,sum_xy=0,n=0;
   for (int x=bar_na4;x<=bar_kon;x++)
   {
      sum_x  += 1.0*x;                    // Sx
      sum_x2 += 1.0*x*x;                  // Sx2
      sum_y  += iClose(Symbol(),TF,x);    // Sy
      sum_xy += iClose(Symbol(),TF,x)*x;  // Sxy
      n++;     //                 
   }
   
   if (n==0 || (n*sum_x2-sum_x*sum_x)==0.0)return(0);
   
      //                                    .           y=a*x+b
   double a=(n*sum_xy-sum_x*sum_y)/(n*sum_x2-sum_x*sum_x);
   double b=(sum_y-a*sum_x)/n;
      //                        
   pr1=a*bar_na4+b;
   pr2=a*bar_kon+b;
   if (revers)
   {
      double m=pr1;
      pr1=pr2;
      pr2=m;
   }
   return(1);
}
//===========================================================