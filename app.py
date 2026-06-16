import streamlit as st
import math
import pandas as pd

# Módulo 1: Conversiones Basicas y Complementos (8 bits)

def binario_decimal(n: str):
    if not n:
        return "Error: Cadena vacia."
    
    signo_char = '+' if n[0] == '0' else '-'
    magnitud = n[1:]
    
    if not magnitud:
        return f"RESPUESTA: {signo_char}0"
    
    # Invert to iterate from lowest significant bit
    magnitud_rev = magnitud[::-1]
    
    bina = [1, 2, 4, 8, 16, 32, 64, 128]
    suma = 0
    t = len(magnitud_rev)
    
    for i in range(t):
        if magnitud_rev[i] == '1':
            if i < 8:
                suma += bina[i]
            else:
                suma += 2**i
                
    return f"RESPUESTA: {signo_char}{suma}"

def decimal_binario(dato: int):
    original = dato
    dato = abs(dato)
    respuesta = []
    
    if dato == 0:
        respuesta.append('0')
        
    while dato >= 2:
        residuo = dato % 2
        respuesta.append('1' if residuo == 1 else '0')
        dato = dato // 2
        
    if dato == 1:
        respuesta.append('1')

    while len(respuesta) < 7:
        respuesta.append('0')
        
    if original >= 0:
        respuesta.append('0')
    else:
        respuesta.append('1')
        
    respuesta.reverse()
    res3 = "".join(respuesta)
    return f"RESPUESTA (Signo Magnitud): {res3}"

def decimal_a_c1(dato: int):
    if dato < -127 or dato > 127:
        return "Error: El numero esta fuera del rango para 8 bits (-127 a 127).", None
    
    valor = abs(dato)
    binario = ""
    for _ in range(8):
        binario = ("0" if valor % 2 == 0 else "1") + binario
        valor //= 2
        
    pasos = f"Binario Base (Magnitud): {binario}\n"
    
    if dato < 0:
        binario_inv = "".join(['1' if b == '0' else '0' for b in binario])
        pasos += f"RESPUESTA (Complemento a 1): {binario_inv}"
        return pasos, binario_inv
    else:
        pasos += f"RESPUESTA (Complemento a 1): {binario}"
        return pasos, binario

def decimal_a_c2(dato: int):
    if dato < -128 or dato > 127:
        return "Error: El numero esta fuera del rango para 8 bits (-128 a 127).", None
        
    if dato == -128:
        return "RESPUESTA (Complemento a 2): 10000000", "10000000"
        
    valor = abs(dato)
    binario = ""
    for _ in range(8):
        binario = ("0" if valor % 2 == 0 else "1") + binario
        valor //= 2
        
    if dato >= 0:
        return f"RESPUESTA (Complemento a 2): {binario} (Al ser positivo, no cambia)", binario
        
    binario_list = ['1' if b == '0' else '0' for b in binario]
    pasos = f"Paso 1 (Invertir bits - C1): {''.join(binario_list)}\n"
    
    acarreo = 1
    for i in range(7, -1, -1):
        if binario_list[i] == '1' and acarreo == 1:
            binario_list[i] = '0'
            acarreo = 1
        elif binario_list[i] == '0' and acarreo == 1:
            binario_list[i] = '1'
            acarreo = 0
            break
            
    res = ''.join(binario_list)
    pasos += f"RESPUESTA (Complemento a 2): {res}"
    return pasos, res

# Módulo 2: Algoritmo de Booth (8 Bits)
def bitset8(n: int) -> str:
    return format(n & 0xFF, '08b')

def algoritmoBooth(multiplicando: int, multiplicador: int, conSigno: bool):
    MASCARA_8BITS = 0xFF
    BIT_SIGNO = 0x80
    
    if not conSigno:
        multiplicando &= MASCARA_8BITS
        multiplicador &= MASCARA_8BITS
    else:
        multiplicando = ((multiplicando + 128) & MASCARA_8BITS) - 128
        multiplicador = ((multiplicador + 128) & MASCARA_8BITS) - 128
        
    M = multiplicando & MASCARA_8BITS
    Q = multiplicador & MASCARA_8BITS
    A = 0
    Q_1 = 0
    
    binM = M & MASCARA_8BITS
    menosM = (-M) & MASCARA_8BITS
    
    pasos_html = f"<b>M</b> = {multiplicando if conSigno else binM} &nbsp;&nbsp;|&nbsp;&nbsp; <b>M</b>: {bitset8(binM)} &nbsp;&nbsp;|&nbsp;&nbsp; <b>-M (C2)</b>: {bitset8(menosM)}<br>"
    pasos_html += f"<b>Q</b> = {multiplicador if conSigno else Q & MASCARA_8BITS} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Q</b>: {bitset8(Q)}<br><br>"
    
    rows = []
    rows.append({"Cuenta": "8", "A": bitset8(A), "Q": bitset8(Q), "Q_1": str(Q_1)})
    
    for i in range(8, 0, -1):
        ultimoBitQ = Q & 1
        strCuenta = f"{i} -> {i-1}"
        
        if ultimoBitQ == 1 and Q_1 == 0:
            A = (A - M) & MASCARA_8BITS
            rows.append({"Cuenta": str(i), "A": bitset8(A), "Q": bitset8(Q), "Q_1": str(Q_1)})
        elif ultimoBitQ == 0 and Q_1 == 1:
            A = (A + M) & MASCARA_8BITS
            rows.append({"Cuenta": str(i), "A": bitset8(A), "Q": bitset8(Q), "Q_1": str(Q_1)})
            
        bitMenosSignificativoA = A & 1
        bitMenosSignificativoQ = Q & 1
        
        Q = (Q >> 1) & 0x7F
        Q |= (bitMenosSignificativoA << 7)
        
        bitSignoA = A & BIT_SIGNO
        A = (A >> 1) & 0x7F
        A |= bitSignoA
        
        Q_1 = bitMenosSignificativoQ
        rows.append({"Cuenta": strCuenta, "A": bitset8(A), "Q": bitset8(Q), "Q_1": str(Q_1)})
        
    resultadoFinal = (A << 8) | Q
    if conSigno and (resultadoFinal & 0x8000):
        resultadoFinal = resultadoFinal - 65536
        
    mul1 = multiplicando if conSigno else (multiplicando & MASCARA_8BITS)
    mul2 = multiplicador if conSigno else (multiplicador & MASCARA_8BITS)
        
    resultado_texto = f"<b>Resultado:</b><br>"
    resultado_texto += f"A Q = {bitset8(A)} {bitset8(Q)} ({resultadoFinal} en decimal)<br>"
    resultado_texto += f"{mul1} x {mul2} = {resultadoFinal}"
    
    return pasos_html, rows, resultado_texto

# Módulo 3: Coma Flotante IEEE 754
def decimal_a_ieee754(numero: float):
    if numero == 0.0:
        return "0|00000000|00000000000000000000000", "0", "00000000", "00000000000000000000000"
        
    signo = "1" if numero < 0 else "0"
    valor = abs(numero)
    
    parte_entera = int(valor)
    parte_fraccionaria = valor - parte_entera
    
    entera_bin = ""
    if parte_entera == 0:
        entera_bin = "0"
    while parte_entera > 0:
        entera_bin = ("0" if parte_entera % 2 == 0 else "1") + entera_bin
        parte_entera //= 2
        
    fracc_bin = ""
    while parte_fraccionaria > 0 and len(fracc_bin) < 30:
        parte_fraccionaria *= 2
        if parte_fraccionaria >= 1.0:
            fracc_bin += "1"
            parte_fraccionaria -= 1.0
        else:
            fracc_bin += "0"
            
    exponente_real = 0
    mantisa = ""
    
    if entera_bin != "0":
        exponente_real = len(entera_bin) - 1
        mantisa = entera_bin[1:] + fracc_bin
    else:
        primer_uno = fracc_bin.find('1')
        if primer_uno != -1:
            exponente_real = -(primer_uno + 1)
            mantisa = fracc_bin[primer_uno + 1:]
            
    exponente_sesgado = exponente_real + 127
    exponente_bin = ""
    for _ in range(8):
        exponente_bin = ("0" if exponente_sesgado % 2 == 0 else "1") + exponente_bin
        exponente_sesgado //= 2
        
    if len(mantisa) < 23:
        mantisa = mantisa + "0" * (23 - len(mantisa))
    else:
        mantisa = mantisa[:23]
        
    return f"{signo}(signo) | {exponente_bin}(exponente) | {mantisa}(mantisa)", signo, exponente_bin, mantisa

# Módulo 4: Multiplicación Sin Signo
def multiplicacionSinSignoDiagrama(multiplicando: int, multiplicador: int):
    MASCARA_8BITS = 0xFF
    M = multiplicando & MASCARA_8BITS
    Q = multiplicador & MASCARA_8BITS
    A = 0
    C = 0
    cuenta = 8
    
    header = f"<b>M</b> = {M} &nbsp;&nbsp;|&nbsp;&nbsp; <b>M (Binario)</b>: {bitset8(M)}<br>"
    header += f"<b>Q</b> = {Q} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Q (Binario)</b>: {bitset8(Q)}<br><br>"
    
    rows = []
    rows.append({"Cuenta": str(cuenta), "C": str(C), "A": bitset8(A), "Q": bitset8(Q), "Operación": "Inicio"})
    
    while cuenta > 0:
        Q0 = Q & 1
        op_realizada = ""
        
        if Q0 == 1:
            suma = A + M
            A = suma & MASCARA_8BITS
            C = 1 if suma > 0xFF else 0
            rows.append({"Cuenta": "", "C": str(C), "A": bitset8(A), "Q": bitset8(Q), "Operación": "A = A + M"})
            
        bit_saliente_A = A & 1
        bit_saliente_C = C
        
        Q = (Q >> 1) & 0x7F
        Q |= (bit_saliente_A << 7)
        
        A = (A >> 1) & 0x7F
        A |= (bit_saliente_C << 7)
        
        C = 0
        cuenta -= 1
        rows.append({"Cuenta": str(cuenta), "C": str(C), "A": bitset8(A), "Q": bitset8(Q), "Operación": "Desplazamiento"})
        
    productoFinal = (A << 8) | Q
    
    resultado = f"<b>Resultado Final (A Q):</b><br>"
    resultado += f"Binario: {bitset8(A)} {bitset8(Q)}<br>"
    resultado += f"Decimal: {productoFinal}<br>"
    resultado += f"Comprobacion: {M} x {Q} = {M * Q}"
    
    return header, rows, resultado

# ===============================
# INTERFAZ DE STREAMLIT
# ===============================
st.set_page_config(page_title="Calculadora de Arquitectura", layout="wide")

st.title("Calculadora de Arquitectura de Computadoras")
st.markdown("Herramienta interactiva para conversiones numéricas, algoritmos de multiplicación y coma flotante.")

menu = ["Signo Magnitud", "Complemento a 1", "Complemento a 2", "Multiplicación de Booth", "Coma Flotante (IEEE 754)", "Multiplicación Sin Signo"]
choice = st.sidebar.selectbox("Seleccione una opción", menu)

if choice == "Signo Magnitud":
    st.header("Signo Magnitud")
    op2 = st.radio("Elija la conversión:", ("Binario a Decimal", "Decimal a Binario"))
    
    if op2 == "Binario a Decimal":
        binario = st.text_input("Ingrese el dato binario (ej: 10001010):")
        if st.button("Calcular"):
            if all(c in '01' for c in binario) and len(binario) > 0:
                res = binario_decimal(binario)
                st.success(res)
            else:
                st.error("Por favor ingrese un número binario válido.")
                
    elif op2 == "Decimal a Binario":
        decimal = st.number_input("Ingrese el dato decimal:", step=1, format="%d")
        if st.button("Calcular"):
            res = decimal_binario(int(decimal))
            st.success(res)

elif choice == "Complemento a 1":
    st.header("Complemento a 1 (8 bits)")
    dato_c1 = st.number_input("Ingrese un número decimal (-127 a 127):", min_value=-127, max_value=127, step=1)
    if st.button("Calcular"):
        texto, bin_res = decimal_a_c1(dato_c1)
        st.text(texto)

elif choice == "Complemento a 2":
    st.header("Complemento a 2 (8 bits)")
    dato_c2 = st.number_input("Ingrese un número decimal (-128 a 127):", min_value=-128, max_value=127, step=1)
    if st.button("Calcular"):
        texto, bin_res = decimal_a_c2(dato_c2)
        st.text(texto)

elif choice == "Multiplicación de Booth":
    st.header("Algoritmo de Booth (8 Bits)")
    opBooth = st.radio("Tipo de multiplicación:", ("CON Signo", "SIN Signo"))
    col1, col2 = st.columns(2)
    with col1:
        num1 = st.number_input("Primer número (Multiplicando):", step=1)
    with col2:
        num2 = st.number_input("Segundo número (Multiplicador):", step=1)
        
    if st.button("Calcular por Booth"):
        conSigno = (opBooth == "CON Signo")
        header_html, rows, result_html = algoritmoBooth(int(num1), int(num2), conSigno)
        
        st.markdown(header_html, unsafe_allow_html=True)
        df = pd.DataFrame(rows)
        st.table(df)
        st.markdown(result_html, unsafe_allow_html=True)

elif choice == "Coma Flotante (IEEE 754)":
    st.header("Conversión a Coma Flotante (IEEE 754)")
    numFloat = st.number_input("Ingrese el número decimal (ejemplo: -13.625):", format="%.5f")
    if st.button("Convertir a IEEE 754"):
        texto, s, e, m = decimal_a_ieee754(float(numFloat))
        st.success(f"RESULTADO: {texto}")
        
        st.markdown("### Representación:")
        st.markdown(f"<div style='font-family: monospace; font-size: 20px;'><span style='color:red;'>{s}</span> <span style='color:blue;'>{e}</span> <span style='color:green;'>{m}</span></div>", unsafe_allow_html=True)
        st.markdown("<small><span style='color:red;'>Rojo: Signo</span> | <span style='color:blue;'>Azul: Exponente</span> | <span style='color:green;'>Verde: Mantisa</span></small>", unsafe_allow_html=True)

elif choice == "Multiplicación Sin Signo":
    st.header("Multiplicación Binaria Sin Signo")
    col1, col2 = st.columns(2)
    with col1:
        a = st.number_input("Multiplicando (A):", min_value=0, step=1)
    with col2:
        b = st.number_input("Multiplicador (B):", min_value=0, step=1)
        
    if st.button("Calcular"):
        header, rows, resultado = multiplicacionSinSignoDiagrama(int(a), int(b))
        st.markdown(header, unsafe_allow_html=True)
        df = pd.DataFrame(rows)
        st.table(df)
        st.markdown(resultado, unsafe_allow_html=True)

st.markdown("---")
st.markdown("")
