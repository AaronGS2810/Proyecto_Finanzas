import yfinance as yf
import pandas as pd
from time import sleep
from datetime import datetime, timedelta
import os
import numpy as np

# 📅 Calcular fecha de hace 5 días laborales
def get_fecha_laboral_retrasada(dias_laborales=5):
    fecha = datetime.today()
    dias_contados = 0

    while dias_contados < dias_laborales:
        fecha -= timedelta(days=1)
        if fecha.weekday() < 5:  # 0=lunes, 6=domingo
            dias_contados += 1

    return fecha.strftime("%Y-%m-%d")

# 📄 Cargar CSV desde la carpeta data
def cargar_tickers_csv(fecha_objetivo):
    ruta = f"data/tickers_{fecha_objetivo}.csv"
    if not os.path.exists(ruta):
        print(f"❌ No se encontró el archivo: {ruta}")
        return []
    
    df = pd.read_csv(ruta)
    return df.iloc[:, 0].tolist()

# 📊 Analizar ingresos
def analizar_ingresos(tickers):
    resultados = []

    for i, symbol in enumerate(tickers):
        print(f"🔍 Analizando {symbol} ({i+1}/{len(tickers)})")
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            nombre = info.get("longName", symbol)

            df = ticker.quarterly_financials
            if df.empty or "Total Revenue" not in df.index:
                continue

            ingresos = df.loc["Total Revenue"].tolist()
            fechas = df.columns.tolist()

            if len(ingresos) >= 2 and ingresos[1] != 0:
                actual = ingresos[0]
                if actual//1_000_000_000 >= 1:
                    actual_str = round(actual / 1_000_000_000, 2)
                    actual_str = str(actual_str) + "B"
                elif actual//1_000_000 >= 1:
                    actual_str = round(actual / 1_000_000, 2)
                    actual_str = str(actual_str) + "M"
                else:
                    actual_str = str(actual)
                anterior = ingresos[1]
                if anterior//1_000_000_000 >= 1:
                    anterior_str = round(anterior / 1_000_000_000, 2)
                    anterior_str = str(anterior_str) + "B"
                elif anterior//1_000_000 >= 1:
                    anterior_str = round(anterior / 1_000_000, 2)
                    anterior_str = str(anterior_str) + "M"
                else:
                    anterior_str = str(anterior)
                crecimiento = ((actual - anterior) / anterior) * 100

                fecha_actual = fechas[0].strftime("%Y-%m-%d") if hasattr(fechas[0], "strftime") else str(fechas[0])
                fecha_anterior = fechas[1].strftime("%Y-%m-%d") if hasattr(fechas[1], "strftime") else str(fechas[1])

                resultados.append({
                    "Ticker": symbol,
                    "Empresa": nombre,
                    "Fecha Resultado Actual": fecha_actual,
                    "Fecha Resultado Anterior": fecha_anterior,
                    "Ingresos Actual": actual_str,
                    "Ingresos Anterior": anterior_str,
                    "Crecimiento %": round(crecimiento, 2)
                })
                
                def guardar_historico_empresa(ticker, nombre):
                    try:
                        t = yf.Ticker(ticker)
                        financials = t.quarterly_financials
                        balance = t.quarterly_balance_sheet
                        cashflow = t.quarterly_cashflow
                        info = t.info

                        fechas = financials.columns.tolist()[:8]

                        data = {
                            "Fecha": [],
                            "Ingresos": [],
                            "Net Income": [],
                            "EBITDA": [],
                            "Free Cash Flow": [],
                            "PER": []
                        }

                        for fecha in fechas:
                            data["Fecha"].append(fecha.strftime("%Y-%m-%d") if hasattr(fecha, "strftime") else str(fecha))

                            data["Ingresos"].append(financials.loc["Total Revenue", fecha] if "Total Revenue" in financials.index else None)
                            data["Net Income"].append(financials.loc["Net Income", fecha] if "Net Income" in financials.index else None)
                            data["EBITDA"].append(financials.loc["EBITDA", fecha] if "EBITDA" in financials.index else None)
                            data["Free Cash Flow"].append(cashflow.loc["Total Cash From Operating Activities", fecha] if "Total Cash From Operating Activities" in cashflow.index else None)

                            # Estimar PER si es posible
                            try:
                                eps = financials.loc["Diluted EPS", fecha]
                                price = info.get("previousClose", None)
                                per = (price / eps) if eps and eps != 0 else None
                            except:
                                per = None

                            data["PER"].append(per)

                        os.makedirs("empresa_data", exist_ok=True)
                        ruta = f"empresa_data/{ticker}.csv"
                        pd.DataFrame(data).to_csv(ruta, index=False)
                        print(f"📁 Datos históricos guardados: {ruta}")

                    except Exception as e:
                        print(f"⚠️ No se pudo guardar histórico para {ticker}: {e}")

                guardar_historico_empresa(symbol, nombre)

            
            sleep(0.5)

        except Exception as e:
            print(f"❌ Error con {symbol}: {e}")
            continue

    return resultados




# 🧠 Script principal
def main():
    fecha_objetivo = get_fecha_laboral_retrasada(5)
    print(f"📁 Buscando tickers del: {fecha_objetivo}")

    tickers = cargar_tickers_csv(fecha_objetivo)
    if not tickers:
        print("⚠️ No se encontraron tickers para esa fecha.")
        return

    resultados = analizar_ingresos(tickers)
    df = pd.DataFrame(resultados)
    df = df.sort_values(by="Crecimiento %", ascending=False)

    # Guardar en carpeta analisis
    os.makedirs("analisis", exist_ok=True)
    salida = f"analisis/crecimiento_{fecha_objetivo}.csv"
    df.to_csv(salida, index=False)

    print(f"✅ Resultados guardados en {salida}")
    print(df.head(10))

if __name__ == "__main__":
    main()
