import math
import os
import pdb

def leer_datos(filename):
    datos = {}
    fechas = []
    #tengo q usar el latin1 porque con el utf8 se me rompe
    with open(filename, encoding="latin-1") as arch:
        for raw in arch:
            linea = raw.rstrip()
            if not linea.strip() or not linea[0].isdigit(): #para saltearme los encabezados
                continue 
            #ahora corto por posiciones fijas
            fecha = linea[0:8].strip()
            tmax = to_float(linea[9:15])
            tmin = to_float(linea[15:21])
            nombre = linea[21:].strip()
            #hasta acá funciona bien

            if nombre not in datos:
                datos[nombre] = {"tmax": [], "tmin": []}

            datos[nombre]["tmax"].append(tmax)
            datos[nombre]["tmin"].append(tmin)

            if fecha not in fechas:
                fechas.append(fecha)
                
            #print(datos)

    return datos, fechas

def to_float(s):
    s = s.strip()
    if s == "":
        return None
    try:
        return float(s)
    except ValueError:
        return None
        
def generar_reporte(datos, fechas, salida="reporte.txt"):
    import math
    with open(salida, "w", encoding="utf-8") as arch:

        # 1) Reporte por estación: max y min absoluta
        arch.write("== Temperaturas máximas y mínimas por estación ==\n")
        for est, temps in datos.items():
            max_abs = max([t for t in temps["tmax"] if t is not None], default=None)
            min_abs = min([t for t in temps["tmin"] if t is not None], default=None)
            arch.write(f"{est}: Tmax={max_abs}, Tmin={min_abs}\n")

        # 2) Mayor y menor amplitud térmica en un mismo día
        mayor_amp = (-math.inf, None, None)  # (valor, estacion, fecha) Arranco en -infinito y el resto vacío
        menor_amp = (math.inf, None, None)
        for est, temps in datos.items():
            for i, (tmax, tmin) in enumerate(zip(temps["tmax"], temps["tmin"])): #el zip me recorre las 2 listas en paralelo ta buenp
                if tmax is not None and tmin is not None:
                    amp = tmax - tmin
                    if amp > mayor_amp[0]:
                        mayor_amp = (amp, est, fechas[i])
                    if amp < menor_amp[0]:
                        menor_amp = (amp, est, fechas[i])

        arch.write("\n== Amplitud térmica ==\n")
        arch.write(f"Mayor: {mayor_amp[1]} día {mayor_amp[2]} con {mayor_amp[0]:.1f}°C\n")
        arch.write(f"Menor: {menor_amp[1]} día {menor_amp[2]} con {menor_amp[0]:.1f}°C\n")

        # 3) Diferencia entre estaciones el mismo día
        max_diff = (-math.inf, None, None, None, None, None) #(diferencia, fecha, estacion1, amp1, estacion2, amp2)
        min_diff = (math.inf, None, None, None, None, None)

        estaciones = list(datos.keys())

        for i, fecha in enumerate(fechas):
            for indexEstacionBase, estacion1 in enumerate(estaciones): #ese es el q se compara contra el resto
                for estacion2 in estaciones[indexEstacionBase+ 1:]:
                    # verificar que ambas estaciones tengan datos para ese día
                    if i >= len(datos[estacion1]["tmax"]) or i >= len(datos[estacion2]["tmax"]):
                        continue

                    tmax1, tmin1 = datos[estacion1]["tmax"][i], datos[estacion1]["tmin"][i]
                    tmax2, tmin2 = datos[estacion2]["tmax"][i], datos[estacion2]["tmin"][i]

                    if None in (tmax1, tmin1, tmax2, tmin2):
                        continue

                    amp1 = tmax1 - tmin1
                    amp2 = tmax2 - tmin2
                    diff = abs(amp1 - amp2)

                    if diff > max_diff[0]:
                        max_diff = (diff, fecha, estacion1, amp1, estacion2, amp2)
                    if diff < min_diff[0]:
                        min_diff = (diff, fecha, estacion1, amp1, estacion2, amp2)

        arch.write("\n== Diferencias entre estaciones en el mismo día==\n")
        arch.write(f"Máxima diferencia {max_diff[0]:.1f}°C en {max_diff[1]}: "
                   f"{max_diff[2]}({max_diff[3]:.1f}) vs {max_diff[4]}({max_diff[5]:.1f})\n")
        arch.write(f"Mínima diferencia {min_diff[0]:.1f}°C en {min_diff[1]}: "
                   f"{min_diff[2]}({min_diff[3]:.1f}) vs {min_diff[4]}({min_diff[5]:.1f})\n")

def main():
    print("Este es el TP 1 de Agostina Pérez. Generando reporte...")
    base = os.path.dirname(__file__)
    filename = os.path.join(base, "registro_temperatura365d_smn.txt")
    datos, fechas = leer_datos(filename)
    generar_reporte(datos, fechas)
    print("Reporte generado!!")

if __name__ == "__main__": #hago esto x si quisiera importarlo como librería para q no se ejecute solo el scrip
    main()
