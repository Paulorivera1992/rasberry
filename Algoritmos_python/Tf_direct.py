# Importamos a misc para el manejo de imagenes
from scipy import misc
from skimage.color import rgb2hsv
import numpy as np
from math import log
import itertools
from time import time

#paramatros calculo Temperatura
c2=1.4385e-2
lambda_B=473.5e-9
lambda_G=540e-9
lambda_R=615e-9  

#variables
maxTf=3000         # limite superior de Temperatura
minTf=1000         # limite inferior de Temperatura
avg_Tf=0

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
    #calcula temperatura de llama por pixel
    Tf=np.zeros((uu,vv))  #creamos la matriz de temperaturas
    for n1 in range(vv):
      for n2 in range(uu):
        I_R=float(R[n2,n1])/255
        I_G=float(G[n2,n1])/255
        I_B=float(B[n2,n1])/255
        #calcula Tf sin rec espectral por pixel 
        if I_G!=0 and I_R!=0 and I_B!=0:
          #Chen: Tf sin recup espectral
          SS=0.3653*((I_R/I_G)**2)-1.669*(I_R/I_G) + 3.392    # factor de forma obtenido experimental
          num=c2*((1/lambda_G)-(1/lambda_R))               #numerador de la ecuacion
          denom= log(I_R/I_G)  + 6*log(lambda_R/lambda_G) + log(SS) #denominador de la ecuacion # 
          temp=num/denom #temperatura calculada
          #test sobrepaso limites
          if temp>maxTf: # nivel superior
            Tf[n2,n1]=maxTf
          elif temp<minTf: # nivel inferior
            Tf[n2,n1]=minTf
          else: # minTf < Tf < maxTf valor correcto
            Tf[n2,n1]=temp;        
        else:
          Tf[n2,n1]=0
    
    return Tf      
    

def Tf_direct(ruta):
    img = misc.imread(ruta) # Leemos la imagen  #ruta 'imagenes_llama/Llama (1).tiff'
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
    avg_Tf=np.mean(Tf[np.nonzero(Tf)])
  
    return avg_Tf #fin de la funcion

#funcion principal 
f=open("Tf_direct_temp.txt","w")
f1=open("Tf_direct_tiempo.txt","w")
for k in range(1):
  nombre_archivo='imagenes_llama/Llama ('+str(k+1)+').tiff'
  start_time = time()
  temperatura= Tf_direct(nombre_archivo) #calculo de la temperatura para la imagen nombre_archivo
  elapsed_time = time() - start_time
  
  f.write(str(temperatura)+'\n')
  f1.write(str(elapsed_time)+'\n')
  
  #print('la temperatura es',temperatura)
  #print('el tiempo es',elapsed_time)

f.close()
f1.close()
 
 
#print('sum SS es igual a:',sum_num)    
#print('sum_TF', sum(itertools.chain.from_iterable(Tf)))
# Tipo de dato de la variable "img"
#if img.size== 0:
 # print('no hay imagen')
#else:
 # print(img.shape)
 # print(hsv_img.shape)