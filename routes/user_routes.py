"""
Rutas de usuarios - Endpoints HTTP.

Este módulo define los endpoints REST para operaciones de usuarios,
delegando la lógica al controlador correspondiente.
"""

from typing import List

from fastapi import APIRouter, Depends

from models.user import UserCreate, UserResponse, UserUpdate
from controllers.user_controller import UserController
from services.user_service import UserService

# Instancias singleton del servicio y controlador
_user_service = UserService()
_user_controller = UserController(_user_service)

router = APIRouter(prefix="/users", tags=["users"])


def get_controller() -> UserController:
    """
    Dependency para obtener el controlador.

    Returns:
        Instancia de UserController.
    """
    return _user_controller


@router.get("/", response_model=List[UserResponse])
async def get_users(
    controller: UserController = Depends(get_controller),
) -> List[UserResponse]:
    """
    Obtiene todos los usuarios.

    Returns:
        Lista de usuarios.
    """
    return controller.get_all_users()


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int, controller: UserController = Depends(get_controller)
) -> UserResponse:
    """
    Obtiene un usuario por ID.

    Args:
        user_id: ID del usuario.

    Returns:
        Usuario encontrado.
    """
    return controller.get_user_by_id(user_id)


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(
    user_data: UserCreate, controller: UserController = Depends(get_controller)
) -> UserResponse:
    """
    Crea un nuevo usuario.

    Args:
        user_data: Datos del usuario a crear.

    Returns:
        Usuario creado.
    """
    return controller.create_user(user_data)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    controller: UserController = Depends(get_controller),
) -> UserResponse:
    """
    Actualiza un usuario existente.

    Args:
        user_id: ID del usuario a actualizar.
        user_data: Datos a actualizar.

    Returns:
        Usuario actualizado.
    """
    return controller.update_user(user_id, user_data)


@router.delete("/{user_id}")
async def delete_user(
    user_id: int, controller: UserController = Depends(get_controller)
) -> dict:
    """
    Elimina un usuario.

    Args:
        user_id: ID del usuario a eliminar.

    Returns:
        Confirmación de eliminación.
    """
    return controller.delete_user(user_id)
