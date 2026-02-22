"""Utilidad de paginación para consultas SQLAlchemy."""

DEFAULT_PER_PAGE = 5


def paginate(query, page: int, per_page: int | None = None):
    """Helper de paginación genérico para SQLAlchemy queries.

    :param query: Query de SQLAlchemy a paginar.
    :param page: Número de página actual.
    :param per_page: Cantidad de elementos por página.
    :return: Tupla con lista de items y diccionario de paginación.
    """
    if not per_page:
        per_page = DEFAULT_PER_PAGE

    page = max(page, 1)

    total_items = query.count()
    total_pages = max((total_items + per_page - 1) // per_page, 1)

    offset_value = (page - 1) * per_page
    items = query.offset(offset_value).limit(per_page).all()

    pagination = {
        "page": page,
        "per_page": per_page,
        "total": total_items,
        "total_pages": total_pages,
        "has_prev": page > 1,
        "has_next": page < total_pages,
    }

    return items, pagination
