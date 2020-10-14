#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>       /* round() */
#include <time.h> 

typedef struct bmpFileHeader
{
  uint32_t size;
  uint16_t resv1;
  uint16_t resv2;
  uint32_t offset;
} bmpFileHeader;

typedef struct bmpInfoHeader
{
  uint32_t headersize;      /* DIB header size */
  uint32_t width;
  uint32_t height;
  uint16_t planes;         /* color planes */
  uint16_t bpp;            /* bits per pixel */
  uint32_t compress;
  uint32_t imgsize;    
  uint32_t bpmx;        /* X bits per meter */
  uint32_t bpmy;        /* Y bits per meter */
  uint32_t colors;      /* colors used */
  uint32_t imxtcolors;      /* important colors */
} bmpInfoHeader;

double max(double a, double b, double c);
double countingSort (double *numbers, int size, double *B, double *C,int perc);
double TF(char *filename);
double calculo_temperatura_direct(double *R,double *G, double *B,int num_pixel);
void leer_matriz_T(double *T);
double calculo_temperatura_rec_spectral(double *R,double *G,double *B,int num_pixel);

int main()
{
  FILE* tiempo;
  FILE* valor;
  tiempo = fopen("C_tf_direct_tem.txt", "wt");
  valor = fopen("C_tf_direct_tiempo.txt", "wt");
  char tempe[100];
  char tiemp[100];
  for(int i=0; i<1; i++){
    char* result;
    asprintf(&result, "%s%d%s", "imagenes_llama_bmp/Llama (",i+1,").bmp");
    printf("la rura es %s\n",result);
    clock_t begin = clock(); 
    double temperatura=TF(result);
    clock_t end = clock();
    double time_spent = (double)(end - begin) / CLOCKS_PER_SEC;
    printf("la temperatura es: %6.10f \n", temperatura);
    printf("el tiempo es: %f \n", time_spent);
    gcvt(temperatura, 15, tempe); 
    gcvt(time_spent, 15, tiemp); 
    fputs(tempe, valor);
    fputs(tiemp, tiempo);
  }
  fclose(tiempo);
  fclose(valor);
}



//////////////////////////////////////////////////7
double max(double a, double b, double c) {
   return ((a > b)? (a > c ? a : c) : (b > c ? b : c));
}

double countingSortMain (double *numbers, double k, int size, double *B, double *C,int perc) {
    int i, j, indexB = 0;
    B = (double*) malloc(sizeof(double) * (size + 1));
    C = (double*) calloc((k + 1), sizeof(double));
    for (i = 0; i < size; i++) {
        C[(int)numbers[i]] = C[(int)numbers[i]] + 1;
    }
    for (i=0; i <= k; ++i) {
        for(j=0; j < C[i]; ++j) {
            B[indexB] = i;
            indexB++;
        }
    }
    int x= perc*(size)/100;
    double percentil=(B[x-1]);
    free(B);
    free(C);
    return percentil;
}

double countingSort (double *numbers, int size, double *B, double *C,int perc) {
    int i; 
    double k=-1;
    for (i = 0; i < size; i++) {
        if (numbers[i] > k) {
            k = numbers[i];
        }
    }
    return countingSortMain(numbers, k, size, B, C, perc);
}

double TF(char *filename){
  FILE *f;
  bmpInfoHeader info;
  bmpFileHeader header;
  unsigned char *imgdata;
  uint16_t type;
  int desfase;
  f=fopen (filename, "r");
  /* handle open error */
  fread(&type, sizeof(uint16_t), 1, f);
  if (type !=0x4D42)
    {
      fclose(f);
    }
  fread(&header, sizeof(bmpFileHeader), 1, f);
  desfase=header.offset-54; //corrimiento de 54 consta de la informacion ya leida, header y info (52 bytes) + (2 bytes) aun no descubiertos.
  fread(&info, sizeof(bmpInfoHeader), 1, f);
  double c;
  for(int i=0;i<desfase;i++) c = fgetc(f);

  int numero_pixeles=info.height*info.width;//width*height;//2304000;//(int) width*height;
  int bytes_agregados=info.width%4;
  
  
  //printf("el numero de pixeles es: %d \n", numero_pixeles);
  double* matriz_R=malloc(numero_pixeles*sizeof(double));//=malloc(numero_pixeles*sizeof(int));
  double* matriz_G=malloc(numero_pixeles*sizeof(double));//=malloc(numero_pixeles*sizeof(int));
  double* matriz_B=malloc(numero_pixeles*sizeof(double));//=malloc(numero_pixeles*sizeof(int));
  double* value=malloc(numero_pixeles*sizeof(double));

  double valor_R;
  double valor_G;
  double valor_B;
  for(int i=0;i<numero_pixeles;i++) {
    if(((i+1)%info.width==0)&&(bytes_agregados!=0)){ //esto elimina los bit abregados al final de la linea
      for(int j=0; j<bytes_agregados;j++)
      c = fgetc(f);
    }
    matriz_B[i] = (double)fgetc(f);//valor_B;
    matriz_G[i] = (double)fgetc(f);//valor_G;
    matriz_R[i] = (double)fgetc(f);//valor_R;
    value[i] = max(matriz_R[i], matriz_G[i], matriz_B[i]);
  }
    
  /////////////////calculo de percentiles/////////
  double delta_min;
  double delta_max;
  double* b1=malloc(numero_pixeles*sizeof(double));;
  double* c1=malloc(numero_pixeles*sizeof(double));;
  delta_min=countingSort(value,numero_pixeles, b1, c1,99);
  delta_max=countingSort(value,numero_pixeles, b1, c1,100);
  ///////////////////////////////7
  
  ////aplicación de mascara//////////////7
  for(int i=0;i<numero_pixeles;i++){
    if(value[i]<delta_max && value[i]>delta_min-2){
      matriz_B[i]=matriz_B[i];
      matriz_G[i]=matriz_G[i];
      matriz_R[i]=matriz_R[i];
      }
    else{
      matriz_B[i]=0;
      matriz_G[i]=0;
      matriz_R[i]=0;
    }    
  }
  //////////ccalculo temperatura//////////////////////7
  
  double temp;
  temp=calculo_temperatura_direct(matriz_R,matriz_G, matriz_B,numero_pixeles);
  //temp=calculo_temperatura_rec_spectral(matriz_R,matriz_G, matriz_B,numero_pixeles);


  
  //printf("el numero de pixeles sumados es: %d\n", numero_no_zero);
  //printf("la temperatura es: %6.10f \n", suma/numero_no_zero);
  fclose(f);
  free(b1);
  free(c1);
  free(value);
  free(matriz_R);
  free(matriz_G);
  free(matriz_B);
  return temp;
}

double calculo_temperatura_direct(double *R,double *G,double *B,int num_pixel){
  double c2=1.4385*pow(10,-2);
  double lambda_B=473.5*pow(10,-9);
  double lambda_G=540*pow(10,-9);
  double lambda_R=615*pow(10,-9); 
  double maxTf=3000;         // limite superior de Temperatura
  double minTf=1000;         // limite inferior de Temperatura 
  double I_R;
  double I_G;
  double I_B;
  int numero_no_zero=0;
  double suma=0;
  for(int i=0;i<num_pixel;i++) {
    I_R=(double)R[i]/255;
    I_G=(double)G[i]/255;
    I_B=(double)B[i]/255;
    if(I_R!=0 && I_G!=0 && I_B!=0){
      numero_no_zero=numero_no_zero+1;
      double SS=0.3653*(pow((I_R/I_G),2))-1.669*(I_R/I_G) + 3.392;    // factor de forma obtenido experimental
      double num=c2*(1/(lambda_G)-1/(lambda_R));               //numerador de la ecuacion
      double denom=log(I_R/I_G) + 6*log(lambda_R/lambda_G) + log(SS); //denominador de la ecuacion
      double temp=num/denom; //temperatura calculada
      //test sobrepaso limites
      if (temp>maxTf) {// nivel superior
        suma=suma + maxTf;//Tf[i];
        }
      else if(temp<minTf){ //nivel inferior
        suma=suma + minTf;//Tf[i];
        }
      else {//minTf < Tf < maxTf valor correcto
        suma=suma + temp;//Tf[i];
        }
     } 
    else{
       suma=suma;
       }
    }

//  printf("numeros no zeros %d\n",numero_no_zero);
  return suma/numero_no_zero;
}

double calculo_temperatura_rec_spectral(double *R,double *G,double *B,int num_pixel){ 
  double c2=1.4385*pow(10,-2);
  double lambda_B=473.5*pow(10,-9);
  double lambda_G=540*pow(10,-9);
  double lambda_R=615*pow(10,-9); 
  double pl1=580*pow(10,-9);
  double pl2=620*pow(10,-9);
  double T[6];
  leer_matriz_T(T);
  double pE1;
  double pE2;
  double num;
  double denom;
  double temp;
  int maxTf=5000;         // limite superior de Temperatura
  int minTf=1000;         // limite inferior de Temperatura 
  int numero_no_zero=0;
  double rho[3];

  double suma=0;
  for(int i=0;i<num_pixel;i++) {
    rho[0]=(double)R[i];
    rho[1]=(double)0.7677*G[i];
    rho[2]=(double)0.3197*B[i];
    if(rho[0] >= 8 && rho[0] < 245){
      pE1 = T[0]*rho[0]+ T[1]*rho[1]+ T[2]*rho[2]; //faltan los valores de T
      pE2 = T[3]*rho[0]+ T[4]*rho[1]+ T[5]*rho[2]; //faltan los valores de T
      num=(c2*(pl1-pl2)/(pl1*pl2));//numerador de la ecuacion
      if(pE1<0){
        suma=suma;
        }
      else{
        denom=(log((pE1*pow(pl1,5))/(pE2*pow(pl2,5))));//denominador de la ecuacion
        temp=num/denom; //temperatura calculada
        //test sobrepaso limites
        if (temp>maxTf) {// nivel superior
          suma=suma + maxTf;//Tf[i];
        }
        else if(temp<minTf){ //nivel inferior
          suma=suma + minTf;//Tf[i];
        }    
        else {//minTf < Tf < maxTf valor correcto
          suma=suma + temp;//Tf[i];
        }  
        numero_no_zero=numero_no_zero+1;  
      }
    } 
    else{
       suma=suma;
       }
    }
  return suma/numero_no_zero;
}

void leer_matriz_T(double *T){ 
  FILE* fichero;
  fichero = fopen("T.txt", "r");
  fscanf(fichero, "%lf", &T[0]);
  fscanf(fichero, "%lf", &T[1]);
  fscanf(fichero, "%lf", &T[2]);
  fscanf(fichero, "%lf", &T[3]);
  fscanf(fichero, "%lf", &T[4]);
  fscanf(fichero, "%lf", &T[5]);
  fclose(fichero);
}