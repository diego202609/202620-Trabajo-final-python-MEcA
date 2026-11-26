"""Pruebas automáticas offline del módulo src/indicadores.py."""

from __future__ import annotations

import pandas as pd
import pytest

from src.config import PRUEBAS_DIR
from src.indicadores import (
    asignar_franja_cuantia,
    calcular_concentracion_proveedores,
    clasificar_categoria_hhi,
    ejecutar_calculo_indicadores,
)


def test_clasificar_categoria_hhi_estandar_doj() -> None:
    assert clasificar_categoria_hhi(800) == "Baja (< 1.500)"
    assert clasificar_categoria_hhi(1500) == "Moderada (1.500–2.500)"
    assert clasificar_categoria_hhi(2500) == "Moderada (1.500–2.500)"
    assert clasificar_categoria_hhi(2501) == "Alta (> 2.500)"


def test_asignar_franja_cuantia_separa_cero_simbolica_y_reales() -> None:
    assert asignar_franja_cuantia(0.0)[0] == 1
    assert asignar_franja_cuantia(0.01)[0] == 2
    assert asignar_franja_cuantia(2.0)[0] == 2
    assert asignar_franja_cuantia(1_000.0)[0] == 2
    assert asignar_franja_cuantia(51_600.0)[0] == 3
    assert asignar_franja_cuantia(5_000_000.0)[0] == 4
    assert asignar_franja_cuantia(45_000_000.0)[0] == 5
    assert asignar_franja_cuantia(250_000_000.0)[0] == 6
    assert asignar_franja_cuantia(5_000_000_000.0)[0] == 7


def test_calcular_concentracion_proveedores_monopolio_e_igualdad() -> None:
    df_prueba = pd.DataFrame(
        [
            # Monopolio: 1 solo proveedor = HHI 10.000, CR1 = 100%
            {
                "id_contrato": "C1",
                "codigo_entidad": "1",
                "sigla_entidad": "ENT1",
                "nombre_entidad_corto": "Entidad 1",
                "anio": 2024,
                "id_proveedor_limpio": "P1",
                "nombre_proveedor_limpio": "PROV UNO",
                "valor_del_contrato": 100_000_000.0,
                "es_contrato_valido_con_cuantia": True,
            },
            # 2 proveedores iguales (50% y 50%): HHI = 5.000
            {
                "id_contrato": "C2",
                "codigo_entidad": "2",
                "sigla_entidad": "ENT2",
                "nombre_entidad_corto": "Entidad 2",
                "anio": 2024,
                "id_proveedor_limpio": "PA",
                "nombre_proveedor_limpio": "PROV A",
                "valor_del_contrato": 50_000_000.0,
                "es_contrato_valido_con_cuantia": True,
            },
            {
                "id_contrato": "C3",
                "codigo_entidad": "2",
                "sigla_entidad": "ENT2",
                "nombre_entidad_corto": "Entidad 2",
                "anio": 2024,
                "id_proveedor_limpio": "PB",
                "nombre_proveedor_limpio": "PROV B",
                "valor_del_contrato": 50_000_000.0,
                "es_contrato_valido_con_cuantia": True,
            },
        ]
    )
    conc = calcular_concentracion_proveedores(df_prueba)
    fila_1 = conc[conc["sigla_entidad"] == "ENT1"].iloc[0]
    fila_2 = conc[conc["sigla_entidad"] == "ENT2"].iloc[0]

    assert fila_1["hhi_proveedores"] == pytest.approx(10_000.0)
    assert fila_1["cr1_pct"] == pytest.approx(100.0)
    assert fila_2["hhi_proveedores"] == pytest.approx(5_000.0)
    assert fila_2["cr5_pct"] == pytest.approx(100.0)


def test_ejecutar_calculo_indicadores_en_directorio_pruebas() -> None:
    salida_pruebas = PRUEBAS_DIR / "dashboard_data_test"
    tablas = ejecutar_calculo_indicadores(directorio_salida=salida_pruebas)

    assert len(tablas["resumen_anual"]) >= 12
    assert (salida_pruebas / "resumen_entidad_anio.csv").exists()
    assert (salida_pruebas / "distribucion_franjas_cuantia.csv").exists()
    assert (salida_pruebas / "README.md").exists()

    # Verificar que la suma de porcentajes de contratos por franja en 'TODAS' es ~100%
    todas = tablas["franjas_cuantia"][tablas["franjas_cuantia"]["sigla_entidad"] == "TODAS"]
    assert len(todas) == 7
    assert todas["pct_contratos"].sum() == pytest.approx(100.0, abs=0.1)
