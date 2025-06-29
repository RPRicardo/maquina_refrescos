import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
from typing import List, Dict, Any, Optional, Tuple

class Nodo:
    """Representa un nodo en el árbol de derivación"""
    def __init__(self, simbolo: str, tipo: str = "terminal"):
        self.simbolo = simbolo
        self.tipo = tipo  # "terminal" o "no_terminal"
        self.hijos: List['Nodo'] = []
        self.padre: Optional['Nodo'] = None
        
        # Atributos semánticos
        self.saldo = 0
        self.valido = True
        self.nivel = 0
        self.refrescos_comprados = 0
        self.errores: List[str] = []
        
    def agregar_hijo(self, hijo: 'Nodo'):
        """Agrega un hijo al nodo"""
        hijo.padre = self
        self.hijos.append(hijo)
        
    def __str__(self):
        return f"{self.simbolo} (saldo={self.saldo}, valido={self.valido}, nivel={self.nivel})"

class AnalizadorSemantico:
    """Analizador semántico para la máquina expendedora"""
    
    def __init__(self):
        self.errores_globales: List[str] = []
        
    def analizar_cadena(self, cadena: str) -> Tuple[Nodo, bool]:
        """
        Analiza una cadena y construye el árbol de derivación con análisis semántico
        Retorna: (nodo_raiz, es_valida)
        """
        self.errores_globales = []
        
        # Validar sintaxis básica
        if not self._validar_sintaxis(cadena):
            return None, False
            
        # Construir árbol de derivación
        raiz = self._construir_arbol(cadena)
        
        # Decorar con atributos semánticos
        self._decorar_arbol(raiz, nivel=1)
        
        # Verificar validez global
        es_valida = raiz.valido and len(self.errores_globales) == 0
        
        return raiz, es_valida
    
    def _validar_sintaxis(self, cadena: str) -> bool:
        """Validación sintáctica básica"""
        # Verificar que empiece y termine con llaves
        cadena = cadena.strip()
        if not cadena.startswith('{') or not cadena.endswith('}'):
            self.errores_globales.append("La cadena debe empezar con '{' y terminar con '}'")
            return False
            
        # Verificar balance de llaves
        nivel = 0
        for char in cadena:
            if char == '{':
                nivel += 1
            elif char == '}':
                nivel -= 1
                if nivel < 0:
                    self.errores_globales.append("Llaves desbalanceadas")
                    return False
        
        if nivel != 0:
            self.errores_globales.append("Llaves desbalanceadas")
            return False
            
        # Verificar caracteres válidos
        caracteres_validos = set('{}$R< ')
        for char in cadena:
            if char not in caracteres_validos:
                self.errores_globales.append(f"Carácter inválido: '{char}'")
                return False
                
        return True
    
    def _construir_arbol(self, cadena: str) -> Nodo:
        """Construye el árbol de derivación"""
        raiz = Nodo("P", "no_terminal")
        
        # P → { C }
        llave_izq = Nodo("{", "terminal")
        nodo_c = Nodo("C", "no_terminal")
        llave_der = Nodo("}", "terminal")
        
        raiz.agregar_hijo(llave_izq)
        raiz.agregar_hijo(nodo_c)
        raiz.agregar_hijo(llave_der)
        
        # Procesar contenido entre llaves
        contenido = cadena[1:-1].strip()
        self._procesar_contenido(nodo_c, contenido)
        
        return raiz
    
    def _procesar_contenido(self, nodo_c: Nodo, contenido: str):
        """Procesa el contenido de un bloque C"""
        if not contenido:
            # C → ε
            epsilon = Nodo("ε", "terminal")
            nodo_c.agregar_hijo(epsilon)
            return
            
        i = 0
        while i < len(contenido):
            char = contenido[i]
            
            if char == ' ':
                i += 1
                continue
                
            # C → A C
            nodo_a = Nodo("A", "no_terminal")
            nodo_c_siguiente = Nodo("C", "no_terminal")
            nodo_c.agregar_hijo(nodo_a)
            nodo_c.agregar_hijo(nodo_c_siguiente)
            
            if char in ['$', 'R', '<']:
                # A → $ | R | <
                terminal = Nodo(char, "terminal")
                nodo_a.agregar_hijo(terminal)
                i += 1
            elif char == '{':
                # A → { C }
                # Encontrar la llave de cierre correspondiente
                nivel = 1
                j = i + 1
                while j < len(contenido) and nivel > 0:
                    if contenido[j] == '{':
                        nivel += 1
                    elif contenido[j] == '}':
                        nivel -= 1
                    j += 1
                
                bloque_completo = contenido[i:j]
                
                llave_izq = Nodo("{", "terminal")
                nodo_c_interno = Nodo("C", "no_terminal")
                llave_der = Nodo("}", "terminal")
                
                nodo_a.agregar_hijo(llave_izq)
                nodo_a.agregar_hijo(nodo_c_interno)
                nodo_a.agregar_hijo(llave_der)
                
                # Procesar contenido del bloque anidado
                contenido_interno = bloque_completo[1:-1]
                self._procesar_contenido(nodo_c_interno, contenido_interno)
                
                i = j
            else:
                i += 1
            
            # Actualizar nodo_c para la siguiente iteración
            contenido_restante = contenido[i:].strip()
            if not contenido_restante:
                epsilon = Nodo("ε", "terminal")
                nodo_c_siguiente.agregar_hijo(epsilon)
                break
            else:
                nodo_c = nodo_c_siguiente
    
    def _decorar_arbol(self, nodo: Nodo, nivel: int = 1):
        """Decora el árbol con atributos semánticos"""
        nodo.nivel = nivel
        
        # Verificar límite de anidación
        if nivel > 3:
            nodo.valido = False
            nodo.errores.append(f"Excede el límite de 3 niveles de anidación (nivel {nivel})")
            self.errores_globales.append(f"Excede el límite de 3 niveles de anidación")
            return
        
        if nodo.simbolo == "P":
            # P → { C }
            if len(nodo.hijos) >= 2:
                nodo_c = nodo.hijos[1]  # El nodo C
                self._decorar_arbol(nodo_c, nivel)
                nodo.saldo = nodo_c.saldo
                nodo.valido = nodo_c.valido
                nodo.refrescos_comprados = nodo_c.refrescos_comprados
                nodo.errores.extend(nodo_c.errores)
                
        elif nodo.simbolo == "C":
            if len(nodo.hijos) == 1 and nodo.hijos[0].simbolo == "ε":
                # C → ε
                nodo.saldo = 0
                nodo.valido = True
                nodo.refrescos_comprados = 0
            elif len(nodo.hijos) == 2:
                # C → A C
                nodo_a = nodo.hijos[0]
                nodo_c = nodo.hijos[1]
                
                # Decorar A primero
                self._decorar_arbol(nodo_a, nivel)
                
                # Heredar estado de A
                nodo.saldo = nodo_a.saldo
                nodo.valido = nodo_a.valido
                nodo.refrescos_comprados = nodo_a.refrescos_comprados
                nodo.errores.extend(nodo_a.errores)
                
                # Decorar C con el estado actualizado
                nodo_c.saldo = nodo.saldo
                nodo_c.refrescos_comprados = nodo.refrescos_comprados
                self._decorar_arbol(nodo_c, nivel)
                
                # Actualizar estado final
                nodo.saldo = nodo_c.saldo
                nodo.valido = nodo.valido and nodo_c.valido
                nodo.refrescos_comprados = nodo_c.refrescos_comprados
                nodo.errores.extend(nodo_c.errores)
                
        elif nodo.simbolo == "A":
            if len(nodo.hijos) == 1:
                hijo = nodo.hijos[0]
                
                if hijo.simbolo == "$":
                    # Insertar moneda
                    nodo.saldo = (nodo.padre.saldo if nodo.padre else 0) + 1
                    nodo.valido = True
                    nodo.refrescos_comprados = nodo.padre.refrescos_comprados if nodo.padre else 0
                    
                elif hijo.simbolo == "R":
                    # Comprar refresco
                    saldo_actual = nodo.padre.saldo if nodo.padre else 0
                    refrescos_actual = nodo.padre.refrescos_comprados if nodo.padre else 0
                    
                    if saldo_actual < 3:
                        nodo.valido = False
                        nodo.errores.append(f"Saldo insuficiente para comprar refresco (saldo: {saldo_actual}, necesario: 3)")
                        nodo.saldo = saldo_actual
                        nodo.refrescos_comprados = refrescos_actual
                    elif refrescos_actual >= 3:
                        nodo.valido = False
                        nodo.errores.append("Excede el máximo de 3 refrescos por bloque")
                        nodo.saldo = saldo_actual
                        nodo.refrescos_comprados = refrescos_actual
                    else:
                        nodo.saldo = saldo_actual - 3
                        nodo.valido = True
                        nodo.refrescos_comprados = refrescos_actual + 1
                        
                elif hijo.simbolo == "<":
                    # Devolver moneda
                    saldo_actual = nodo.padre.saldo if nodo.padre else 0
                    
                    if saldo_actual < 1:
                        nodo.valido = False
                        nodo.errores.append("No hay monedas para devolver")
                        nodo.saldo = saldo_actual
                    else:
                        nodo.saldo = saldo_actual - 1
                        nodo.valido = True
                    
                    nodo.refrescos_comprados = nodo.padre.refrescos_comprados if nodo.padre else 0
                    
            elif len(nodo.hijos) == 3:
                # A → { C }
                nodo_c = nodo.hijos[1]  # El nodo C interno
                # Incrementar nivel para el bloque anidado
                self._decorar_arbol(nodo_c, nivel + 1)
                
                # El bloque anidado es independiente, no transfiere saldo
                nodo.saldo = nodo.padre.saldo if nodo.padre else 0
                nodo.valido = nodo_c.valido
                nodo.refrescos_comprados = nodo.padre.refrescos_comprados if nodo.padre else 0
                nodo.errores.extend(nodo_c.errores)
        
        # Decorar hijos restantes
        for hijo in nodo.hijos:
            if hijo.simbolo in ["{", "}", "ε"]:
                continue
            if not hasattr(hijo, 'saldo'):
                self._decorar_arbol(hijo, nivel)

    def imprimir_arbol_visual(self, nodo: Nodo, prefijo: str = "", es_ultimo: bool = True, es_raiz: bool = True) -> str:
        """Imprime el árbol de derivación con formato visual decorado"""
        resultado = []
        
        # Construir la línea actual
        if es_raiz:
            linea_actual = ""
        else:
            conector = "└── " if es_ultimo else "├── "
            linea_actual = prefijo + conector
        
        # Mostrar información del nodo
        if nodo.tipo == "no_terminal":
            atributos = f"[saldo={nodo.saldo}, valido={nodo.valido}, nivel={nodo.nivel}, refrescos={nodo.refrescos_comprados}]"
            resultado.append(f"{linea_actual}{nodo.simbolo}{atributos}")
            
            # Mostrar errores si existen
            if nodo.errores:
                error_prefijo = prefijo + ("    " if es_ultimo else "│   ")
                for error in nodo.errores:
                    resultado.append(f"{error_prefijo}⚠ ERROR: {error}")
        else:
            # Para terminales, solo mostrar el símbolo
            resultado.append(f"{linea_actual}{nodo.simbolo}")
        
        # Procesar hijos
        if nodo.hijos:
            # Calcular nuevo prefijo para los hijos
            if es_raiz:
                nuevo_prefijo = ""
            else:
                nuevo_prefijo = prefijo + ("    " if es_ultimo else "│   ")
            
            # Procesar cada hijo
            for i, hijo in enumerate(nodo.hijos):
                es_ultimo_hijo = (i == len(nodo.hijos) - 1)
                resultado.append(self.imprimir_arbol_visual(hijo, nuevo_prefijo, es_ultimo_hijo, False))
        
        return "\n".join(resultado)

    def imprimir_arbol(self, nodo: Nodo, nivel: int = 0) -> str:
        """Imprime el árbol de derivación decorado (formato original)"""
        resultado = []
        indentacion = "  " * nivel
        
        if nodo.tipo == "no_terminal":
            info = f"saldo={nodo.saldo}, valido={nodo.valido}, nivel={nodo.nivel}, refrescos={nodo.refrescos_comprados}"
            resultado.append(f"{indentacion}{nodo.simbolo} ({info})")
            if nodo.errores:
                for error in nodo.errores:
                    resultado.append(f"{indentacion}  ERROR: {error}")
        else:
            resultado.append(f"{indentacion}{nodo.simbolo}")
        
        for hijo in nodo.hijos:
            resultado.append(self.imprimir_arbol(hijo, nivel + 1))
        
        return "\n".join(resultado)

class InterfazGrafica:
    """Interfaz gráfica para el analizador semántico"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Analizador Semántico - Máquina Expendedora")
        self.root.geometry("1000x800")
        
        self.analizador = AnalizadorSemantico()
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Entrada de cadena
        ttk.Label(main_frame, text="Cadena de entrada:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entry_cadena = ttk.Entry(main_frame, width=50, font=('Courier', 12))
        self.entry_cadena.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Analizar", command=self.analizar).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cargar Ejemplos", command=self.cargar_ejemplos).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Limpiar", command=self.limpiar).pack(side=tk.LEFT, padx=5)
        
        # Resultado
        ttk.Label(main_frame, text="Resultado del análisis:").grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        self.label_resultado = ttk.Label(main_frame, text="", font=('Arial', 12, 'bold'))
        self.label_resultado.grid(row=2, column=1, sticky=tk.W, pady=(10, 5), padx=(10, 0))
        
        # Selector de formato de árbol
        format_frame = ttk.Frame(main_frame)
        format_frame.grid(row=3, column=0, columnspan=2, pady=5)
        
        ttk.Label(format_frame, text="Formato del árbol:").pack(side=tk.LEFT, padx=5)
        self.formato_var = tk.StringVar(value="visual")
        ttk.Radiobutton(format_frame, text="Visual (como imagen)", variable=self.formato_var, 
                       value="visual", command=self.cambiar_formato).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(format_frame, text="Indentado (original)", variable=self.formato_var, 
                       value="original", command=self.cambiar_formato).pack(side=tk.LEFT, padx=5)
        
        # Área de texto para mostrar el árbol
        self.text_area = scrolledtext.ScrolledText(main_frame, width=90, height=35, font=('Courier', 9))
        self.text_area.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Ejemplos predefinidos
        self.ejemplos = [
            ("{ $ $ $ R }", "Válido - 3 monedas, 1 refresco"),
            ("{ $ { $ $ $ R } < }", "Válido - Bloque anidado"),
            ("{ $ $ $ $ $ $ $ $ $ R R R }", "Válido - 9 monedas, 3 refrescos"),
            ("{ $ R }", "Inválido - Saldo insuficiente"),
            ("{ $ { $ $ R } < }", "Inválido - Saldo insuficiente en bloque anidado"),
            ("{ { { { $ $ $ R } } } }", "Inválido - Excede niveles de anidación"),
            ("{ < }", "Inválido - No hay monedas para devolver"),
            ("{ $ $ $ $ R R R R }", "Inválido - Excede máximo de refrescos"),
        ]
        
        # Variable para almacenar el último análisis
        self.ultimo_arbol = None
        
    def cambiar_formato(self):
        """Cambia el formato de visualización del árbol"""
        if hasattr(self, 'ultimo_arbol') and self.ultimo_arbol:
            self.mostrar_arbol()
    
    def mostrar_arbol(self):
        """Muestra el árbol en el formato seleccionado"""
        if not self.ultimo_arbol:
            return
            
        formato = self.formato_var.get()
        
        if formato == "visual":
            arbol_texto = self.analizador.imprimir_arbol_visual(self.ultimo_arbol)
        else:
            arbol_texto = self.analizador.imprimir_arbol(self.ultimo_arbol)
        
        # Encontrar la posición del árbol en el texto actual
        contenido_actual = self.text_area.get(1.0, tk.END)
        lineas = contenido_actual.split('\n')
        
        # Buscar donde comienza el árbol
        inicio_arbol = -1
        for i, linea in enumerate(lineas):
            if "ÁRBOL DE DERIVACIÓN DECORADO:" in linea:
                inicio_arbol = i + 2  # Saltar la línea de guiones
                break
        
        if inicio_arbol != -1:
            # Reemplazar solo la parte del árbol
            nuevas_lineas = lineas[:inicio_arbol] + [arbol_texto] + lineas[inicio_arbol:]
            
            # Buscar donde termina el árbol (próxima sección)
            fin_arbol = -1
            for i in range(inicio_arbol + 1, len(nuevas_lineas)):
                if nuevas_lineas[i].strip() and (nuevas_lineas[i].startswith("ERRORES") or nuevas_lineas[i].startswith("✓") or nuevas_lineas[i].startswith("=")):
                    fin_arbol = i
                    break
            
            if fin_arbol != -1:
                # Reconstruir el texto manteniendo solo el nuevo árbol
                resultado_final = nuevas_lineas[:inicio_arbol] + [arbol_texto] + ["\n"] + nuevas_lineas[fin_arbol:]
            else:
                resultado_final = nuevas_lineas[:inicio_arbol] + [arbol_texto]
            
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, "\n".join(resultado_final))
        
    def analizar(self):
        """Analiza la cadena ingresada"""
        cadena = self.entry_cadena.get().strip()
        
        if not cadena:
            messagebox.showwarning("Advertencia", "Por favor ingrese una cadena")
            return
            
        try:
            arbol, es_valida = self.analizador.analizar_cadena(cadena)
            self.ultimo_arbol = arbol
            
            # Mostrar resultado
            if es_valida:
                self.label_resultado.config(text="✓ CADENA VÁLIDA", foreground="green")
            else:
                self.label_resultado.config(text="✗ CADENA INVÁLIDA", foreground="red")
            
            # Mostrar árbol y análisis
            self.text_area.delete(1.0, tk.END)
            
            if arbol:
                resultado_texto = f"ANÁLISIS SEMÁNTICO DE: {cadena}\n"
                resultado_texto += "=" * 60 + "\n\n"
                resultado_texto += "ÁRBOL DE DERIVACIÓN DECORADO:\n"
                resultado_texto += "-" * 35 + "\n"
                
                # Usar el formato seleccionado
                formato = self.formato_var.get()
                if formato == "visual":
                    resultado_texto += self.analizador.imprimir_arbol_visual(arbol)
                else:
                    resultado_texto += self.analizador.imprimir_arbol(arbol)
                
                resultado_texto += "\n\n"
                
                if self.analizador.errores_globales:
                    resultado_texto += "ERRORES ENCONTRADOS:\n"
                    resultado_texto += "-" * 20 + "\n"
                    for i, error in enumerate(self.analizador.errores_globales, 1):
                        resultado_texto += f"{i}. {error}\n"
                else:
                    resultado_texto += "✓ No se encontraron errores semánticos\n"
                    
                resultado_texto += "\n" + "=" * 60 + "\n"
                
                if es_valida:
                    resultado_texto += f"RESULTADO: La cadena '{cadena}' es SEMÁNTICAMENTE VÁLIDA\n"
                else:
                    resultado_texto += f"RESULTADO: La cadena '{cadena}' es SEMÁNTICAMENTE INVÁLIDA\n"
                    
            else:
                resultado_texto = "ERROR: No se pudo construir el árbol de derivación\n"
                for error in self.analizador.errores_globales:
                    resultado_texto += f"- {error}\n"
            
            self.text_area.insert(tk.END, resultado_texto)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error durante el análisis: {str(e)}")
    
    def cargar_ejemplos(self):
        """Muestra ventana con ejemplos predefinidos"""
        ventana_ejemplos = tk.Toplevel(self.root)
        ventana_ejemplos.title("Ejemplos Predefinidos")
        ventana_ejemplos.geometry("600x400")
        
        ttk.Label(ventana_ejemplos, text="Seleccione un ejemplo:", font=('Arial', 12, 'bold')).pack(pady=10)
        
        frame_ejemplos = ttk.Frame(ventana_ejemplos)
        frame_ejemplos.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for i, (cadena, descripcion) in enumerate(self.ejemplos):
            frame_ejemplo = ttk.Frame(frame_ejemplos)
            frame_ejemplo.pack(fill=tk.X, pady=2)
            
            btn = ttk.Button(frame_ejemplo, text=f"Usar ejemplo {i+1}", 
                           command=lambda c=cadena: self.usar_ejemplo(c, ventana_ejemplos))
            btn.pack(side=tk.LEFT, padx=5)
            
            ttk.Label(frame_ejemplo, text=f"{cadena} - {descripcion}", 
                     font=('Courier', 10)).pack(side=tk.LEFT, padx=10)
    
    def usar_ejemplo(self, cadena, ventana):
        """Usa un ejemplo seleccionado"""
        self.entry_cadena.delete(0, tk.END)
        self.entry_cadena.insert(0, cadena)
        ventana.destroy()
        self.analizar()
    
    def limpiar(self):
        """Limpia la interfaz"""
        self.entry_cadena.delete(0, tk.END)
        self.text_area.delete(1.0, tk.END)
        self.label_resultado.config(text="")
        self.ultimo_arbol = None
    
    def ejecutar(self):
        """Ejecuta la interfaz gráfica"""
        self.root.mainloop()

def main():
    """Función principal"""
    print("=== ANALIZADOR SEMÁNTICO - MÁQUINA EXPENDEDORA ===")
    print("1. Interfaz Gráfica")
    print("2. Consola")
    print("3. Archivo de texto")
    
    opcion = input("\nSeleccione una opción (1-3): ").strip()
    
    if opcion == "1":
        # Interfaz gráfica
        app = InterfazGrafica()
        app.ejecutar()
        
    elif opcion == "2":
        # Modo consola
        analizador = AnalizadorSemantico()
        
        print("\nOpciones de visualización:")
        print("1. Formato visual (como árbol)")
        print("2. Formato indentado (original)")
        formato_opcion = input("Seleccione formato (1-2): ").strip()
        usar_formato_visual = formato_opcion == "1"
        
        while True:
            print("\n" + "="*60)
            cadena = input("Ingrese una cadena (o 'salir' para terminar): ").strip()
            
            if cadena.lower() == 'salir':
                break
                
            if not cadena:
                continue
                
            try:
                arbol, es_valida = analizador.analizar_cadena(cadena)
                
                print(f"\nAnálisis de: {cadena}")
                print("-" * 35)
                
                if arbol:
                    print("\nÁrbol de derivación decorado:")
                    if usar_formato_visual:
                        print(analizador.imprimir_arbol_visual(arbol))
                    else:
                        print(analizador.imprimir_arbol(arbol))
                    
                    if analizador.errores_globales:
                        print("\nErrores encontrados:")
                        for i, error in enumerate(analizador.errores_globales, 1):
                            print(f"{i}. {error}")
                    
                    print(f"\nResultado: {'VÁLIDA' if es_valida else 'INVÁLIDA'}")
                else:
                    print("Error: No se pudo construir el árbol")
                    for error in analizador.errores_globales:
                        print(f"- {error}")
                        
            except Exception as e:
                print(f"Error durante el análisis: {e}")
                
    elif opcion == "3":
        # Archivo de texto
        nombre_archivo = input("Ingrese el nombre del archivo: ").strip()
        
        print("Opciones de visualización:")
        print("1. Formato visual (como árbol)")
        print("2. Formato indentado (original)")
        formato_opcion = input("Seleccione formato (1-2): ").strip()
        usar_formato_visual = formato_opcion == "1"
        
        try:
            with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
                cadenas = [linea.strip() for linea in archivo if linea.strip()]
                
            analizador = AnalizadorSemantico()
            
            # Crear archivo de salida
            nombre_salida = nombre_archivo.replace('.txt', '_resultado.txt')
            
            with open(nombre_salida, 'w', encoding='utf-8') as salida:
                salida.write("=== ANÁLISIS SEMÁNTICO - MÁQUINA EXPENDEDORA ===\n")
                salida.write(f"Formato: {'Visual' if usar_formato_visual else 'Indentado'}\n\n")
                
                for i, cadena in enumerate(cadenas, 1):
                    salida.write(f"CADENA {i}: {cadena}\n")
                    salida.write("="*60 + "\n")
                    
                    try:
                        arbol, es_valida = analizador.analizar_cadena(cadena)
                        
                        if arbol:
                            salida.write("ÁRBOL DE DERIVACIÓN DECORADO:\n")
                            salida.write("-" * 35 + "\n")
                            
                            if usar_formato_visual:
                                salida.write(analizador.imprimir_arbol_visual(arbol))
                            else:
                                salida.write(analizador.imprimir_arbol(arbol))
                            
                            salida.write("\n\n")
                            
                            if analizador.errores_globales:
                                salida.write("ERRORES ENCONTRADOS:\n")
                                salida.write("-" * 20 + "\n")
                                for j, error in enumerate(analizador.errores_globales, 1):
                                    salida.write(f"{j}. {error}\n")
                                salida.write("\n")
                            
                            salida.write(f"RESULTADO: {'VÁLIDA' if es_valida else 'INVÁLIDA'}\n")
                        else:
                            salida.write("ERROR: No se pudo construir el árbol\n")
                            for error in analizador.errores_globales:
                                salida.write(f"- {error}\n")
                                
                    except Exception as e:
                        salida.write(f"ERROR: {e}\n")
                        
                    salida.write("\n" + "="*60 + "\n\n")
                    
            print(f"Análisis completado. Resultados guardados en: {nombre_salida}")
            
        except FileNotFoundError:
            print(f"Error: No se pudo encontrar el archivo '{nombre_archivo}'")
        except Exception as e:
            print(f"Error al procesar el archivo: {e}")
    
    else:
        print("Opción no válida")

if __name__ == "__main__":
    main()