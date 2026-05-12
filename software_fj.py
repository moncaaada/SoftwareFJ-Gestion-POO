"""
Software FJ - Sistema Integral de Gestión de Clientes, Servicios y Reservas
Curso: Programación (213023_457) - UNAD
Estudiante: Jhon Sebastián Moncada Martínez
"""

import logging
import uuid
from abc import ABC, abstractmethod
from datetime import datetime

# ─────────────────────────────────────────────────────────────
# 1. SISTEMA DE LOGS
# ─────────────────────────────────────────────────────────────

# Configuramos el logger para que escriba en logs.txt con timestamp
logging.basicConfig(
    filename="logs.txt",
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8"
)
logger = logging.getLogger("SoftwareFJ")


# ─────────────────────────────────────────────────────────────
# 2. JERARQUÍA DE EXCEPCIONES PERSONALIZADAS
# ─────────────────────────────────────────────────────────────

class ErrorSoftwareFJ(Exception):
    """Excepción base de la aplicación. Toda excepción interna hereda de aquí."""
    pass


class ErrorValidacionDatos(ErrorSoftwareFJ):
    """Se lanza cuando un dato de entrada no pasa las validaciones del sistema."""
    pass


class ErrorReservaEmpresa(ErrorSoftwareFJ):
    """Se lanza cuando una operación de reserva no puede completarse."""
    pass


# ─────────────────────────────────────────────────────────────
# 3. CLASE ABSTRACTA EntidadBase
# ─────────────────────────────────────────────────────────────

class EntidadBase(ABC):
    """
    Clase abstracta que representa cualquier entidad registrable en el sistema.
    Garantiza que todo objeto tenga un identificador único y fecha de registro.
    """

    def __init__(self):
        self._identificador = str(uuid.uuid4())[:8].upper()
        self._fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @property
    def identificador(self):
        return self._identificador

    @property
    def fecha_registro(self):
        return self._fecha_registro

    @abstractmethod
    def obtener_resumen_tecnico(self) -> str:
        """Cada entidad debe poder describirse a sí misma."""
        pass

    def __str__(self):
        return self.obtener_resumen_tecnico()


# ─────────────────────────────────────────────────────────────
# 4. CLASE CLIENTE
# ─────────────────────────────────────────────────────────────

class Cliente(EntidadBase):
    """
    Representa a un cliente de Software FJ.
    Encapsula sus datos personales con validaciones estrictas.
    Si algún dato es inválido se lanza ErrorValidacionDatos y se registra en el log.
    """

    def __init__(self, nombre: str, cedula: str, correo: str):
        super().__init__()
        # Primero validamos antes de asignar nada
        self._validar_cedula(cedula)
        self._validar_correo(correo)
        self._nombre = nombre.strip()
        self._cedula = cedula.strip()
        self._correo = correo.strip()
        logger.info(f"Cliente registrado: {self._nombre} | Cédula: {self._cedula}")

    # ── Validaciones internas ──────────────────────────────────

    def _validar_cedula(self, cedula: str):
        if not cedula or not cedula.strip().isdigit():
            msg = f"Cédula inválida: '{cedula}'. Solo se permiten dígitos."
            logger.error(msg)
            raise ErrorValidacionDatos(msg)

    def _validar_correo(self, correo: str):
        if not correo or "@" not in correo or "." not in correo:
            msg = f"Correo inválido: '{correo}'. Debe contener '@' y '.'."
            logger.error(msg)
            raise ErrorValidacionDatos(msg)

    # ── Propiedades (encapsulamiento) ──────────────────────────

    @property
    def nombre(self):
        return self._nombre

    @property
    def cedula(self):
        return self._cedula

    @property
    def correo(self):
        return self._correo

    def obtener_resumen_tecnico(self) -> str:
        return (
            f"[CLIENTE #{self.identificador}] {self._nombre} | "
            f"CC: {self._cedula} | Email: {self._correo} | "
            f"Registrado: {self.fecha_registro}"
        )


# ─────────────────────────────────────────────────────────────
# 5. JERARQUÍA DE SERVICIOS
# ─────────────────────────────────────────────────────────────

class Servicio(EntidadBase, ABC):
    """
    Clase abstracta base para todos los servicios de Software FJ.
    Cada servicio especializado define su propio costo y descripción.
    """

    def __init__(self, nombre: str, disponible: bool = True):
        super().__init__()
        if not nombre or not nombre.strip():
            msg = "El nombre del servicio no puede estar vacío."
            logger.error(msg)
            raise ErrorValidacionDatos(msg)
        self._nombre = nombre.strip()
        self._disponible = disponible

    @property
    def nombre(self):
        return self._nombre

    @property
    def disponible(self):
        return self._disponible

    @abstractmethod
    def calcular_costo_base(self) -> float:
        """Cada servicio calcula su costo de forma diferente."""
        pass

    @abstractmethod
    def describir_servicio(self) -> str:
        pass

    def obtener_resumen_tecnico(self) -> str:
        estado = "Disponible" if self._disponible else "No disponible"
        return (
            f"[SERVICIO #{self.identificador}] {self._nombre} | "
            f"Costo base: ${self.calcular_costo_base():,.0f} | {estado}"
        )


class ReservaSala(Servicio):
    """
    Reserva de sala de reuniones o trabajo.
    El costo depende del número de personas y si incluye proyector.
    """

    TARIFA_POR_PERSONA = 15_000  # pesos por persona

    def __init__(self, capacidad: int, con_proyector: bool = False):
        super().__init__(nombre="Reserva de Sala")
        if capacidad <= 0:
            msg = f"Capacidad de sala inválida: {capacidad}. Debe ser mayor a 0."
            logger.error(msg)
            raise ErrorValidacionDatos(msg)
        self._capacidad = capacidad
        self._con_proyector = con_proyector

    def calcular_costo_base(self) -> float:
        costo = self._capacidad * self.TARIFA_POR_PERSONA
        if self._con_proyector:
            costo += 20_000  # costo adicional por proyector
        return costo

    def describir_servicio(self) -> str:
        extra = " + proyector" if self._con_proyector else ""
        return f"Sala para {self._capacidad} personas{extra}"

    def obtener_resumen_tecnico(self) -> str:
        return super().obtener_resumen_tecnico() + f" | {self.describir_servicio()}"


class AlquilerEquipo(Servicio):
    """
    Alquiler de equipos tecnológicos (laptops, cámaras, etc.).
    El costo base varía según el tipo de equipo.
    """

    TARIFAS = {
        "laptop": 35_000,
        "camara": 50_000,
        "tablet": 25_000,
        "proyector": 30_000,
    }

    def __init__(self, tipo_equipo: str):
        super().__init__(nombre="Alquiler de Equipo")
        tipo = tipo_equipo.lower().strip()
        if tipo not in self.TARIFAS:
            msg = f"Tipo de equipo desconocido: '{tipo_equipo}'. Opciones: {list(self.TARIFAS.keys())}"
            logger.error(msg)
            raise ErrorValidacionDatos(msg)
        self._tipo_equipo = tipo

    def calcular_costo_base(self) -> float:
        return self.TARIFAS[self._tipo_equipo]

    def describir_servicio(self) -> str:
        return f"Alquiler de {self._tipo_equipo}"

    def obtener_resumen_tecnico(self) -> str:
        return super().obtener_resumen_tecnico() + f" | {self.describir_servicio()}"


class AsesoriaEspecializada(Servicio):
    """
    Asesoría profesional en áreas como software, redes o seguridad.
    Se cobra por hora de consultoría.
    """

    TARIFA_POR_HORA = 80_000

    def __init__(self, area: str, horas_estimadas: float):
        super().__init__(nombre="Asesoría Especializada")
        if horas_estimadas <= 0:
            msg = f"Horas de asesoría inválidas: {horas_estimadas}."
            logger.error(msg)
            raise ErrorValidacionDatos(msg)
        self._area = area.strip()
        self._horas = horas_estimadas

    def calcular_costo_base(self) -> float:
        return self._horas * self.TARIFA_POR_HORA

    def describir_servicio(self) -> str:
        return f"Asesoría en {self._area} ({self._horas}h)"

    def obtener_resumen_tecnico(self) -> str:
        return super().obtener_resumen_tecnico() + f" | {self.describir_servicio()}"


# ─────────────────────────────────────────────────────────────
# 6. CLASE RESERVA
# ─────────────────────────────────────────────────────────────

ESTADOS_VALIDOS = ("pendiente", "confirmada", "procesada", "cancelada")


class Reserva(EntidadBase):
    """
    Integra un Cliente con un Servicio durante una duración determinada.
    Maneja el ciclo de vida de la reserva: pendiente → confirmada → procesada / cancelada.
    """

    def __init__(self, cliente: Cliente, servicio: Servicio, duracion_horas: float):
        super().__init__()
        self._cliente = cliente
        self._servicio = servicio
        self._duracion = duracion_horas
        self._estado = "pendiente"
        logger.info(
            f"Reserva {self.identificador} creada | Cliente: {cliente.nombre} | "
            f"Servicio: {servicio.nombre} | Duración: {duracion_horas}h"
        )

    # ── Propiedades ────────────────────────────────────────────

    @property
    def estado(self):
        return self._estado

    @property
    def cliente(self):
        return self._cliente

    @property
    def servicio(self):
        return self._servicio

    # ── Métodos de ciclo de vida ───────────────────────────────

    def confirmar(self):
        """Pasa la reserva de pendiente a confirmada."""
        try:
            if self._estado != "pendiente":
                raise ErrorReservaEmpresa(
                    f"No se puede confirmar una reserva en estado '{self._estado}'."
                )
            if not self._servicio.disponible:
                raise ErrorReservaEmpresa(
                    f"El servicio '{self._servicio.nombre}' no está disponible."
                )
        except ErrorReservaEmpresa as e:
            logger.warning(f"Reserva {self.identificador} | Confirmar fallido: {e}")
            raise
        else:
            self._estado = "confirmada"
            logger.info(f"Reserva {self.identificador} confirmada.")
        finally:
            logger.debug(f"Reserva {self.identificador} | Estado actual: {self._estado}")

    def procesar(self):
        """Marca la reserva como procesada (ejecutada)."""
        try:
            if self._estado != "confirmada":
                raise ErrorReservaEmpresa(
                    f"Solo se pueden procesar reservas confirmadas. Estado actual: '{self._estado}'."
                )
        except ErrorReservaEmpresa as e:
            logger.warning(f"Reserva {self.identificador} | Procesar fallido: {e}")
            raise
        else:
            self._estado = "procesada"
            logger.info(f"Reserva {self.identificador} procesada exitosamente.")
        finally:
            logger.debug(f"Reserva {self.identificador} | Estado final: {self._estado}")

    def cancelar(self):
        """Cancela la reserva si aún no fue procesada."""
        try:
            if self._estado in ("procesada", "cancelada"):
                raise ErrorReservaEmpresa(
                    f"No se puede cancelar una reserva en estado '{self._estado}'."
                )
        except ErrorReservaEmpresa as e:
            logger.warning(f"Reserva {self.identificador} | Cancelar fallido: {e}")
            raise
        else:
            self._estado = "cancelada"
            logger.info(f"Reserva {self.identificador} cancelada.")
        finally:
            logger.debug(f"Reserva {self.identificador} | Estado actual: {self._estado}")

    # ── Cálculo de costos (sobrecarga emulada con parámetros opcionales) ──

    def calcular_total_con_descuento(
        self,
        descuento: float = 0.0,
        impuesto: float = 0.19,
        horas_extra: float = 0.0
    ) -> float:
        """
        Calcula el costo total de la reserva.

        Parámetros opcionales que emulan sobrecarga:
          - descuento  : porcentaje de descuento (0.0 a 1.0)
          - impuesto   : porcentaje de IVA (por defecto 19%)
          - horas_extra: horas adicionales que se suman a la duración

        Uso básico (sin argumentos)   → costo base × duración + IVA
        Con descuento                 → aplica descuento antes del IVA
        Con impuesto personalizado    → reemplaza el IVA estándar
        Con horas_extra               → añade tiempo adicional al cálculo
        """
        duracion_total = self._duracion + horas_extra
        costo_base = self._servicio.calcular_costo_base() * duracion_total
        costo_con_descuento = costo_base * (1 - descuento)
        total = costo_con_descuento * (1 + impuesto)
        return round(total, 2)

    def obtener_resumen_tecnico(self) -> str:
        total = self.calcular_total_con_descuento()
        return (
            f"[RESERVA #{self.identificador}] Estado: {self._estado.upper()} | "
            f"Cliente: {self._cliente.nombre} | Servicio: {self._servicio.nombre} | "
            f"Duración: {self._duracion}h | Total: ${total:,.0f}"
        )


# ─────────────────────────────────────────────────────────────
# 7. SIMULADOR DE 10 OPERACIONES
# ─────────────────────────────────────────────────────────────

def separador(titulo: str):
    """Imprime un separador visual para la consola."""
    print(f"\n{'─' * 60}")
    print(f"  {titulo}")
    print('─' * 60)


def ejecutar_simulacion():
    """
    Ejecuta 10 casos de prueba que cubren escenarios válidos e inválidos.
    El programa NUNCA se detiene; todos los errores se capturan y registran.
    """
    logger.info("=" * 60)
    logger.info("INICIO DE SIMULACIÓN - Software FJ")
    logger.info("=" * 60)
    print("\n" + "═" * 60)
    print("   SOFTWARE FJ - SIMULADOR DE OPERACIONES")
    print("═" * 60)

    # ── CASO 1: Cliente válido ─────────────────────────────────
    separador("CASO 1 | Registro de cliente válido")
    try:
        c1 = Cliente("Laura Gómez", "1098765432", "laura.gomez@email.com")
        print(f"✔ {c1.obtener_resumen_tecnico()}")
    except ErrorSoftwareFJ as e:
        print(f"✘ Error: {e}")

    # ── CASO 2: Cliente con cédula inválida ────────────────────
    separador("CASO 2 | Cliente con cédula inválida (letras en cédula)")
    try:
        c_mal = Cliente("Pedro Ruiz", "ABC123XYZ", "pedro@mail.com")
        print(f"✔ {c_mal}")
    except ErrorValidacionDatos as e:
        print(f"✘ ErrorValidacionDatos capturado correctamente: {e}")
    except ErrorSoftwareFJ as e:
        print(f"✘ ErrorSoftwareFJ: {e}")

    # ── CASO 3: Cliente con correo inválido ────────────────────
    separador("CASO 3 | Cliente con correo sin '@'")
    try:
        c_mal2 = Cliente("Ana Torres", "987654321", "correo-sin-arroba")
        print(f"✔ {c_mal2}")
    except ErrorValidacionDatos as e:
        print(f"✘ ErrorValidacionDatos capturado: {e}")

    # ── CASO 4: Servicio válido - Reserva de sala ──────────────
    separador("CASO 4 | Creación de servicio ReservaSala válido")
    sala_ok = None
    try:
        sala_ok = ReservaSala(capacidad=10, con_proyector=True)
        print(f"✔ {sala_ok.obtener_resumen_tecnico()}")
    except ErrorSoftwareFJ as e:
        print(f"✘ Error: {e}")

    # ── CASO 5: Reserva de sala con capacidad inválida ─────────
    separador("CASO 5 | ReservaSala con capacidad 0 (inválida)")
    try:
        sala_mala = ReservaSala(capacidad=0)
        print(f"✔ {sala_mala}")
    except ErrorValidacionDatos as e:
        print(f"✘ ErrorValidacionDatos capturado: {e}")

    # ── CASO 6: Reserva exitosa (pendiente → confirmada → procesada)
    separador("CASO 6 | Flujo completo de reserva exitosa")
    try:
        c2 = Cliente("Carlos Medina", "1122334455", "c.medina@empresa.co")
        servicio_asesoria = AsesoriaEspecializada("Ciberseguridad", horas_estimadas=3)
        reserva1 = Reserva(c2, servicio_asesoria, duracion_horas=3)
        reserva1.confirmar()
        reserva1.procesar()
        total = reserva1.calcular_total_con_descuento(descuento=0.10, impuesto=0.19)
        print(f"✔ {reserva1.obtener_resumen_tecnico()}")
        print(f"  └─ Total con 10% descuento + IVA 19%: ${total:,.0f}")
    except ErrorSoftwareFJ as e:
        print(f"✘ Error: {e}")

    # ── CASO 7: Intentar cancelar una reserva ya procesada ─────
    separador("CASO 7 | Cancelar reserva ya procesada (debe fallar)")
    try:
        # Reutilizamos reserva1 del caso 6 que ya fue procesada
        reserva1.cancelar()
        print("✔ Cancelada (esto no debería imprimirse)")
    except ErrorReservaEmpresa as e:
        print(f"✘ ErrorReservaEmpresa capturado correctamente: {e}")
    except NameError:
        print("✘ La reserva del caso 6 no se creó por error previo.")

    # ── CASO 8: AlquilerEquipo con tipo desconocido ────────────
    separador("CASO 8 | AlquilerEquipo con tipo de equipo inválido")
    try:
        equipo_raro = AlquilerEquipo("dron")
        print(f"✔ {equipo_raro}")
    except ErrorValidacionDatos as e:
        print(f"✘ ErrorValidacionDatos capturado: {e}")

    # ── CASO 9: Reserva con encadenamiento de excepciones ──────
    separador("CASO 9 | Encadenamiento de excepciones (raise ... from ...)")
    try:
        try:
            # Simulamos que recibimos datos externos con error
            datos_externos = {"cedula": "NO_VALIDA", "correo": "x@x.com"}
            if not datos_externos["cedula"].isdigit():
                raise ValueError("Datos del formulario externo corruptos.")
        except ValueError as ve:
            # Encadenamos: el origen fue un ValueError externo
            raise ErrorValidacionDatos(
                "Error al procesar datos del cliente desde fuente externa."
            ) from ve
    except ErrorValidacionDatos as e:
        causa = type(e.__cause__).__name__ if e.__cause__ else "N/A"
        print(f"✘ ErrorValidacionDatos capturado | Causa original: {causa}: {e.__cause__}")
        logger.error(f"Excepción encadenada: {e} | Causa: {e.__cause__}")

    # ── CASO 10: Cálculo de total con múltiples variantes ──────
    separador("CASO 10 | Polimorfismo en cálculo de costo + variantes")
    try:
        c3 = Cliente("María Ospina", "5544332211", "maria.ospina@unad.edu.co")
        laptop = AlquilerEquipo("laptop")
        reserva2 = Reserva(c3, laptop, duracion_horas=2)
        reserva2.confirmar()

        # Variante 1: sin descuento, IVA estándar
        t1 = reserva2.calcular_total_con_descuento()
        # Variante 2: con 15% de descuento
        t2 = reserva2.calcular_total_con_descuento(descuento=0.15)
        # Variante 3: con horas extra y sin IVA
        t3 = reserva2.calcular_total_con_descuento(impuesto=0.0, horas_extra=1.0)

        print(f"✔ {reserva2.obtener_resumen_tecnico()}")
        print(f"  ├─ Sin descuento + IVA 19%:          ${t1:,.0f}")
        print(f"  ├─ Con 15% descuento + IVA 19%:      ${t2:,.0f}")
        print(f"  └─ Sin IVA + 1h extra:               ${t3:,.0f}")
    except ErrorSoftwareFJ as e:
        print(f"✘ Error: {e}")

    # ── Resumen final ──────────────────────────────────────────
    print("\n" + "═" * 60)
    print("   SIMULACIÓN COMPLETADA - Revisa logs.txt para detalles")
    print("═" * 60)
    logger.info("FIN DE SIMULACIÓN - Software FJ")


# Punto de entrada
if __name__ == "__main__":
    ejecutar_simulacion()
