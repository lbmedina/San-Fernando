# Alerta de crecida: San Fernando, Tigre y Delta

La app lee sola la altura del río en San Fernando desde el Servicio de Hidrografía Naval (SHN)
y muestra avisos del SHN y novedades del INA. Un actualizador (GitHub Actions) corre cada 30 minutos.

## Puesta en marcha (unos 10 minutos)

1. Creá una cuenta en github.com si no tenés.
2. Creá un repositorio nuevo, **público** (así Pages es gratis), por ejemplo `alerta-crecidas`.
3. Subí todo el contenido de esta carpeta (botón «Add file» → «Upload files»).
   Incluí la carpeta oculta `.github`; si no se ve al arrastrar, creá el archivo
   `.github/workflows/actualizar.yml` a mano y pegá su contenido.
4. En el repositorio: **Settings → Pages → Build and deployment**: Source «Deploy from a branch»,
   Branch `main`, carpeta `/docs`. Guardá.
5. En **Settings → Actions → General → Workflow permissions**: elegí «Read and write permissions».
6. En la pestaña **Actions**, abrí «Actualizar datos oficiales» y tocá **Run workflow** para la primera carga.
7. Tu app queda en `https://TU-USUARIO.github.io/alerta-crecidas/`.

## Qué consulta
- SHN: alturas horarias (CSV) de San Fernando, Buenos Aires, La Plata y Martín García, y su RSS de avisos.
- INA: RSS del Alerta Hidrológico.
Si una fuente falla, la app muestra la última lectura buena con su hora y lo avisa. Si la lectura tiene
más de 3 horas de atraso, también lo avisa.

## Límites conocidos
- El pico previsto no se calcula: aparece en los avisos del SHN y se puede escribir a mano (opcional).
- Los umbrales de alerta (3,00 m) y evacuación (3,50 m) son los del INA para San Fernando; el de atención (2,50 m) es una propuesta propia.
- Los feeds RSS del SHN y del INA no pudieron verificarse desde el entorno donde se armó esto.
  Tras la primera ejecución, revisá `docs/datos.json`: si alguna fuente figura con `"ok": false`, pasame el error.
- Prefectura Naval bloquea el acceso automatizado a su sitio; no se usa sin su autorización.
- Herramienta orientativa: no reemplaza los avisos del SHN, del SMN ni de Defensa Civil.
