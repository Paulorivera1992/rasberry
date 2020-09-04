# Importamos a misc para el manejo de imagenes
import numpy as np
from time import time

#mediciones con espectrometro entre 400 - 1000 nm
imin=961                           #ubicacion de \lambda = 399.9 nm
imax=2724                         #ubicacion de \lambda = 800.06 nm
Radt_CCS200=0                     #inicializacion de radt

def trapezoidal(longitudes,intensidades):
    #calculo de area bajo la curva metodo trapeziodal
    area=0
    if longitudes.size==intensidades.size:
      for j in range(intensidades.size):
        if j>1:
          area = area + 0.5*((longitudes[j]-longitudes[j-1])*(intensidades[j]+intensidades[j-1]));
    else:
      print('longitud de matrices es distinto')
      
    return area

def calibracion(intensidades):  
    #calibrar espectro
    #calib=np.ones(Em_CCS200.shape) #esto se puede cargar desde archivo
    calib=np.loadtxt('calib.txt', dtype=float)
    calib=calib[imin:imax]
    Espectro_calibrado=intensidades*calib      #se genera la calibracion   
    
    return Espectro_calibrado
    
def Radt_CCS200(ruta_longitud,ruta_intensidad):
    #cargar longitudes de onda
    wavelength_CCS200=np.loadtxt(ruta_longitud, dtype=float) #cargar longitudes de onda
    #print('longitud de onda minimo',wavelength_CCS200[imin] ) #longitud minima
    #print('longitud de onda maximo',wavelength_CCS200[imax] ) #logitud maxima
    wavelength_CCS200=wavelength_CCS200[imin:imax]    #restringe espectro entre rango 400-800
    #print('tamano de longitudes de onda',wavelength_CCS200.shape)

    #cargar intensidades sin calibrar
    Em_CCS200=np.loadtxt(ruta_intensidad, dtype=float) #cargar intensidades
    Em_CCS200=Em_CCS200[imin:imax]    #restringe espectro entre rango 400-800
    #print('tamano de intensidades',Em_CCS200.shape)

    Em_CCS200=calibracion(Em_CCS200)
    
    Radt_CCS200= 1e-3*trapezoidal(wavelength_CCS200,Em_CCS200)   #calculo de Radt
    #print('Radt tiene un valor de:',Radt_CCS200 )
    
    return Radt_CCS200

#funcion principal 
#f=open("Tf_direct_temp.txt","w")
#f1=open("Tf_direct_tiempo.txt","w")
for k in range(1):
  nombre_archivo='imagenes_llama/Llama ('+str(k+1)+').tiff'
  start_time = time()
  Radt=Radt_CCS200('wavelengthCCS200.txt','ccs200_irad.txt') #calculo de la Radt para la imagen nombre_archivo
  elapsed_time = time() - start_time
  
  #f.write(str(temperatura)+'\n')
  #f1.write(str(elapsed_time)+'\n')
  
  print('la Radt es',Radt)
  print('el tiempo es',elapsed_time)

#f.close()
#f1.close()