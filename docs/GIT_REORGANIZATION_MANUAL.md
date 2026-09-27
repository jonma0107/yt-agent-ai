# Manual de Reorganización de Ramas Git

Este documento detalla los pasos ejecutados para reemplazar la rama `main` antigua con el contenido de `feature/deploy` y limpiar las ramas obsoletas (`develop`).

## Objetivo
Reestructurar el repositorio para que `feature/deploy` se convierta en la nueva `main`, conservando un respaldo de la antigua `main` y eliminando `develop`.

## Resumen de Acciones Ejecutadas

### Fase 1: Respaldo de la antigua Main
Como no se puede borrar o renombrar la rama que está definida como "Default" en GitHub directamente sin antes cambiar esa configuración, primero aseguramos el respaldo.

1.  **Renombrado Local:**
    ```bash
    git branch -m main main-old
    ```
    *Esto cambió el nombre de tu rama local `main` a `main-old`.*

2.  **Subida del Respaldo:**
    ```bash
    git push -u origin main-old
    ```
    *Esto creó la rama `main-old` en GitHub con el historial antiguo.*

3.  **Cambio de Default Branch (Temporal):**
    ```bash
    gh repo edit --default-branch feature/deploy
    ```
    *Cambiamos la rama por defecto en GitHub a `feature/deploy` para desbloquear la eliminación de `main`.*

4.  **Eliminación de la Main antigua remota:**
    ```bash
    git push origin --delete main
    ```

### Fase 2: Promoción de Feature/Deploy a Main
Con la `main` antigua eliminada del remoto, procedimos a convertir tu rama de trabajo en la nueva principal.

1.  **Renombrado Local:**
    *(Estando ubicados en `feature/deploy`)*
    ```bash
    git branch -m main
    ```
    *Ahora tu rama local `feature/deploy` se llama `main`.*

2.  **Subida de la Nueva Main:**
    ```bash
    git push -u origin main
    ```
    *Se subió el contenido actual como la nueva rama `main` en GitHub.*

3.  **Restauración de Default Branch:**
    ```bash
    gh repo edit --default-branch main
    ```
    *Configuramos oficialmente la nueva `main` como la rama por defecto del repositorio.*

### Fase 3: Limpieza
Eliminación de ramas que ya no son necesarias o que quedaron huérfanas tras el renombrado.

1.  **Eliminación de referencias antiguas:**
    ```bash
    git push origin --delete feature/deploy
    ```
    *Borramos la referencia remota `feature/deploy` ya que ahora su contenido vive en `main`.*

2.  **Eliminación de Develop:**
    ```bash
    git branch -D develop
    git push origin --delete develop
    ```
    *Eliminamos la rama `develop` tanto de tu máquina local como de GitHub.*

## Estado Final del Repositorio

| Rama | Descripción | Estado |
|------|-------------|--------|
| **main** | Nueva rama principal (tiene el contenido de `feature/deploy`) | **Activa / Default** |
| **main-old** | Respaldo del historial antiguo | **Respaldo** |
| feature/deploy | Rama de trabajo anterior | *Eliminada* |
| develop | Rama de desarrollo anterior | *Eliminada* |
