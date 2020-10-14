# Importamos a misc para el manejo de imagenes
from scipy import misc
from skimage.color import rgb2hsv
import numpy as np
from math import log
import itertools
from time import time
import scipy.io as sio

#paramatros calculo Temperatura
c2=1.4385e-2;
lambda_B=473.5e-9;
lambda_G=540e-9;
lambda_R=615e-9; 

#variables
#T= sio.loadmat('T2.mat')
T = np.loadtxt('T.txt', dtype=float)
c1=1.498e-15;  #Primera constante de Planck
i1 = 0#813; #espectro en 580 nm
i2 = 1#992; #espectro en 620 nm
pl1=580e-9;
pl2=620e-9;
maxTf=5000         #limite superior de Tf
minTf=1000         #limite inferior de Tf
avg_Tf_spect=0

def calculo_mascara(imagen,uu,vv):
    #cambiamos a hvs
    hsv_img = rgb2hsv(imagen)
    #estiramos el verctor
    valor=np.reshape(hsv_img[:,:,2], (uu*vv,1)) 
    #calculamos los percentiles
    delta_min=np.percentile(valor, 99, interpolation='midpoint') #valor normalizado por 1/255
    #print('delta min=', delta_min) #se debe multiplicar por 255 para calzar con matlab
    delta_max=np.percentile(valor, 100, interpolation='midpoint') #valor normalizado por 1/255
    #print('delta max=', delta_max) #se debe multiplicar por 255 para calzar con matlab

    #calcula mask por cada imagen, conservando pixeles que estan en el rango delta_min<pixel(x,y)<delta_max
    foreground_min = hsv_img[:,:,2] > (delta_min*255 - 2)/255     # marca cuando intensidad es mayor que delta_min  
    #foreground_min.astype('uint8')
    #print('tamano de la mascara minima',foreground_min.size)
    foreground_max = hsv_img[:,:,2] < delta_max         # marca cuando intensidad es menor que delta_max
    #foreground_max.astype('uint8')
    #print('tamano de la mascara maxima',foreground_max.size)
    #foreground=double(foreground_min.*foreground_max);     %% combina foreground min y max para calcular mask final
    foreground=foreground_min*foreground_max         #opcion de convinacion para mascara final
    #print('tamano de la mascara final',foreground)
    
    return foreground

    
def calculo_matriz_temperatura(R,G,B,vv,uu):   
    Tf=np.zeros((uu,vv))  #creamos la matriz de temperaturas
    rho=np.zeros(3)
    #start_time = time()
    #calcula temperatura de llama por pixel
    for n1 in range(vv):
      for n2 in range(uu):
        #ajusta ganancia de los canales para calcular Tf con recup espectral
        rho[0]=float(R[n2,n1])
        rho[1]=0.7677*float(G[n2,n1])
        rho[2]=0.3197*float(B[n2,n1])
        #Arias + Castillo: Tf con recup espectral
        if rho[0] >= 8 and rho[0] < 245: # compara intensidad del canal R 
          pE1 = np.sum(T[i1,:]*rho) #T[0,0]*rho[0]+ T[0,1]*rho[1]+ T[0,2]*rho[2]
          #print('valor de pE1',pE1)
          pE2 = np.sum(T[i2,:]*rho) #T[1,0]*rho[0]+ T[1,1]*rho[1]+ T[1,2]*rho[2]
           
          # print('valor de pE2',pE2)
           
          num=(c2*(pl1-pl2)/(pl1*pl2))
          #print('valor de dentro del log',pE1*pl1**5)
          if pE1<0:
            Tp=0
            print("es cero")
          else:
            denom=(log((pE1*pl1**5)/(pE2*pl2**5)))
            Tp = num/denom
            #test sobrepaso limites
            if Tp>maxTf: # nivel superior
              Tf[n2,n1]=maxTf
            elif Tp<minTf: # nivel inferior
              Tf[n2,n1]=minTf
            else: # minTf < Tf < maxTf valor correcto
              Tf[n2,n1]=Tp                   
        else:       
          Tf[n2,n1]=0
            
           
    return Tf

def Tf_rec_spectral(ruta):
    img = misc.imread(ruta)  # Leemos la imagen  #ruta 'imagenes_llama/Llama (1).tiff'
    #print(type(img))
    [uu,vv,rr]=img.shape  #calculamos el tamano de la imagen
    #print('ancho', uu)
    #print('largo',vv)
    #print('canal', rr)
    
    foreground=calculo_mascara(img,uu,vv) #se calcula la mascara de la imagen
    
    #aplica mascara a una copia de la imagen, deja solo los pixeles en los que existe llama
    imag_R = img[:,:,0]*foreground
    imag_G=  img[:,:,1]*foreground  
    imag_B=  img[:,:,2]*foreground  
    #print('tamano de R',imag_R.size)
    #print('tamano de G',imag_G.size)
    #print('tamano de B',imag_B.size)
    
    Tf=calculo_matriz_temperatura(imag_R,imag_G,imag_B,vv,uu)
        
    #calcula Tf promedio por imagen 
    avg_Tf_spect=np.mean(Tf[np.nonzero(Tf)])
    
    return avg_Tf_spect #fin de la funcion


#funcion principal 
f=open("Tf_rec_spectral_temp.txt","w")
f1=open("Tf_rec_spectral_tiempo.txt","w")
for k in range(25):
  nombre_archivo='imagenes_llama/Llama ('+str(k+1)+').tiff'
  start_time = time()
  temperatura= Tf_rec_spectral(nombre_archivo) #calculo de la temperatura para la imagen nombre_archivo
  elapsed_time = time() - start_time
  
  f.write(str(temperatura)+'\n')
  f1.write(str(elapsed_time)+'\n')
  
  #print('la temperatura es',temperatura)
  #print('el tiempo es',elapsed_time)

f.close()
f1.close()

#calcula Tf promedio por imagen 
#avg_Tf_spect=np.mean(Tf[np.nonzero(Tf)])
#print('La temperatura promedio es', avg_Tf_spect)

#elapsed_time = time() - start_time
#print("Elapsed time: %0.10f seconds." % elapsed_time)
 
#print('sum rho[2] es igual a:',sum)    

# Tipo de dato de la variable "img"
#if img.size== 0:
 # print('no hay imagen')
#else:
 # print(img.shape)
 # print(hsv_img.shape)