from data.database import get_connection

def create_checkin(
    adopcion_id,
    fecha,
    bienestar,
    comportamiento,
    notas
):
    """
    Guarda check-in.

    Returns:
        None
    """
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
        INSERT INTO checkins (
            adopcion_id,
            fecha,
            bienestar,
            comportamiento,
            notas
        )
        VALUES (?, ?, ?, ?, ?)
        """, (
            adopcion_id,
            fecha,
            bienestar,
            comportamiento,
            notas
        ))

        connection.commit()

    except Exception as error:
        raise RuntimeError(
            f"Error guardando check-in: {error}"
        )

def get_checkins_by_adoption(adoption_id):
    """
    Obtiene historial.

    Returns:
        list
    """
    connection = get_connection()
    cursor = connection.cursor()

    try:
        rows = cursor.execute("""
        SELECT fecha, bienestar, comportamiento, notas
        FROM checkins
        WHERE adopcion_id = ?
        ORDER BY id DESC
        """, (adoption_id,)).fetchall()

        return rows

    except Exception as error:
        raise RuntimeError(
            f"Error leyendo historial: {error}"
        )

def get_risk_cases(threshold):
    """
    Obtiene alertas.

    Returns:
        list
    """
    connection = get_connection()
    cursor = connection.cursor()

    try:
        rows = cursor.execute("""
        SELECT
            adopciones.familia,
            adopciones.mascota,
            checkins.bienestar,
            checkins.comportamiento,
            checkins.notas
        FROM checkins
        JOIN adopciones
        ON adopciones.id = checkins.adopcion_id
        WHERE checkins.bienestar <= ?
        ORDER BY checkins.id DESC
        """, (threshold,)).fetchall()

        return rows

    except Exception as error:
        raise RuntimeError(
            f"Error leyendo alertas: {error}"
        )
