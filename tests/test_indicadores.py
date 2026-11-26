"""Pruebas automáticas offline del módulo src/indicadores.py."""

from __future__ import annotations

import pandas as pd
import pytest

from src.config import FACTOR_DEFLACTOR_IPC_2025, PRUEBAS_DIR
from src.indicadores import (
    asignar_franja_cuantia,
    calcular_concentracion_proveedores,
    calcular_indice_duncan_unspsc,
    clasificar_categoria_hhi,
    construir_registro_ia_rubro5,
    ejecutar_calculo_indicadores,
)
from src.visualizacion import (
    graficar_rubro5_antes_despues_ipc,
    graficar_rubro5_ejecucion_vs_duncan,
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


def test_calcular_indice_duncan_unspsc_extremos_y_reasignacion_parcial() -> None:
    df_seg = pd.DataFrame(
        [
            # Caso 1 (IGUAL): composición idéntica (70% / 30%) aunque distinto nivel -> D = 0
            {
                "codigo_entidad": "10",
                "sigla_entidad": "IGUAL",
                "anio": 2024,
                "codigo_segmento": "80",
                "nombre_segmento": "Servicios de Gestión",
                "valor_paa_vigencia": 70.0,
                "valor_ejecutado": 140.0,
            },
            {
                "codigo_entidad": "10",
                "sigla_entidad": "IGUAL",
                "anio": 2024,
                "codigo_segmento": "43",
                "nombre_segmento": "TI y Telecomunicaciones",
                "valor_paa_vigencia": 30.0,
                "valor_ejecutado": 60.0,
            },
            # Caso 2 (DISJUNTO): 100% planeado en seg 80, 100% ejecutado en seg 43 -> D = 1.0 (100%)
            {
                "codigo_entidad": "20",
                "sigla_entidad": "DISJUNTO",
                "anio": 2024,
                "codigo_segmento": "80",
                "nombre_segmento": "Servicios de Gestión",
                "valor_paa_vigencia": 100.0,
                "valor_ejecutado": 0.0,
            },
            {
                "codigo_entidad": "20",
                "sigla_entidad": "DISJUNTO",
                "anio": 2024,
                "codigo_segmento": "43",
                "nombre_segmento": "TI y Telecomunicaciones",
                "valor_paa_vigencia": 0.0,
                "valor_ejecutado": 100.0,
            },
        ]
    )
    duncan = calcular_indice_duncan_unspsc(df_seg)
    d_igual = duncan[duncan["sigla_entidad"] == "IGUAL"].iloc[0]
    d_disj = duncan[duncan["sigla_entidad"] == "DISJUNTO"].iloc[0]

    assert d_igual["indice_duncan"] == pytest.approx(0.0)
    assert d_igual["duncan_pct"] == pytest.approx(0.0)
    assert d_disj["indice_duncan"] == pytest.approx(1.0)
    assert d_disj["duncan_pct"] == pytest.approx(100.0)


def test_registro_ia_rubro5_contiene_prompt_y_respuesta_integra() -> None:
    reg = construir_registro_ia_rubro5()
    assert "Actúa como un economista experto" in reg["prompt_enviado"]
    assert "### 1. Deflactación Intertemporal" in reg["respuesta_ia_completa"]
    assert "### 4. Emparejamiento Micro Bloqueado" in reg["respuesta_ia_completa"]
    assert len(reg["mejoras_implementadas"]) == 2
    assert len(reg["mejoras_descartadas"]) == 2


def test_ejecutar_calculo_indicadores_en_directorio_pruebas() -> None:
    salida_pruebas = PRUEBAS_DIR / "dashboard_data_test"
    tablas = ejecutar_calculo_indicadores(directorio_salida=salida_pruebas)

    assert len(tablas["resumen_anual"]) == 24
    assert (salida_pruebas / "resumen_entidad_anio.csv").exists()
    assert (salida_pruebas / "distribucion_franjas_cuantia.csv").exists()
    assert (salida_pruebas / "rubro5_antes_despues.csv").exists()
    assert (salida_pruebas / "rubro5_registro_ia.json").exists()
    assert (salida_pruebas / "README.md").exists()

    # Verificar deflactación IPC 2025 e invarianza de tasa intra-anual
    res = tablas["resumen_anual"]
    fila_2022 = res[res["anio"] == 2022].iloc[0]
    fila_2025 = res[res["anio"] == 2025].iloc[0]
    assert fila_2022["factor_ipc_2025"] == pytest.approx(FACTOR_DEFLACTOR_IPC_2025[2022])
    assert fila_2025["factor_ipc_2025"] == pytest.approx(1.0)
    assert res["duncan_pct"].between(0.0, 100.0).all()

    # Verificar tabla comparativa Antes vs. Después (6 entidades + TOTAL_MUESTRA = 7 filas)
    r5 = tablas["rubro5_antes_despues"]
    assert len(r5) == 7
    fig_ipc = graficar_rubro5_antes_despues_ipc(r5)
    fig_duncan = graficar_rubro5_ejecucion_vs_duncan(res)
    assert len(fig_ipc.data) == 4
    assert len(fig_duncan.data) == 6

    # Verificar que la suma de porcentajes de contratos por franja en 'TODAS' es ~100%
    todas = tablas["franjas_cuantia"][tablas["franjas_cuantia"]["sigla_entidad"] == "TODAS"]
    assert len(todas) == 7
    assert todas["pct_contratos"].sum() == pytest.approx(100.0, abs=0.1)
