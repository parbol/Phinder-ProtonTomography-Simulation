# Phinder – Simulación de Tomografía de Protones

Simulador basado en **Geant4** de un sistema de tomografía con protones (*proton CT*). Un haz de protones atraviesa uno o varios *phantoms* (cilindros de tejido) y es registrado por detectores de fibras situados antes y después del objeto. Las señales (hits) se guardan en un fichero ROOT, y unos scripts en Python reconstruyen las trazas y estiman el punto de interacción.

```
          gantry (cono de acero)
                 │  haz de protones (z = +125 cm)
                 ▼
     ┌──────────────────────┐  Detector 0 (z = +70 cm)
     │  4 capas de fibras    │  capas alternadas 0° / 90° → medida X e Y
     └──────────────────────┘
                 │
              ( phantom )       cilindro de material biológico (lung, bone…)
                 │
     ┌──────────────────────┐  Detector 1 (z = −70 cm)
     │  4 capas de fibras    │
     └──────────────────────┘
```

## Estructura del repositorio

```
.
├── setup.sh                         # Variables de entorno (Geant4, jsoncpp, ROOT) por máquina
└── ProtonTomographySimulator/
    ├── CMakeLists.txt               # Compilación del ejecutable `Generator`
    ├── Generator.cc                 # main(): opciones de línea de comandos y run manager
    ├── include/, src/               # Código C++ de la simulación
    │   ├── ConfigurationGeometry    # Lee el JSON de configuración
    │   ├── DetectorConstruction     # Mundo, materiales y volúmenes
    │   ├── Detector / Layer / Fiber # Jerarquía detector → capa → fibra
    │   ├── FiberSensor(Hit)         # Detector sensible y hits
    │   ├── Phantom                  # Objeto a "fotografiar" (cilindro)
    │   ├── Gantry                   # Gantry/cono de salida del haz
    │   ├── Beam, PrimaryGeneratorAction  # Generación del haz de protones
    │   ├── ModularPhysicsList       # Lista de física
    │   ├── RunAction / EventAction  # Escritura del ntuple de salida
    │   └── *Messenger, RNGWrapper   # Comandos UI y generador aleatorio
    ├── vis.mac, init_vis.mac        # Macros de visualización (modo interactivo)
    ├── data/
    │   ├── confExample.json         # Plantilla de configuración
    │   └── makeConfiguration.py     # Genera una configuración completa a partir de la plantilla
    ├── test/                        # Generadores de configuración alternativos
    └── dataAnalysis/                # Análisis en Python (PyROOT)
        ├── trackReconstruction*.py  # Reconstrucción de trazas
        ├── makePOCA.py              # Estimación POCA (Point Of Closest Approach)
        ├── BackFilteredPropagation.py
        ├── makeHLTuple.py, basicPlots.py, analysis.py
        └── tools/                   # Track, TrackFinder, POCAEstimator, Voxel, …
```

## Requisitos

- **Geant4** 11.x (probado con 11.1.2 y 11.3.2), compilado con soporte de UI/Vis (Qt/OpenGL) si se quiere visualización.
- **jsoncpp** (se enlaza estáticamente desde `$JSONCPPDIR/lib/libjsoncpp.a`).
- **CMake** ≥ 3.5 y un compilador C++ compatible con tu Geant4.
- **ROOT** 6 con PyROOT, y **Python 3** con `numpy`, para el análisis.

## Configuración del entorno

`setup.sh` define, según el `$HOSTNAME`, estas variables:

| Variable       | Significado                                   |
|----------------|-----------------------------------------------|
| `G4INSTALLDIR` | Instalación de Geant4 (se hace `source geant4.sh`) |
| `G4WORKDIR`    | Directorio de trabajo del proyecto            |
| `JSONCPPDIR`   | Instalación de jsoncpp (`include/`, `lib/`)   |
| `PYTHONPATH`   | Ruta para los módulos de análisis             |

Si tu máquina no aparece, añade un bloque nuevo con tus rutas (o exporta las variables a mano) y después:

```bash
source setup.sh
```

## Compilación

```bash
cd ProtonTomographySimulator
mkdir build && cd build
cmake ..            # -DWITH_GEANT4_UIVIS=OFF para compilar solo en modo batch
make -j$(nproc)
```

Se genera el ejecutable `Generator`.

## Uso

### 1. Crear la configuración de geometría

La geometría y el haz se describen en un JSON. Lo más sencillo es generarlo a partir de la plantilla:

```bash
cd ProtonTomographySimulator/data
python3 makeConfiguration.py -i confExample.json -o conf.json
```

Esto produce un mundo de 300 cm³, un haz de protones de 250 MeV en z = 125 cm, un phantom de pulmón en el origen y **dos detectores** (z = ±70 cm) con **4 capas** cada uno (orientadas 0°/90°/0°/90°) de **21 fibras**. Edita el script para cambiar la configuración.

### 2. Ejecutar la simulación

Modo batch:

```bash
./Generator --input ../data/conf.json --output salida.root --number 10000 --seed 1234
```

Modo interactivo con visualización (ejecuta `init_vis.mac`, que debe estar en el directorio de ejecución):

```bash
cp ../vis.mac ../init_vis.mac .
./Generator --input ../data/conf.json --output salida.root --number 1 --geant vis
```

| Opción      | Descripción                                               |
|-------------|-----------------------------------------------------------|
| `--input`   | Fichero JSON de geometría/haz                             |
| `--output`  | Fichero de salida (ROOT)                                  |
| `--number`  | Número de eventos (> 0)                                   |
| `--seed`    | Semilla del generador aleatorio                           |
| `--geant`   | Si se indica (cualquier valor), abre la sesión interactiva |
| `--pt`      | Aceptado por la línea de comandos (actualmente sin efecto) |

### 3. Analizar los resultados

La cadena de análisis prevista es: ntuple `hits` → `makeHLTuple.py` (agrupa los hits por evento en el árbol `events`) → reconstrucción de trazas → POCA.

```bash
cd ProtonTomographySimulator/dataAnalysis
python3 makeHLTuple.py -i salida.root -c ../data/conf.json -o events.root
python3 trackReconstruction.py -i events.root -o tracks.root
python3 makePOCA.py -i tracks.root -o plots/
```

> ⚠️ Estos scripts vienen de la versión con sensores LGAD (usan variables como `lgad`, `xpad`, `toa`) y todavía no están adaptados a la geometría de fibras. Ver *Notas y limitaciones*.

## Formato del fichero de configuración

Todas las longitudes están en **cm**, los ángulos en **grados**, la energía en **MeV** y el tiempo en **ns**.

- **`theWorld`**: `xSizeWorld`, `ySizeWorld`, `zSizeWorld`.
- **`theBeam`**: posición (`x/y/zBeamPosition`), dispersión (`x/yBeamSigma`), orientación (`x/y/zDir`), `maxOpenAngle`, `nStep`, `nParticles` por evento, `energy`, `energySigma`, `energyDistribution` (`"Constant"` o `"Gauss"`), `tBeamSigma`.
- **`Phantoms`** (lista): `name`, `material`, posición `x/y/zPos`, rotación `x/y/zDir`, `radius`, `zsize` (cilindro).
- **`Detectors`** (lista): posición/rotación/tamaño (`*Detector`) y una lista de **`Layers`** (`*Layer`), cada una con una lista de **`Fibers`**: posición/rotación/tamaño (`*Sensor`), `coreRadius`, `claddingRadius`, `length`, `coreMaterial`, `claddingMaterial`.

Materiales disponibles (claves en minúsculas, de la base NIST de Geant4):

`air`, `iron`, `uranium`, `aluminium`, `carbon`, `argon`, `lead`, `silicon`, `steel`, `lung`, `bone`, `fat`, `brain`.

## Salida

El fichero ROOT contiene el ntuple **`hits`**, con una fila por hit con depósito de energía no nulo:

| Columna                     | Descripción                                    |
|-----------------------------|------------------------------------------------|
| `eventNumber`               | Número de evento                               |
| `det`, `layer`, `fiber`     | Identificadores del detector, capa y fibra     |
| `energy`                    | Energía depositada (MeV)                       |
| `localx/y/z`                | Posición local en la fibra (cm)                |
| `x`, `y`, `z`               | Posición global (cm)                           |
| `genID`, `genTrackID`       | Identificadores de la partícula generadora     |

## Física

`ModularPhysicsList` combina física electromagnética estándar y extra, desintegraciones (incluida radiactiva), dispersión elástica hadrónica de alta precisión, FTFP_BERT_HP, física de iones (Binary Cascade) y *stopping physics*.

## Notas y limitaciones conocidas

- El proyecto está en desarrollo. Parte de los scripts de `dataAnalysis/` provienen de una versión anterior basada en sensores LGAD y pueden necesitar adaptarse al ntuple actual (p. ej. `basicPlots.py` importa `tools/tdrstyle`, que no está en el repositorio).
- `confExample.json` usa `"Lead"` como material, pero las claves son en minúsculas (`"lead"`); usa `makeConfiguration.py` o corrígelo a mano.
- La plantilla usa la clave `nParticlesDistribution`, mientras que el código lee `particleDistribution` (`"Poisson"` o constante).
- Las macros de visualización se buscan en el directorio de ejecución.

## Créditos

Desarrollado en el **IFCA** (Instituto de Física de Cantabria).
